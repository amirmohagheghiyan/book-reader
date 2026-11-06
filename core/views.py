from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from .forms import DesignSystemSampleForm


class DesignSystemView(TemplateView):
    """UI kit page: shows every token and shared component in every state."""

    template_name = "core/design-system.html"

    sections = [
        ("sec-brand", "برند"),
        ("sec-colors", "رنگ‌ها"),
        ("sec-type", "تایپوگرافی"),
        ("sec-buttons", "دکمه‌ها"),
        ("sec-forms", "فرم‌ها"),
        ("sec-feedback", "بازخورد"),
        ("sec-nav", "ناوبری"),
        ("sec-overlays", "لایه‌ها"),
        ("sec-data", "نمایش اطلاعات"),
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sections"] = self.sections
        context["breadcrumbs"] = [
            {"label": "خانه", "url": reverse_lazy("books:list")},
            {"label": "سیستم طراحی"},
        ]
        context["form"] = DesignSystemSampleForm()
        context["invalid_form"] = DesignSystemSampleForm(
            data={"title": "", "email": "nahid@", "pages": "0", "status": ""}
        )
        context["invalid_form"].is_valid()
        paginator = Paginator(range(1, 48), 10)
        context["page_obj"] = paginator.get_page(self.request.GET.get("page"))
        context["rows"] = [
            {"title": "حقوق مدنی، جلد اول", "author": "ناصر کاتوزیان", "month": "مهر", "status": "done"},
            {"title": "آیین دادرسی کیفری", "author": "علی خالقی", "month": "آبان", "status": "reading"},
            {"title": "حقوق تجارت", "author": "ربیعا اسکینی", "month": "آذر", "status": "queued"},
        ]
        return context
