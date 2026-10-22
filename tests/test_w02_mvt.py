"""Suite de pruebas W02 — Patrón MVT: templates, vistas y estáticos.

Actualizado en W07: se cambiaron las rutas de 'inicio' a 'lista'.
"""

from django.test import TestCase
from django.urls import reverse

class TemplatesRenderTest(TestCase):
    """Verifica que las vistas usan render() y los templates correctos."""

    def test_bienvenida_usa_template_correcto(self):
        """La vista de inicio debe renderizar bienvenida.html."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bienvenida.html')

    def test_bienvenida_extiende_base(self):
        """La página de inicio debe extender base.html."""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'base.html')

    def test_productos_usa_template_correcto(self):
        """La vista de productos debe usar productos/lista.html (W07)."""
        response = self.client.get(reverse('productos:lista')) # <-- Cambiado
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'productos/lista.html') # <-- Cambiado

    def test_clientes_usa_template_correcto(self):
        """La vista de clientes debe usar clientes/lista.html (W07)."""
        response = self.client.get(reverse('clientes:lista')) # <-- Cambiado
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/lista.html') # <-- Cambiado

    def test_proveedores_usa_template_correcto(self):
        """La vista de proveedores debe usar proveedores/lista.html (W07)."""
        response = self.client.get(reverse('proveedores:lista')) # <-- Cambiado
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proveedores/lista.html') # <-- Cambiado

    def test_ventas_usa_template_correcto(self):
        """La vista de ventas debe usar ventas/lista.html (W07)."""
        response = self.client.get(reverse('ventas:lista')) # <-- Cambiado
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ventas/lista.html') # <-- Cambiado

    def test_reportes_usa_template_correcto(self):
        """La vista de reportes debe usar reportes/index.html."""
        response = self.client.get(reverse('reportes:inicio')) # Este se queda igual
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reportes/index.html')


class ContextoBienvenidaTest(TestCase):
    """Verifica el contexto de la vista de bienvenida."""

    def test_contexto_contiene_modulos(self):
        response = self.client.get('/')
        self.assertIn('modulos', response.context, "El contexto debe incluir la lista 'modulos'")

    def test_contexto_tiene_seis_modulos(self):
        response = self.client.get('/')
        modulos = response.context.get('modulos', [])
        self.assertEqual(len(modulos), 6, f"Se esperaban 6 módulos, se encontraron {len(modulos)}")


class StaticFilesConfigTest(TestCase):
    """Verifica la configuración de archivos estáticos y WhiteNoise."""

    def test_static_url_es_slash_static(self):
        from django.conf import settings
        self.assertEqual(settings.STATIC_URL, '/static/')

    def test_static_root_configurado(self):
        from django.conf import settings
        self.assertTrue(bool(settings.STATIC_ROOT), "STATIC_ROOT no está configurado")

    def test_whitenoise_en_middleware(self):
        from django.conf import settings
        self.assertIn('whitenoise.middleware.WhiteNoiseMiddleware', settings.MIDDLEWARE)

    def test_whitenoise_despues_de_security(self):
        from django.conf import settings
        m = settings.MIDDLEWARE
        idx_sec  = m.index('django.middleware.security.SecurityMiddleware')
        idx_wn   = m.index('whitenoise.middleware.WhiteNoiseMiddleware')
        self.assertLess(idx_sec, idx_wn, "SecurityMiddleware debe ir ANTES que WhiteNoise")