import shutil
import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from books.models import Book

from .forms import BookFileUploadForm
from .models import BookFile
from .validators import validate_pdf

TEMP_MEDIA = tempfile.mkdtemp(prefix="bookfiles-test-")
PDF_BODY = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF\n"
PNG_BODY = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


def pdf(name="فصل-۱.pdf", body=PDF_BODY):
    return SimpleUploadedFile(name, body, content_type="application/pdf")


def make_book(**kwargs):
    data = {"title": "حقوق مدنی", "author": "ناصر کاتوزیان", "year": 1404, "month": 7}
    data.update(kwargs)
    return Book.objects.create(**data)


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class MediaTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def upload(self, book, *files, follow=False):
        url = reverse("bookfiles:list", args=[book.pk])
        return self.client.post(url, {"files": list(files)}, follow=follow)


class ValidatorTests(TestCase):
    def test_accepts_real_pdf(self):
        validate_pdf(pdf("a.pdf"))

    def test_rejects_other_extension(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_pdf(pdf("جزوه.docx"))
        self.assertIn("«جزوه.docx» فایل PDF نیست", ctx.exception.messages[0])

    def test_rejects_renamed_non_pdf(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_pdf(pdf("عکس.pdf", body=PNG_BODY))
        self.assertIn("«عکس.pdf» فایل PDF نیست", ctx.exception.messages[0])

    def test_file_is_rewound_after_check(self):
        upload = pdf("a.pdf")
        validate_pdf(upload)
        self.assertEqual(upload.read(5), b"%PDF-")


class UploadFormTests(MediaTestCase):
    def test_one_and_three_files(self):
        book = make_book()
        form = BookFileUploadForm(files={"files": [pdf("a.pdf")]})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save(book), 1)
        form = BookFileUploadForm(files={"files": [pdf("b.pdf"), pdf("c.pdf"), pdf("d.pdf")]})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save(book), 3)
        self.assertEqual(book.files.count(), 4)

    def test_no_file_is_required_error(self):
        form = BookFileUploadForm(data={}, files={})
        self.assertFalse(form.is_valid())
        self.assertIn("دست‌کم یک فایل PDF انتخاب کنید.", form.errors["files"])

    def test_one_bad_file_rejects_all(self):
        form = BookFileUploadForm(files={"files": [pdf("a.pdf"), pdf("b.pdf"), pdf("c.docx")]})
        self.assertFalse(form.is_valid())
        self.assertIn("«c.docx» فایل PDF نیست", form.errors["files"][0])
        self.assertEqual(BookFile.objects.count(), 0)


class BookFileModelTests(MediaTestCase):
    def test_str_ordering_and_path(self):
        book = make_book()
        first = BookFile.objects.create(book=book, file=pdf("x.pdf"), original_name="فصل-۱.pdf", size=5)
        second = BookFile.objects.create(book=book, file=pdf("y.pdf"), original_name="فصل-۲.pdf", size=5)
        self.assertEqual(str(first), "فصل-۱.pdf")
        self.assertEqual(list(book.files.all()), [first, second])
        self.assertEqual(BookFile(size=512).size_label, "512 بایت")
        self.assertEqual(BookFile(size=1536).size_label, "1٫5 کیلوبایت")
        self.assertEqual(BookFile(size=2_516_582).size_label, "2٫4 مگابایت")
        self.assertEqual(BookFile(size=3 * 1024**3).size_label, "3٫0 گیگابایت")
        self.assertTrue(first.file.name.startswith(f"books/{book.pk}/"))
        self.assertTrue(first.file.url.startswith("/media/"))

    def test_delete_removes_file_from_disk(self):
        book = make_book()
        record = BookFile.objects.create(book=book, file=pdf("x.pdf"), original_name="x.pdf", size=5)
        path = Path(record.file.path)
        self.assertTrue(path.exists())
        record.delete()
        self.assertFalse(path.exists())

    def test_book_delete_cascades_to_files_and_disk(self):
        book = make_book()
        paths = [
            Path(BookFile.objects.create(book=book, file=pdf(f"{i}.pdf"), original_name=f"{i}.pdf", size=5).file.path)
            for i in range(2)
        ]
        book.delete()
        self.assertEqual(BookFile.objects.count(), 0)
        for path in paths:
            self.assertFalse(path.exists())


