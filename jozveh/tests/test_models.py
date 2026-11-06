from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from jozveh.models import Block

from .helpers import VALID_DATA, add_text, make_book, texts

INVALID_DATA = {
    Block.Kind.HEADING: {"text": "  "},
    Block.Kind.TEXT: {},
    Block.Kind.NOTE: {"text": 3},
    Block.Kind.STEPS: {"items": []},
    Block.Kind.TABLE: {"header": ["الف", "ب"], "rows": [["۱"]]},
    Block.Kind.CONCEPT_MAP: {"center": "مرکز", "branches": []},
}


class BlockShapeTests(TestCase):
    def setUp(self):
        self.book = make_book()

    def test_valid_shape_of_every_kind(self):
        for kind, data in VALID_DATA.items():
            with self.subTest(kind=kind):
                Block(book=self.book, kind=kind, data=data, position=1).full_clean()

    def test_invalid_shape_of_every_kind(self):
        for kind, data in INVALID_DATA.items():
            with self.subTest(kind=kind), self.assertRaises(ValidationError):
                Block(book=self.book, kind=kind, data=data, position=1).full_clean()

    def test_summary_and_template(self):
        block = Block(book=self.book, kind=Block.Kind.TEXT, data={"text": "الف " * 30})
        self.assertTrue(block.summary.startswith("متن: الف"))
        self.assertTrue(block.summary.endswith("…"))
        self.assertLessEqual(len(block.summary), len("متن: ") + 41)
        self.assertEqual(block.template_name, "jozveh/blocks/text.html")
        table = Block(kind=Block.Kind.TABLE, data=VALID_DATA[Block.Kind.TABLE])
        self.assertEqual(str(table), "جدول: اصطلاح، تعریف")
        steps = Block(kind=Block.Kind.STEPS, data=VALID_DATA[Block.Kind.STEPS])
        self.assertEqual(steps.summary, "مراحل: طرح دعوا")


class BlockOrderingTests(TestCase):
    def setUp(self):
        self.book = make_book()

    def test_append_to_empty_and_non_empty(self):
        first = add_text(self.book, "الف")
        second = add_text(self.book, "ب")
        self.assertEqual((first.position, second.position), (1, 2))
        self.assertEqual(texts(self.book), ["الف", "ب"])

    def test_append_is_per_book(self):
        add_text(make_book(title="دیگر"), "x")
        self.assertEqual(add_text(self.book, "الف").position, 1)

    def test_insert_after_first_middle_and_last(self):
        a, b, c = (add_text(self.book, t) for t in ("الف", "ب", "ج"))
        Block.insert_after(a, Block.Kind.TEXT, {"text": "۱"})
        b.refresh_from_db()
        Block.insert_after(b, Block.Kind.TEXT, {"text": "۲"})
        c.refresh_from_db()
        Block.insert_after(c, Block.Kind.TEXT, {"text": "۳"})
        self.assertEqual(texts(self.book), ["الف", "۱", "ب", "۲", "ج", "۳"])

    def test_move_up_and_down_in_middle(self):
        a, b, c = (add_text(self.book, t) for t in ("الف", "ب", "ج"))
        self.assertTrue(c.move("up"))
        self.assertEqual(texts(self.book), ["الف", "ج", "ب"])
        a.refresh_from_db()
        self.assertTrue(a.move("down"))
        self.assertEqual(texts(self.book), ["ج", "الف", "ب"])

    def test_move_at_ends_changes_nothing(self):
        a, b = add_text(self.book, "الف"), add_text(self.book, "ب")
        self.assertFalse(a.move("up"))
        self.assertFalse(b.move("down"))
        self.assertEqual(texts(self.book), ["الف", "ب"])

    def test_unknown_direction(self):
        with self.assertRaises(ValueError):
            add_text(self.book, "الف").move("left")

    def test_order_after_delete_with_gaps(self):
        a, b, c = (add_text(self.book, t) for t in ("الف", "ب", "ج"))
        b.delete()
        self.assertTrue(c.move("up"))
        self.assertEqual(texts(self.book), ["ج", "الف"])
        self.assertEqual(add_text(self.book, "د").position, 4)

    def test_move_repairs_duplicate_positions(self):
        a, b = add_text(self.book, "الف"), add_text(self.book, "ب")
        Block.objects.filter(pk=b.pk).update(position=a.position)
        b.refresh_from_db()
        self.assertTrue(b.move("up"))
        self.assertEqual(texts(self.book), ["ب", "الف"])

    def test_cascade_delete_with_book(self):
        add_text(self.book, "الف")
        self.book.delete()
        self.assertEqual(Block.objects.count(), 0)


class BlockAdminTests(TestCase):
    def test_admin_changelist_renders(self):
        user = get_user_model().objects.create_superuser("admin", "a@example.com", "pass")
        self.client.force_login(user)
        add_text(make_book(), "الف")
        response = self.client.get("/admin/jozveh/block/")
        self.assertContains(response, "متن: الف")
