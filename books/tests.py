from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import resolve, reverse

from .forms import BookForm
from .jalali import gregorian_to_jalali, today_jalali
from .models import Book, Month, Status


def make_book(**kwargs):
    data = {"title": "حقوق مدنی", "author": "ناصر کاتوزیان", "year": 1404, "month": Month.MEHR}
    data.update(kwargs)
    return Book.objects.create(**data)


class BookModelTests(TestCase):
    def test_ordering_newest_period_first_then_title(self):
        make_book(title="ب", year=1404, month=7)
        make_book(title="الف", year=1404, month=8)
        make_book(title="آ", year=1404, month=8)
        self.assertEqual([b.title for b in Book.objects.all()], ["آ", "الف", "ب"])

    def test_labels_and_badge(self):
        book = make_book(year=1404, month=Month.ABAN, status=Status.DONE)
        self.assertEqual(book.period_label, "آبان 1404")
        self.assertEqual(book.status_badge_class, "success")
        self.assertEqual(str(book), "حقوق مدنی")

    def test_validators(self):
        with self.assertRaises(ValidationError):
            Book(title="x", year=1200, month=1).full_clean()
        with self.assertRaises(ValidationError):
            Book(title="x", year=1404, month=1, pages=0).full_clean()
        Book(title="x", year=1404, month=1, pages=1).full_clean()


class JalaliTests(TestCase):
    def test_known_dates(self):
        self.assertEqual(gregorian_to_jalali(2026, 3, 21), (1405, 1, 1))
        self.assertEqual(gregorian_to_jalali(2026, 11, 6), (1405, 8, 15))
        self.assertEqual(gregorian_to_jalali(2025, 3, 20), (1403, 12, 30))


class BookFormTests(TestCase):
    def test_valid_and_invalid(self):
        self.assertTrue(BookForm(data={"title": "x", "year": 1404, "month": 8, "status": "queued"}).is_valid())
        form = BookForm(data={"title": "", "year": 1200, "month": 8, "status": "queued", "pages": 0})
        self.assertFalse(form.is_valid())
        self.assertIn("این فیلد لازم است.", form.errors["title"])
        self.assertIn("سال باید بین ۱۳۰۰ تا ۱۵۰۰ باشد.", form.errors["year"])
        self.assertIn("تعداد صفحه باید دست‌کم ۱ باشد.", form.errors["pages"])


class BookListViewTests(TestCase):
    def test_root_url_is_dashboard(self):
        self.assertEqual(reverse("books:list"), "/")
        self.assertEqual(resolve("/").view_name, "books:list")

    def test_empty_library_state(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "books/book_list.html")
        self.assertContains(response, "هنوز کتابی ثبت نشده")
        self.assertNotContains(response, 'role="search"')
        self.assertNotContains(response, "cdn.")

    def test_grouping_order_and_rows(self):
        make_book(title="حقوق مدنی", year=1404, month=7, pages=510, status=Status.DONE)
        make_book(title="حقوق تجارت", author="ربیعا اسکینی", year=1404, month=8)
        response = self.client.get("/")
        html = response.content.decode()
        self.assertLess(html.index("آبان 1404"), html.index("مهر 1404"))
        self.assertContains(response, "ربیعا اسکینی")
        self.assertContains(response, "510")
        self.assertContains(response, "text-bg-success")
        self.assertContains(response, 'role="search"')

    def test_search_title_and_author(self):
        make_book(title="حقوق مدنی", author="ناصر کاتوزیان")
        make_book(title="آیین دادرسی", author="علی خالقی")
        response = self.client.get("/", {"q": "کاتوزیان"})
        self.assertContains(response, "حقوق مدنی")
        self.assertNotContains(response, "آیین دادرسی")
        self.assertContains(response, 'value="کاتوزیان"')
        response = self.client.get("/", {"q": "دادرسی"})
        self.assertContains(response, "آیین دادرسی")

    def test_status_filter_combined_with_search(self):
        make_book(title="حقوق مدنی", status=Status.READING)
        make_book(title="حقوق تجارت", status=Status.QUEUED)
        response = self.client.get("/", {"q": "حقوق", "status": "reading"})
        self.assertContains(response, "حقوق مدنی")
        self.assertNotContains(response, "حقوق تجارت")
        self.assertContains(response, 'value="reading" selected')
        self.assertContains(response, "پاک کردن جستجو")

    def test_no_results_state_differs_from_empty(self):
        make_book()
        response = self.client.get("/", {"q": "ناموجود"})
        self.assertContains(response, "کتابی با این مشخصات پیدا نشد")
        self.assertNotContains(response, "هنوز کتابی ثبت نشده")

    def test_invalid_status_is_ignored(self):
        make_book()
        response = self.client.get("/", {"status": "bogus"})
        self.assertContains(response, "حقوق مدنی")


