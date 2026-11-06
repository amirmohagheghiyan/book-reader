from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, FormView

from books.models import Book

from .forms import BookFileUploadForm
from .models import BookFile


def files_breadcrumbs():
    return [
        {"label": "کتاب‌های من", "url": reverse_lazy("books:list")},
        {"label": "فایل‌های کتاب"},
    ]


class BookFileListView(FormView):
    """One page per book: the upload form and the list of its PDF files."""

    template_name = "bookfiles/bookfile_list.html"
    form_class = BookFileUploadForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.book = get_object_or_404(Book, pk=kwargs["pk"])

    def get_success_url(self):
        return reverse("bookfiles:list", args=[self.book.pk])

    def form_valid(self, form):
        with transaction.atomic():
            count = form.save(self.book)
        messages.success(self.request, f"{count} فایل به «{self.book.title}» اضافه شد.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["book"] = self.book
        context["files"] = self.book.files.all()
        context["breadcrumbs"] = files_breadcrumbs()
        return context


class BookFileDeleteView(DeleteView):
    """Deletes one file after confirmation; the record and the file on disk go together."""

    model = BookFile
    template_name = "bookfiles/bookfile_confirm_delete.html"

    def get_queryset(self):
        return BookFile.objects.filter(book_id=self.kwargs["book_pk"])

    def get_success_url(self):
        return reverse("bookfiles:list", args=[self.kwargs["book_pk"]])

    def form_valid(self, form):
        messages.success(self.request, f"فایل «{self.object.original_name}» حذف شد.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = files_breadcrumbs()
        return context
