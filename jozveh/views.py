from django.contrib import messages
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DeleteView, FormView, TemplateView

from books.models import Book

from .forms import FORMS_BY_KIND
from .models import Block

KIND_DESCRIPTIONS = {
    Block.Kind.HEADING: "تیتر یک بخش از جزوه، در یک خط.",
    Block.Kind.TEXT: "یک یا چند پاراگراف توضیح.",
    Block.Kind.NOTE: "نکته‌ای مهم در یک کادر رنگی برجسته.",
    Block.Kind.STEPS: "گام‌های شماره‌دار یک روند، هر خط یک گام.",
    Block.Kind.TABLE: "جدولی با سرستون‌ها و چند ردیف.",
    Block.Kind.CONCEPT_MAP: "یک مفهوم مرکزی با شاخه‌ها و زیرمفهوم‌ها، به شکل درخت.",
}


def editor_url(book, block=None):
    url = reverse("jozveh:editor", args=[book.pk])
    return f"{url}#block-{block.pk}" if block else url


class BookBlocksMixin:
    """Loads the book from the URL; blocks are always looked up through that book."""

    page_label = ""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.book = get_object_or_404(Book, pk=kwargs["pk"])

    def get_block(self):
        return get_object_or_404(self.book.blocks, pk=self.kwargs["block_pk"])

    def get_after(self):
        """The block id from `?after=`, kept only when it is a number."""
        after = self.request.GET.get("after", "")
        return after if after.isdigit() else ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = f"جزوه‌ی «{self.book.title}»"
        crumbs = [{"label": "کتاب‌های من", "url": reverse_lazy("books:list")}]
        if self.page_label:
            crumbs += [{"label": title, "url": editor_url(self.book)}, {"label": self.page_label}]
        else:
            crumbs.append({"label": title})
        context.update(book=self.book, jozveh_title=title, breadcrumbs=crumbs)
        return context


class JozvehEditorView(BookBlocksMixin, TemplateView):
    template_name = "jozveh/editor.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blocks"] = list(self.book.blocks.all())
        return context


class JozvehPrintView(JozvehEditorView):
    template_name = "jozveh/print.html"


class BlockKindPickView(BookBlocksMixin, TemplateView):
    template_name = "jozveh/pick.html"
    page_label = "افزودن بلوک"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        after = self.get_after()
        query = f"?after={after}" if after else ""
        context["kinds"] = [
            {
                "label": label,
                "text": KIND_DESCRIPTIONS[value],
                "url": reverse("jozveh:add", args=[self.book.pk, value]) + query,
            }
            for value, label in Block.Kind.choices
        ]
        return context


class BlockFormMixin(BookBlocksMixin):
    template_name = "jozveh/block_form.html"

    def get_form_class(self):
        return FORMS_BY_KIND[self.kind]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["kind_label"] = Block.Kind(self.kind).label
        return context


class BlockCreateView(BlockFormMixin, FormView):
    page_label = "افزودن بلوک"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if kwargs["kind"] not in Block.Kind.values:
            raise Http404("نوع بلوک ناشناخته است.")
        self.kind = kwargs["kind"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        after = self.get_after()
        context["cancel_url"] = editor_url(self.book)
        context["back_url"] = reverse("jozveh:pick", args=[self.book.pk]) + (
            f"?after={after}" if after else ""
        )
        return context

    def form_valid(self, form):
        after = self.get_after()
        anchor = self.book.blocks.filter(pk=after).first() if after else None
        if anchor:
            block = Block.insert_after(anchor, self.kind, form.to_data())
        else:
            block = Block.append(self.book, self.kind, form.to_data())
        messages.success(self.request, f"بلوک «{block.get_kind_display()}» اضافه شد.")
        return HttpResponseRedirect(editor_url(self.book, block))


class BlockUpdateView(BlockFormMixin, FormView):
    page_label = "ویرایش بلوک"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.block = self.get_block()
        self.kind = self.block.kind

    def get_initial(self):
        return self.get_form_class().initial_from(self.block.data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = editor_url(self.book, self.block)
        return context

    def form_valid(self, form):
        self.block.data = form.to_data()
        self.block.save(update_fields=["data", "updated_at"])
        messages.success(self.request, f"بلوک «{self.block.get_kind_display()}» ذخیره شد.")
        return HttpResponseRedirect(editor_url(self.book, self.block))


class BlockMoveView(BookBlocksMixin, View):
    """POST `direction=up|down`; no message, the anchor keeps the user on the block."""

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        block = self.get_block()
        direction = request.POST.get("direction")
        if direction not in ("up", "down"):
            return HttpResponseBadRequest("direction must be up or down")
        block.move(direction)
        return HttpResponseRedirect(editor_url(self.book, block))


class BlockDeleteView(BookBlocksMixin, DeleteView):
    template_name = "jozveh/block_confirm_delete.html"
    page_label = "حذف بلوک"

    def get_object(self, queryset=None):
        return self.get_block()

    def get_success_url(self):
        return editor_url(self.book)

    def form_valid(self, form):
        messages.success(self.request, "بلوک حذف شد.")
        return super().form_valid(form)