class BookCreateUpdateDeleteTests(TestCase):
    def test_create_form_defaults_and_required_marks(self):
        response = self.client.get(reverse("books:create"))
        self.assertContains(response, "(الزامی)")
        year, month = today_jalali()
        self.assertContains(response, f'value="{year}"')
        self.assertContains(response, f'value="{month}" selected')
        self.assertContains(response, 'value="queued" selected')

    def test_create_valid_redirects_with_message(self):
        data = {"title": "حقوق تجارت", "author": "", "year": 1404, "month": 8, "status": "queued", "pages": ""}
        response = self.client.post(reverse("books:create"), data, follow=True)
        self.assertRedirects(response, "/")
        self.assertEqual(Book.objects.count(), 1)
        self.assertContains(response, "کتاب «حقوق تجارت» ذخیره شد.")

    def test_create_invalid_keeps_values_and_creates_nothing(self):
        data = {"title": "", "author": "علی خالقی", "year": 1200, "month": 8, "status": "queued", "pages": 0}
        response = self.client.post(reverse("books:create"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Book.objects.count(), 0)
        self.assertContains(response, "invalid-feedback")
        self.assertContains(response, 'value="علی خالقی"')

    def test_update_in_place(self):
        book = make_book(status=Status.READING)
        response = self.client.get(reverse("books:update", args=[book.pk]))
        self.assertContains(response, 'value="حقوق مدنی"')
        data = {"title": book.title, "author": book.author, "year": 1404, "month": 7, "status": "done", "pages": ""}
        response = self.client.post(reverse("books:update", args=[book.pk]), data, follow=True)
        book.refresh_from_db()
        self.assertEqual(book.status, Status.DONE)
        self.assertEqual(Book.objects.count(), 1)
        self.assertContains(response, "ذخیره شد")

    def test_update_invalid(self):
        book = make_book()
        data = {"title": "", "year": 1404, "month": 7, "status": "done"}
        self.client.post(reverse("books:update", args=[book.pk]), data)
        book.refresh_from_db()
        self.assertEqual(book.title, "حقوق مدنی")

    def test_delete_confirm_page_and_post(self):
        book = make_book()
        response = self.client.get(reverse("books:delete", args=[book.pk]))
        self.assertContains(response, "«حقوق مدنی» حذف شود؟")
        response = self.client.post(reverse("books:delete", args=[book.pk]), follow=True)
        self.assertRedirects(response, "/")
        self.assertEqual(Book.objects.count(), 0)
        self.assertContains(response, "کتاب «حقوق مدنی» حذف شد.")

    def test_list_has_confirm_modal_per_book(self):
        book = make_book()
        response = self.client.get("/")
        self.assertContains(response, f'id="delete-book-{book.pk}"')
        self.assertContains(response, reverse("books:delete", args=[book.pk]))
        self.assertContains(response, "این کار قابل بازگشت نیست.")

    def test_list_shows_file_count_and_files_link(self):
        from bookfiles.models import BookFile

        with_files = make_book(title="حقوق مدنی")
        without_files = make_book(title="حقوق تجارت")
        for i in range(2):
            BookFile.objects.create(book=with_files, file=f"books/{with_files.pk}/{i}.pdf", original_name=f"{i}.pdf", size=1)
        response = self.client.get("/")
        self.assertContains(response, reverse("bookfiles:list", args=[with_files.pk]))
        self.assertContains(response, reverse("bookfiles:list", args=[without_files.pk]))
        self.assertContains(response, 'text-bg-primary">2</span>')
        self.assertContains(response, 'text-bg-secondary">0</span>')
        self.assertContains(response, "این کار قابل بازگشت نیست و 2 فایل PDF این کتاب هم پاک می‌شود.")

    def test_delete_warning_with_and_without_files(self):
        from bookfiles.models import BookFile

        book = make_book()
        self.assertEqual(book.delete_warning, "این کار قابل بازگشت نیست.")
        for i in range(3):
            BookFile.objects.create(book=book, file=f"books/{book.pk}/{i}.pdf", original_name=f"{i}.pdf", size=1)
        self.assertEqual(book.delete_warning, "این کار قابل بازگشت نیست و 3 فایل PDF این کتاب هم پاک می‌شود.")
        response = self.client.get(reverse("books:delete", args=[book.pk]))
        self.assertContains(response, "3 فایل PDF این کتاب هم پاک می‌شود")
        response = self.client.get(reverse("books:update", args=[book.pk]))
        self.assertContains(response, "3 فایل PDF این کتاب هم پاک می‌شود")

    def test_list_shows_block_and_file_counts_without_multiplying(self):
        from bookfiles.models import BookFile
        from jozveh.models import Block

        with_both = make_book(title="حقوق مدنی")
        empty = make_book(title="حقوق تجارت")
        for i in range(2):
            BookFile.objects.create(book=with_both, file=f"books/{with_both.pk}/{i}.pdf", original_name=f"{i}.pdf", size=1)
        for i in range(5):
            Block.append(with_both, Block.Kind.TEXT, {"text": str(i)})
        response = self.client.get("/")
        listed = {b.title: b for b in response.context["books"]}
        self.assertEqual((listed["حقوق مدنی"].file_count, listed["حقوق مدنی"].block_count), (2, 5))
        self.assertEqual(listed["حقوق تجارت"].block_count, 0)
        self.assertContains(response, reverse("jozveh:editor", args=[with_both.pk]))
        self.assertContains(response, reverse("jozveh:editor", args=[empty.pk]))
        self.assertContains(response, 'جزوه <span class="badge rounded-pill text-bg-primary">5</span>')
        self.assertContains(response, 'جزوه <span class="badge rounded-pill text-bg-secondary">0</span>')

    def test_delete_warning_with_blocks_and_with_both(self):
        from bookfiles.models import BookFile
        from jozveh.models import Block

        book = make_book()
        for i in range(5):
            Block.append(book, Block.Kind.TEXT, {"text": str(i)})
        self.assertEqual(book.delete_warning, "این کار قابل بازگشت نیست و جزوه‌ی این کتاب (5 بلوک) هم پاک می‌شود.")
        for i in range(3):
            BookFile.objects.create(book=book, file=f"books/{book.pk}/{i}.pdf", original_name=f"{i}.pdf", size=1)
        self.assertEqual(
            book.delete_warning,
            "این کار قابل بازگشت نیست و 3 فایل PDF و جزوه‌ی این کتاب (5 بلوک) هم پاک می‌شود.",
        )
        response = self.client.get("/")
        self.assertContains(response, "3 فایل PDF و جزوه‌ی این کتاب (5 بلوک) هم پاک می‌شود.")

    def test_deleting_book_removes_its_blocks(self):
        from jozveh.models import Block

        book = make_book()
        Block.append(book, Block.Kind.TEXT, {"text": "الف"})
        self.client.post(reverse("books:delete", args=[book.pk]))
        self.assertEqual(Block.objects.count(), 0)
        self.assertEqual(self.client.get(reverse("jozveh:editor", args=[book.pk])).status_code, 404)

    def test_unknown_pk_is_404(self):
        self.assertEqual(self.client.get(reverse("books:update", args=[999])).status_code, 404)
        self.assertEqual(self.client.post(reverse("books:delete", args=[999])).status_code, 404)


class BookAdminTests(TestCase):
    def test_admin_changelist_renders(self):
        user = get_user_model().objects.create_superuser("admin", "a@example.com", "pass12345")
        self.client.force_login(user)
        make_book()
        response = self.client.get("/admin/books/book/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "حقوق مدنی")
