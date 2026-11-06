from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

from jozveh.models import Block

from .helpers import VALID_DATA, add_text, make_book


def render_block(kind, data=None):
    block = Block(kind=kind, data=data or VALID_DATA[kind])
    return render_to_string(block.template_name, {"block": block})


class BlockPartialTests(TestCase):
    def test_heading_text_and_note(self):
        self.assertIn("<h2", render_block(Block.Kind.HEADING))
        self.assertEqual(render_block(Block.Kind.TEXT).count("<p>"), 2)
        self.assertIn('class="jozveh-note"', render_block(Block.Kind.NOTE))

    def test_steps(self):
        html = render_block(Block.Kind.STEPS)
        self.assertIn('<ol class="jozveh-steps">', html)
        self.assertEqual(html.count("<li>"), 3)

    def test_table(self):
        html = render_block(Block.Kind.TABLE)
        self.assertEqual(html.count('<th scope="col">'), 2)
        self.assertEqual(html.count("<td>"), 4)
        self.assertIn("table-responsive", html)

    def test_concept_map(self):
        html = render_block(Block.Kind.CONCEPT_MAP)
        self.assertIn('<div class="jozveh-map-center">اشخاص</div>', html)
        self.assertEqual(html.count('class="jozveh-map-branch"'), 2)
        for word in ("حقیقی", "حقوقی", "اهلیت", "اقامتگاه", "ثبت", "تابعیت"):
            self.assertIn(word, html)

    def test_content_is_escaped(self):
        html = render_block(Block.Kind.TEXT, {"text": "<script>alert(1)</script>"})
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)


class PrintViewTests(TestCase):
    def setUp(self):
        self.book = make_book()
        self.url = reverse("jozveh:print", args=[self.book.pk])

    def test_print_page_has_no_site_chrome_and_all_blocks_in_order(self):
        add_text(self.book, "اولین-بلوک")
        Block.append(self.book, Block.Kind.STEPS, VALID_DATA[Block.Kind.STEPS])
        Block.append(self.book, Block.Kind.CONCEPT_MAP, VALID_DATA[Block.Kind.CONCEPT_MAP])
        body = self.client.get(self.url).content.decode()
        self.assertNotIn("navbar", body)
        self.assertNotIn("<footer", body)
        self.assertIn("<h1 class=\"mb-1\">حقوق مدنی</h1>", body)
        self.assertIn("ناصر کاتوزیان", body)
        self.assertIn("data-print", body)
        self.assertIn("d-print-none", body)
        self.assertIn(reverse("jozveh:editor", args=[self.book.pk]), body)
        self.assertLess(body.index("اولین-بلوک"), body.index("jozveh-steps"))
        self.assertLess(body.index("jozveh-steps"), body.index("jozveh-map-center"))
        self.assertNotIn("/edit/", body)
        self.assertNotIn("/move/", body)

    def test_empty_print_view(self):
        response = self.client.get(self.url)
        self.assertContains(response, "این جزوه هنوز بلوکی ندارد")
        self.assertNotContains(response, "data-print")

    def test_editor_links_to_print_view(self):
        add_text(self.book, "الف")
        response = self.client.get(reverse("jozveh:editor", args=[self.book.pk]))
        self.assertContains(response, self.url)
        self.assertContains(response, f"?after={self.book.blocks.first().pk}")
