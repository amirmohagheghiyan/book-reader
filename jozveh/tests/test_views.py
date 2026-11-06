from django.test import TestCase
from django.urls import reverse

from jozveh.models import Block

from .helpers import VALID_DATA, add_text, make_book, texts


class EditorViewTests(TestCase):
    def setUp(self):
        self.book = make_book()
        self.url = reverse("jozveh:editor", args=[self.book.pk])

    def test_unknown_book_is_404(self):
        for name in ("editor", "print", "pick"):
            with self.subTest(name=name):
                response = self.client.get(reverse(f"jozveh:{name}", args=[9999]))
                self.assertEqual(response.status_code, 404)

    def test_empty_state(self):
        response = self.client.get(self.url)
        self.assertContains(response, "این جزوه هنوز بلوکی ندارد")
        self.assertContains(response, reverse("jozveh:pick", args=[self.book.pk]))
        self.assertContains(response, "جزوه‌ی «حقوق مدنی»")
        self.assertContains(response, reverse("books:list"))

    def test_blocks_in_position_order(self):
        a, b, c = (add_text(self.book, t) for t in ("الف-اول", "ب-دوم", "ج-سوم"))
        b.move("up")
        body = self.client.get(self.url).content.decode()
        self.assertLess(body.index("ب-دوم"), body.index("الف-اول"))
        self.assertLess(body.index("الف-اول"), body.index("ج-سوم"))


class CreateViewTests(TestCase):
    def setUp(self):
        self.book = make_book()
        self.add_url = reverse("jozveh:add", args=[self.book.pk, "text"])

    def test_pick_page_lists_six_kinds_and_keeps_after(self):
        response = self.client.get(reverse("jozveh:pick", args=[self.book.pk]) + "?after=7")
        for value, label in Block.Kind.choices:
            self.assertContains(response, label)
            self.assertContains(response, reverse("jozveh:add", args=[self.book.pk, value]) + "?after=7")

    def test_pick_page_drops_non_numeric_after(self):
        response = self.client.get(reverse("jozveh:pick", args=[self.book.pk]) + "?after=x")
        self.assertNotContains(response, "?after=")

    def test_unknown_kind_is_404(self):
        response = self.client.get(reverse("jozveh:add", args=[self.book.pk, "image"]))
        self.assertEqual(response.status_code, 404)

    def test_append_redirects_to_block_with_message(self):
        add_text(self.book, "الف")
        response = self.client.post(self.add_url, {"text": "ب"}, follow=True)
        block = self.book.blocks.last()
        self.assertEqual(response.redirect_chain[0][0], f"/books/{self.book.pk}/jozveh/#block-{block.pk}")
        self.assertContains(response, "بلوک «متن» اضافه شد.")
        self.assertEqual(texts(self.book), ["الف", "ب"])

    def test_insert_after_middle_block(self):
        a, b, c = (add_text(self.book, t) for t in ("الف", "ب", "ج"))
        url = reverse("jozveh:add", args=[self.book.pk, "note"]) + f"?after={b.pk}"
        self.client.post(url, {"text": "نکته"})
        self.assertEqual([x.data["text"] for x in self.book.blocks.all()], ["الف", "ب", "نکته", "ج"])

    def test_stale_or_foreign_after_appends(self):
        a = add_text(self.book, "الف")
        foreign = add_text(make_book(title="دیگر"), "x")
        for after in (9999, foreign.pk):
            self.client.post(f"{self.add_url}?after={after}", {"text": f"ب{after}"})
        self.assertEqual(texts(self.book), ["الف", "ب9999", f"ب{foreign.pk}"])

    def test_form_keeps_after_in_post_url_and_shows_cancel(self):
        response = self.client.get(self.add_url + "?after=3")
        self.assertContains(response, '<form method="post" novalidate>')
        self.assertContains(response, "انصراف")
        self.assertContains(response, reverse("jozveh:pick", args=[self.book.pk]) + "?after=3")

    def test_invalid_form_rerenders_without_saving(self):
        response = self.client.post(self.add_url, {"text": "  "})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "is-invalid")
        self.assertEqual(Block.objects.count(), 0)

    def test_every_kind_can_be_added(self):
        fields = {
            "heading": {"text": "فصل"},
            "text": {"text": "متن"},
            "note": {"text": "نکته"},
            "steps": {"items": "الف\nب"},
            "table": {"rows": "الف | ب\n۱ | ۲"},
            "concept_map": {"center": "م", "branches": "شاخه: الف"},
        }
        for kind, data in fields.items():
            self.client.post(reverse("jozveh:add", args=[self.book.pk, kind]), data)
        self.assertEqual([b.kind for b in self.book.blocks.all()], list(fields))


