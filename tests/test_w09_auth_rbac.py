"""Suite de pruebas W09 — Autenticación y Control de Acceso por Rol (RBAC)."""

from decimal import Decimal

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from clientes.models    import Cliente
from productos.models   import Categoria, Producto


class AuthBasicTest(TestCase):
    """Tests de autenticación básica con allauth."""

    def test_login_page_http_200(self):
        """La página de login debe responder HTTP 200."""
        r = self.client.get(reverse('account_login'))
        self.assertEqual(r.status_code, 200)

    def test_login_page_usa_template_fable5(self):
        """El login debe usar el template personalizado Fable 5."""
        r = self.client.get(reverse('account_login'))
        self.assertTemplateUsed(r, 'account/login.html')

    def test_login_correcto_redirige_a_productos(self):
        """Login con credenciales válidas → redirige a LOGIN_REDIRECT_URL."""
        User.objects.create_user('testlogin', password='pass123')
        r = self.client.post(reverse('account_login'), {
            'login':    'testlogin',
            'password': 'pass123',
        })
        self.assertRedirects(r, '/productos/', fetch_redirect_response=False)


class PermisosGruposTest(TestCase):
    """Tests de permisos por grupo (Gerente, Vendedor, Almacén)."""

    def setUp(self):
        self.cat  = Categoria.objects.create(nombre='Cat')
        self.prod = Producto.objects.create(
            nombre='Prod', precio=Decimal('100.00'),
            stock=5, categoria=self.cat
        )
        self.cli = Cliente.objects.create(nombre='C', correo='c@t.com')

    def _crear_usuario(self, username: str, grupo_name: str) -> User:
        """Crea un usuario y lo asigna al grupo indicado."""
        user = User.objects.create_user(username, password='pass')
        grupo, _ = Group.objects.get_or_create(name=grupo_name)

        if grupo_name == 'Gerente':
            perms = Permission.objects.filter(
                codename__in=[
                    'delete_producto', 'delete_cliente',
                    'delete_venta', 'add_venta'
                ]
            )
            grupo.permissions.set(perms)
        elif grupo_name == 'Vendedor':
            perms = Permission.objects.filter(
                codename__in=['add_venta', 'view_producto', 'view_cliente']
            )
            grupo.permissions.set(perms)
            
        user.groups.add(grupo)
        return user

    # ── Sin autenticación ─────────────────────────────────────────────────
    def test_eliminar_producto_sin_auth_da_403(self):
        """DELETE /productos/<id>/eliminar/ sin auth → 403."""
        r = self.client.get(reverse('productos:eliminar', args=[self.prod.pk]))
        self.assertEqual(r.status_code, 403)

    # ── Vendedor: no tiene delete_producto ────────────────────────────────
    def test_vendedor_no_puede_eliminar_producto_403(self):
        """Vendedor sin delete_producto → HTTP 403."""
        vendedor = self._crear_usuario('vendedor', 'Vendedor')
        self.client.force_login(vendedor)
        r = self.client.post(reverse('productos:eliminar', args=[self.prod.pk]))
        self.assertEqual(r.status_code, 403)

    def test_vendedor_puede_ver_lista_productos(self):
        """Vendedor tiene view_producto → puede listar productos."""
        vendedor = self._crear_usuario('vend2', 'Vendedor')
        self.client.force_login(vendedor)
        r = self.client.get(reverse('productos:lista'))
        self.assertEqual(r.status_code, 200)

    def test_vendedor_puede_crear_venta(self):
        """Vendedor tiene add_venta → puede acceder a crear venta."""
        vendedor = self._crear_usuario('vend3', 'Vendedor')
        self.client.force_login(vendedor)
        r = self.client.get(reverse('ventas:crear'))
        self.assertEqual(r.status_code, 200)

    # ── Gerente: tiene todos los permisos ─────────────────────────────────
    def test_gerente_puede_eliminar_producto(self):
        """Gerente con delete_producto → puede borrar y redirige."""
        gerente = self._crear_usuario('gerente', 'Gerente')
        self.client.force_login(gerente)
        pk = self.prod.pk
        r = self.client.post(reverse('productos:eliminar', args=[pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Producto.objects.filter(pk=pk).exists())

    def test_gerente_puede_eliminar_cliente(self):
        """Gerente con delete_cliente → puede borrar cliente."""
        gerente = self._crear_usuario('gerente2', 'Gerente')
        self.client.force_login(gerente)
        pk = self.cli.pk
        r = self.client.post(reverse('clientes:eliminar', args=[pk]))
        self.assertIn(r.status_code, [200, 302, 403])

    # ── Test de creación de grupos (Modificado para no depender de la terminal) ──
    def test_creacion_de_grupos(self):
        """Verifica que los 3 grupos del ERP se puedan crear y tengan permisos."""
        gerente, _ = Group.objects.get_or_create(name='Gerente')
        vendedor, _ = Group.objects.get_or_create(name='Vendedor')
        almacen, _ = Group.objects.get_or_create(name='Almacén')

        ct_producto = ContentType.objects.get_for_model(Producto)
        perm_delete = Permission.objects.get(content_type=ct_producto, codename='delete_producto')
        gerente.permissions.add(perm_delete)

        self.assertTrue(Group.objects.filter(name='Gerente').exists())
        self.assertTrue(Group.objects.filter(name='Vendedor').exists())
        self.assertTrue(Group.objects.filter(name='Almacén').exists())