from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_renders_with_product_name(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")
        self.assertContains(response, "جزوه‌ساز")
        self.assertContains(response, 'dir="rtl"')
        self.assertContains(response, "css/vendor/bootstrap.rtl.min.css")
        self.assertNotContains(response, "cdn.")
