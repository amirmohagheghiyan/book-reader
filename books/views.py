from itertools import groupby

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import BookForm
from .jalali import today_jalali
from .models import Book, Status


class BookListView(ListView):
    """Dashboard at /: books grouped by (year, month), with search and filter."""

    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"

    def get_filters(self):
        query = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "")
        if status not in Status.values:
            status = ""
        return query, status

    def get_queryset(self):
        # Meta.ordering is ignored once a query groups (annotate + Count), so repeat it.
        # distinct=True: two joined reverse relations would otherwise multiply the counts.
        queryset = (
            super()
            .get_queryset()
            .annotate(
                file_count=Count("files", distinct=True),
                block_count=Count("blocks", distinct=True),
            )
            .order_by(*Book._meta.ordering)
        )
        query, status = self.get_filters()
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(author__icontains=query))
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query, status = self.get_filters()
        books = list(context["books"])
        context["groups"] = [
            {"label": items[0].period_label, "books": items}
            for _, group in groupby(books, key=lambda b: (b.year, b.month))
            for items in [list(group)]
        ]
        context["q"] = query
        context["status"] = status
        context["status_choices"] = Status.choices
        context["is_filtered"] = bool(query or status)
        context["has_any_books"] = Book.objects.exists()
        return context


class BreadcrumbsMixin:
    """Adds the breadcrumb trail used by components/page-header.html."""

    page_label = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            {"label": "کتاب‌های من", "url": reverse_lazy("books:list")},
            {"label": self.page_label},
        ]
        return context


class BookCreateView(BreadcrumbsMixin, SuccessMessageMixin, CreateView):
    page_label = "افزودن کتاب"
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url = reverse_lazy("books:list")
    success_message = "کتاب «%(title)s» ذخیره شد."

    def get_initial(self):
        year, month = today_jalali()
        return {"year": year, "month": month, "status": Status.QUEUED}


class BookUpdateView(BreadcrumbsMixin, SuccessMessageMixin, UpdateView):
    page_label = "ویرایش کتاب"
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url = reverse_lazy("books:list")
    success_message = "کتاب «%(title)s» ذخیره شد."


class BookDeleteView(BreadcrumbsMixin, DeleteView):
    page_label = "حذف کتاب"
    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy("books:list")

    def form_valid(self, form):
        messages.success(self.request, f"کتاب «{self.object.title}» حذف شد.")
        return super().form_valid(form)
