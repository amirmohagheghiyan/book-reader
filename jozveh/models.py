from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F, Max

from books.models import Book

SUMMARY_LENGTH = 40


def _is_text(value):
    return isinstance(value, str) and value.strip() != ""


def _is_text_list(value, allow_empty=False):
    return (
        isinstance(value, list)
        and (allow_empty or len(value) > 0)
        and all(isinstance(item, str) for item in value)
    )


def _valid_table(data):
    header, rows = data.get("header"), data.get("rows")
    return (
        _is_text_list(header)
        and isinstance(rows, list)
        and len(rows) > 0
        and all(_is_text_list(row) and len(row) == len(header) for row in rows)
    )


def _valid_concept_map(data):
    branches = data.get("branches")
    return (
        _is_text(data.get("center"))
        and isinstance(branches, list)
        and len(branches) > 0
        and all(
            isinstance(b, dict)
            and _is_text(b.get("label"))
            and _is_text_list(b.get("children"), allow_empty=True)
            for b in branches
        )
    )


class Block(models.Model):
    """One ordered piece of a book's جزوه; `data` holds its structured content (design D2)."""

    class Kind(models.TextChoices):
        HEADING = "heading", "عنوان"
        TEXT = "text", "متن"
        NOTE = "note", "نکته"
        STEPS = "steps", "مراحل"
        TABLE = "table", "جدول"
        CONCEPT_MAP = "concept_map", "نقشه‌ی مفهومی"

    SHAPE_CHECKS = {
        Kind.HEADING: lambda d: _is_text(d.get("text")),
        Kind.TEXT: lambda d: _is_text(d.get("text")),
        Kind.NOTE: lambda d: _is_text(d.get("text")),
        Kind.STEPS: lambda d: _is_text_list(d.get("items")),
        Kind.TABLE: _valid_table,
        Kind.CONCEPT_MAP: _valid_concept_map,
    }

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="blocks", verbose_name="کتاب"
    )
    kind = models.CharField("نوع", max_length=20, choices=Kind.choices)
    position = models.PositiveIntegerField("جایگاه")
    data = models.JSONField("محتوا", default=dict)
    created_at = models.DateTimeField("زمان ساخت", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین تغییر", auto_now=True)

    class Meta:
        ordering = ["position", "pk"]
        verbose_name = "بلوک جزوه"
        verbose_name_plural = "بلوک‌های جزوه"

    def __str__(self):
        return self.summary

    def clean(self):
        check = self.SHAPE_CHECKS.get(self.kind)
        if check is None:
            raise ValidationError({"kind": "نوع بلوک معتبر نیست."})
        if not isinstance(self.data, dict) or not check(self.data):
            raise ValidationError({"data": "محتوای بلوک با نوع آن جور نیست."})

    @property
    def main_text(self):
        """The text that best names this block, used for summaries."""
        data = self.data if isinstance(self.data, dict) else {}
        if self.kind == self.Kind.STEPS:
            return (data.get("items") or [""])[0]
        if self.kind == self.Kind.TABLE:
            return "، ".join(data.get("header") or [])
        if self.kind == self.Kind.CONCEPT_MAP:
            return data.get("center", "")
        return data.get("text", "")

    @property
    def summary(self):
        """Kind label plus the start of the content, e.g. «متن: اهلیت یعنی…»."""
        text = " ".join(str(self.main_text).split())
        if len(text) > SUMMARY_LENGTH:
            text = text[:SUMMARY_LENGTH].rstrip() + "…"
        return f"{self.get_kind_display()}: {text}" if text else self.get_kind_display()

    @property
    def template_name(self):
        return f"jozveh/blocks/{self.kind}.html"

    # Ordering (design D4). Gaps after deletes are harmless: only comparisons matter.

    @classmethod
    def append(cls, book, kind, data):
        with transaction.atomic():
            last = book.blocks.aggregate(last=Max("position"))["last"] or 0
            return cls.objects.create(book=book, kind=kind, data=data, position=last + 1)

    @classmethod
    def insert_after(cls, anchor, kind, data):
        with transaction.atomic():
            anchor.book.blocks.filter(position__gt=anchor.position).update(
                position=F("position") + 1
            )
            return cls.objects.create(
                book=anchor.book, kind=kind, data=data, position=anchor.position + 1
            )

    def move(self, direction):
        """Swap with the neighbor above ("up") or below ("down"); False at either end."""
        if direction not in ("up", "down"):
            raise ValueError(f"unknown direction: {direction}")
        with transaction.atomic():
            blocks = list(self.book.blocks.select_for_update())
            index = next(i for i, b in enumerate(blocks) if b.pk == self.pk)
            other = index - 1 if direction == "up" else index + 1
            if not 0 <= other < len(blocks):
                return False
            if len({b.position for b in blocks}) != len(blocks):
                # Repair duplicate positions (e.g. from admin) so the swap is visible.
                for number, block in enumerate(blocks, start=1):
                    block.position = number
                Block.objects.bulk_update(blocks, ["position"])
            current, neighbor = blocks[index], blocks[other]
            current.position, neighbor.position = neighbor.position, current.position
            Block.objects.bulk_update([current, neighbor], ["position"])
            self.position = current.position
        return True