class BookFileListViewTests(MediaTestCase):
    def test_unknown_book_is_404(self):
        self.assertEqual(self.client.get(reverse("bookfiles:list", args=[999])).status_code, 404)

    def test_empty_state_and_breadcrumb(self):
        book = make_book()
        response = self.client.get(reverse("bookfiles:list", args=[book.pk]))
        self.assertTemplateUsed(response, "bookfiles/bookfile_list.html")
        self.assertContains(response, "هنوز فایلی برای این کتاب بارگذاری نشده")
        self.assertContains(response, "حقوق مدنی")
        self.assertContains(response, "کتاب‌های من")
        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, "multiple")
        self.assertNotContains(response, "cdn.")

    def test_list_heading_order_and_links(self):
        book = make_book()
        first = BookFile.objects.create(book=book, file=pdf("a.pdf"), original_name="فصل-۱.pdf", size=2_500_000)
        second = BookFile.objects.create(book=book, file=pdf("b.pdf"), original_name="فصل-۲.pdf", size=1024)
        response = self.client.get(reverse("bookfiles:list", args=[book.pk]))
        html = response.content.decode()
        self.assertContains(response, "2 فایل")
        self.assertContains(response, "2٫4 مگابایت")
        self.assertContains(response, "1٫0 کیلوبایت")
        self.assertLess(html.index("فصل-۱.pdf"), html.index("فصل-۲.pdf"))
        self.assertContains(response, 'href="/media/')
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, f'id="delete-file-{first.pk}"')
        self.assertContains(response, reverse("bookfiles:delete", args=[book.pk, second.pk]))
        self.assertNotContains(response, "هنوز فایلی برای این کتاب بارگذاری نشده")

    def test_upload_one_file(self):
        book = make_book()
        response = self.upload(book, pdf("فصل-۱.pdf"), follow=True)
        self.assertRedirects(response, reverse("bookfiles:list", args=[book.pk]))
        self.assertContains(response, "1 فایل به «حقوق مدنی» اضافه شد.")
        record = book.files.get()
        self.assertEqual(record.original_name, "فصل-۱.pdf")
        self.assertEqual(record.size, len(PDF_BODY))
        self.assertTrue(Path(record.file.path).exists())
        self.assertTrue(record.file.name.startswith(f"books/{book.pk}/"))

    def test_upload_three_files(self):
        book = make_book()
        response = self.upload(book, pdf("a.pdf"), pdf("b.pdf"), pdf("c.pdf"), follow=True)
        self.assertContains(response, "3 فایل به «حقوق مدنی» اضافه شد.")
        self.assertEqual(book.files.count(), 3)

    def test_same_name_twice_keeps_both(self):
        book = make_book()
        self.upload(book, pdf("فصل-۱.pdf"))
        self.upload(book, pdf("فصل-۱.pdf"))
        names = list(book.files.values_list("original_name", flat=True))
        self.assertEqual(names, ["فصل-۱.pdf", "فصل-۱.pdf"])
        stored = list(book.files.values_list("file", flat=True))
        self.assertNotEqual(stored[0], stored[1])

    def test_non_pdf_is_rejected(self):
        book = make_book()
        response = self.upload(book, pdf("جزوه.docx"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "«جزوه.docx» فایل PDF نیست. فقط فایل PDF پذیرفته می‌شود.")
        self.assertContains(response, "invalid-feedback")
        self.assertEqual(BookFile.objects.count(), 0)

    def test_renamed_non_pdf_is_rejected(self):
        book = make_book()
        response = self.upload(book, pdf("عکس.pdf", body=PNG_BODY))
        self.assertContains(response, "«عکس.pdf» فایل PDF نیست")
        self.assertEqual(BookFile.objects.count(), 0)

    def test_one_bad_file_among_many_saves_nothing(self):
        book = make_book()
        BookFile.objects.create(book=book, file=pdf("old.pdf"), original_name="قدیمی.pdf", size=5)
        response = self.upload(book, pdf("a.pdf"), pdf("b.pdf"), pdf("c.docx"))
        self.assertContains(response, "«c.docx» فایل PDF نیست")
        self.assertEqual(book.files.count(), 1)
        self.assertContains(response, "قدیمی.pdf")

    def test_empty_form(self):
        book = make_book()
        response = self.client.post(reverse("bookfiles:list", args=[book.pk]), {})
        self.assertContains(response, "دست‌کم یک فایل PDF انتخاب کنید.")
        self.assertEqual(BookFile.objects.count(), 0)


class BookFileDeleteViewTests(MediaTestCase):
    def setUp(self):
        self.book = make_book()
        self.first = BookFile.objects.create(book=self.book, file=pdf("a.pdf"), original_name="فصل-۱.pdf", size=5)
        self.second = BookFile.objects.create(book=self.book, file=pdf("b.pdf"), original_name="فصل-۲.pdf", size=5)

    def test_get_confirm_page(self):
        response = self.client.get(reverse("bookfiles:delete", args=[self.book.pk, self.first.pk]))
        self.assertTemplateUsed(response, "bookfiles/bookfile_confirm_delete.html")
        self.assertContains(response, "فصل-۱.pdf")
        self.assertContains(response, "حذف شود؟")

    def test_post_deletes_record_and_file(self):
        path = Path(self.first.file.path)
        response = self.client.post(reverse("bookfiles:delete", args=[self.book.pk, self.first.pk]), follow=True)
        self.assertRedirects(response, reverse("bookfiles:list", args=[self.book.pk]))
        self.assertContains(response, "فایل «فصل-۱.pdf» حذف شد.")
        self.assertEqual(list(self.book.files.all()), [self.second])
        self.assertFalse(path.exists())
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    def test_deleting_last_file_shows_empty_state(self):
        self.client.post(reverse("bookfiles:delete", args=[self.book.pk, self.first.pk]))
        response = self.client.post(reverse("bookfiles:delete", args=[self.book.pk, self.second.pk]), follow=True)
        self.assertContains(response, "هنوز فایلی برای این کتاب بارگذاری نشده")

    def test_wrong_book_or_missing_file_is_404(self):
        other = make_book(title="حقوق تجارت")
        self.assertEqual(self.client.post(reverse("bookfiles:delete", args=[other.pk, self.first.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("bookfiles:delete", args=[self.book.pk, 999])).status_code, 404)
        self.assertEqual(self.book.files.count(), 2)


class BookFileAdminTests(MediaTestCase):
    def test_admin_changelist_renders(self):
        user = get_user_model().objects.create_superuser("admin", "a@example.com", "pass12345")
        self.client.force_login(user)
        BookFile.objects.create(book=make_book(), file=pdf("a.pdf"), original_name="فصل-۱.pdf", size=5)
        response = self.client.get("/admin/bookfiles/bookfile/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "فصل-۱.pdf")