class UpdateViewTests(TestCase):
    def setUp(self):
        self.book = make_book()
        self.table = Block.append(self.book, Block.Kind.TABLE, VALID_DATA[Block.Kind.TABLE])
        self.url = reverse("jozveh:edit", args=[self.book.pk, self.table.pk])

    def test_form_prefilled_and_row_added(self):
        add_text(self.book, "بعدی")
        response = self.client.get(self.url)
        self.assertContains(response, "اصطلاح | تعریف\nاهلیت | توانایی داشتن حق")
        rows = response.context["form"].initial["rows"] + "\nحجر | ممنوعیت قانونی"
        response = self.client.post(self.url, {"rows": rows}, follow=True)
        self.assertContains(response, "بلوک «جدول» ذخیره شد.")
        self.table.refresh_from_db()
        self.assertEqual(len(self.table.data["rows"]), 3)
        self.assertEqual((self.table.position, self.table.kind), (1, "table"))

    def test_invalid_edit_keeps_data(self):
        response = self.client.post(self.url, {"rows": ""})
        self.assertEqual(response.status_code, 200)
        self.table.refresh_from_db()
        self.assertEqual(self.table.data, VALID_DATA[Block.Kind.TABLE])

    def test_block_of_another_book_is_404(self):
        other = make_book(title="دیگر")
        for name in ("edit", "delete"):
            response = self.client.get(reverse(f"jozveh:{name}", args=[other.pk, self.table.pk]))
            self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse("jozveh:move", args=[other.pk, self.table.pk]), {"direction": "up"})
        self.assertEqual(response.status_code, 404)


class MoveAndDeleteViewTests(TestCase):
    def setUp(self):
        self.book = make_book()
        self.a, self.b, self.c = (add_text(self.book, t) for t in ("الف", "ب", "ج"))

    def move(self, block, direction):
        return self.client.post(reverse("jozveh:move", args=[self.book.pk, block.pk]), {"direction": direction})

    def test_up_and_down(self):
        response = self.move(self.c, "up")
        self.assertRedirects(response, f"/books/{self.book.pk}/jozveh/#block-{self.c.pk}", fetch_redirect_response=False)
        self.assertEqual(texts(self.book), ["الف", "ج", "ب"])
        self.move(self.c, "down")
        self.assertEqual(texts(self.book), ["الف", "ب", "ج"])

    def test_ends_unchanged_and_no_message(self):
        self.move(self.a, "up")
        response = self.move(self.c, "down")
        self.assertEqual(texts(self.book), ["الف", "ب", "ج"])
        response = self.client.get(response.url)
        self.assertNotContains(response, 'role="status"')

    def test_get_is_405_and_bad_direction_is_400(self):
        url = reverse("jozveh:move", args=[self.book.pk, self.a.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.move(self.a, "left").status_code, 400)

    def test_disabled_buttons_at_ends(self):
        body = self.client.get(reverse("jozveh:editor", args=[self.book.pk])).content.decode()
        self.assertIn('aria-label="بالا بردن «متن: الف»" disabled', body)
        self.assertIn('aria-label="پایین بردن «متن: ج»" disabled', body)
        self.assertNotIn('aria-label="بالا بردن «متن: ب»" disabled', body)
        self.assertEqual(body.count(" disabled>"), 2)
        self.assertIn(f'id="delete-block-{self.b.pk}"', body)

    def test_delete_confirm_page_and_middle_delete(self):
        url = reverse("jozveh:delete", args=[self.book.pk, self.b.pk])
        self.assertContains(self.client.get(url), "«متن: ب» حذف شود؟")
        response = self.client.post(url, follow=True)
        self.assertContains(response, "بلوک حذف شد.")
        self.assertEqual(texts(self.book), ["الف", "ج"])

    def test_delete_last_block_shows_empty_state(self):
        for block in (self.a, self.b, self.c):
            response = self.client.post(reverse("jozveh:delete", args=[self.book.pk, block.pk]), follow=True)
        self.assertContains(response, "این جزوه هنوز بلوکی ندارد")
