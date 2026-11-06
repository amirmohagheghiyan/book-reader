"""One plain form per block kind: the text the user types ⇄ the block's `data` (design D3)."""

import re

from django import forms

from .models import Block

CHILD_SEPARATOR = re.compile(r"[،,]")


def textarea(rows=6):
    return forms.Textarea(attrs={"class": "form-control", "rows": rows, "dir": "auto"})


def text_input():
    return forms.TextInput(attrs={"class": "form-control"})


def non_blank_lines(value):
    return [line.strip() for line in value.splitlines() if line.strip()]


class BlockForm(forms.Form):
    """Base: subclasses turn cleaned input into `data` and stored `data` back into initial text."""

    def to_data(self):
        raise NotImplementedError

    @classmethod
    def initial_from(cls, data):
        raise NotImplementedError


class HeadingForm(BlockForm):
    text = forms.CharField(label="متن عنوان", max_length=200, widget=text_input())

    def to_data(self):
        return {"text": self.cleaned_data["text"].replace("\r\n", "\n")}

    @classmethod
    def initial_from(cls, data):
        return {"text": data.get("text", "")}


class TextForm(HeadingForm):
    text = forms.CharField(
        label="متن",
        help_text="برای شروع پاراگراف تازه یک خط خالی بگذارید.",
        widget=textarea(8),
    )


class NoteForm(HeadingForm):
    text = forms.CharField(
        label="متن نکته",
        help_text="برای شروع پاراگراف تازه یک خط خالی بگذارید.",
        widget=textarea(4),
    )


class StepsForm(BlockForm):
    items = forms.CharField(
        label="گام‌ها",
        help_text="هر خط یک گام. مثلاً: «طرح دعوا» در خط اول، «صدور رأی» در خط دوم.",
        error_messages={"required": "دست‌کم یک گام بنویسید."},
        widget=textarea(6),
    )

    def clean_items(self):
        items = non_blank_lines(self.cleaned_data["items"])
        if not items:
            raise forms.ValidationError("دست‌کم یک گام بنویسید.")
        return items

    def to_data(self):
        return {"items": self.cleaned_data["items"]}

    @classmethod
    def initial_from(cls, data):
        return {"items": "\n".join(data.get("items", []))}


class TableForm(BlockForm):
    rows = forms.CharField(
        label="جدول",
        help_text="خط اول سرستون‌ها، هر خط بعدی یک ردیف؛ خانه‌ها را با | جدا کنید. "
        "مثلاً: «اصطلاح | تعریف» و زیرش «اهلیت | توانایی داشتن حق».",
        widget=textarea(6),
    )

    def clean_rows(self):
        # Keep each line's number as typed (blank lines count) so errors match the text box.
        numbered = [
            (number, [cell.strip() for cell in line.split("|")])
            for number, line in enumerate(self.cleaned_data["rows"].splitlines(), start=1)
            if line.strip()
        ]
        if len(numbered) < 2:
            raise forms.ValidationError("دست‌کم یک ردیف زیر سرستون‌ها بنویسید.")
        header = numbered[0][1]
        for number, row in numbered[1:]:
            if len(row) > len(header):
                raise forms.ValidationError(f"خط {number} بیشتر از سرستون‌ها خانه دارد.")
        rows = [row + [""] * (len(header) - len(row)) for _, row in numbered[1:]]
        return {"header": header, "rows": rows}

    def to_data(self):
        return self.cleaned_data["rows"]

    @classmethod
    def initial_from(cls, data):
        lines = [data.get("header", [])] + data.get("rows", [])
        return {"rows": "\n".join(" | ".join(line) for line in lines)}


class ConceptMapForm(BlockForm):
    center = forms.CharField(label="مفهوم مرکزی", max_length=200, widget=text_input())
    branches = forms.CharField(
        label="شاخه‌ها",
        help_text="هر خط یک شاخه: نام شاخه، دو نقطه، و زیرمفهوم‌ها با ویرگول. "
        "مثلاً: «حقیقی: اهلیت، اقامتگاه». خطی بدون دو نقطه شاخه‌ای بی‌زیرمفهوم است.",
        error_messages={"required": "دست‌کم یک شاخه بنویسید."},
        widget=textarea(6),
    )

    def clean_branches(self):
        branches = []
        for line in non_blank_lines(self.cleaned_data["branches"]):
            label, _, rest = line.partition(":")
            children = [c.strip() for c in CHILD_SEPARATOR.split(rest) if c.strip()]
            if label.strip():
                branches.append({"label": label.strip(), "children": children})
        if not branches:
            raise forms.ValidationError("دست‌کم یک شاخه بنویسید.")
        return branches

    def to_data(self):
        return {"center": self.cleaned_data["center"], "branches": self.cleaned_data["branches"]}

    @classmethod
    def initial_from(cls, data):
        lines = []
        for branch in data.get("branches", []):
            children = "، ".join(branch.get("children", []))
            lines.append(f"{branch['label']}: {children}" if children else branch["label"])
        return {"center": data.get("center", ""), "branches": "\n".join(lines)}


FORMS_BY_KIND = {
    Block.Kind.HEADING: HeadingForm,
    Block.Kind.TEXT: TextForm,
    Block.Kind.NOTE: NoteForm,
    Block.Kind.STEPS: StepsForm,
    Block.Kind.TABLE: TableForm,
    Block.Kind.CONCEPT_MAP: ConceptMapForm,
}
