import re

from django.test import TestCase
from django.urls import resolve, reverse

HEX_COLOR = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")


class RootUrlTests(TestCase):
    def test_root_is_served_by_books_dashboard(self):
        self.assertEqual(resolve("/").view_name, "books:list")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "جزوه‌ساز")
        self.assertContains(response, 'dir="rtl"')
        self.assertContains(response, "css/vendor/bootstrap.rtl.min.css")
        self.assertNotContains(response, "cdn.")


class DesignSystemPageTests(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse("core:design_system"))
        self.html = self.response.content.decode()

    def test_page_renders(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "core/design-system.html")
        self.assertContains(self.response, "سیستم طراحی")
        self.assertContains(self.response, "brand/aleflogo.png")
        self.assertContains(self.response, "js/app.js")

    def test_no_cdn_links(self):
        self.assertNotRegex(self.html, r"https?://(cdn|fonts|unpkg|jsdelivr)")

    def test_no_hard_coded_hex_colors(self):
        self.assertEqual(HEX_COLOR.findall(self.html), [])

    def test_shared_components_are_used(self):
        for marker in ["alert-success", "invalid-feedback", "pagination", "modal", "breadcrumb"]:
            self.assertIn(marker, self.html)

    def test_pagination_follows_page_param(self):
        response = self.client.get(reverse("core:design_system"), {"page": 2})
        self.assertContains(response, "صفحه‌ی 2 از 5")
