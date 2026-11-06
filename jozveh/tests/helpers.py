from books.models import Book, Month
from jozveh.models import Block

VALID_DATA = {
    Block.Kind.HEADING: {"text": "فصل اول: اشخاص"},
    Block.Kind.TEXT: {"text": "پاراگراف اول\n\nپاراگراف دوم"},
    Block.Kind.NOTE: {"text": "اهلیت شرط صحت معامله است."},
    Block.Kind.STEPS: {"items": ["طرح دعوا", "جلسه‌ی رسیدگی", "صدور رأی"]},
    Block.Kind.TABLE: {
        "header": ["اصطلاح", "تعریف"],
        "rows": [["اهلیت", "توانایی داشتن حق"], ["ولایت", "سرپرستی قانونی"]],
    },
    Block.Kind.CONCEPT_MAP: {
        "center": "اشخاص",
        "branches": [
            {"label": "حقیقی", "children": ["اهلیت", "اقامتگاه"]},
            {"label": "حقوقی", "children": ["ثبت", "تابعیت"]},
        ],
    },
}


def make_book(**kwargs):
    data = {"title": "حقوق مدنی", "author": "ناصر کاتوزیان", "year": 1404, "month": Month.MEHR}
    data.update(kwargs)
    return Book.objects.create(**data)


def add_text(book, text):
    return Block.append(book, Block.Kind.TEXT, {"text": text})


def texts(book):
    return [b.data["text"] for b in book.blocks.all()]
