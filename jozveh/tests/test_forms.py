from django.test import SimpleTestCase

from jozveh.forms import (
    FORMS_BY_KIND,
    ConceptMapForm,
    HeadingForm,
    StepsForm,
    TableForm,
    TextForm,
)
from jozveh.models import Block

from .helpers import VALID_DATA


def data_of(form_class, **fields):
    form = form_class(data=fields)
    assert form.is_valid(), form.errors
    return form.to_data()


class RoundTripTests(SimpleTestCase):
    def test_every_kind_round_trips(self):
        self.assertEqual(set(FORMS_BY_KIND), set(Block.Kind))
        for kind, data in VALID_DATA.items():
            with self.subTest(kind=kind):
                form_class = FORMS_BY_KIND[kind]
                form = form_class(data=form_class.initial_from(data))
                self.assertTrue(form.is_valid(), form.errors)
                self.assertEqual(form.to_data(), data)

    def test_branch_without_children_round_trips(self):
        data = {"center": "م", "branches": [{"label": "تعریف", "children": []}]}
        self.assertEqual(ConceptMapForm.initial_from(data)["branches"], "تعریف")
        self.assertEqual(data_of(ConceptMapForm, **ConceptMapForm.initial_from(data)), data)


class SimpleKindTests(SimpleTestCase):
    def test_valid_heading_and_text(self):
        self.assertEqual(data_of(HeadingForm, text=" فصل اول "), {"text": "فصل اول"})
        self.assertEqual(data_of(TextForm, text="الف\r\n\r\nب"), {"text": "الف\n\nب"})

    def test_empty_or_whitespace_is_required(self):
        for form_class in (FORMS_BY_KIND[Block.Kind.HEADING], TextForm, FORMS_BY_KIND[Block.Kind.NOTE]):
            for value in ("", "   \n  "):
                with self.subTest(form=form_class.__name__, value=value):
                    form = form_class(data={"text": value})
                    self.assertFalse(form.is_valid())
                    self.assertIn("text", form.errors)

    def test_heading_over_200_characters(self):
        self.assertFalse(HeadingForm(data={"text": "ا" * 201}).is_valid())


class StepsFormTests(SimpleTestCase):
    def test_three_steps_and_blank_lines(self):
        data = data_of(StepsForm, items="طرح دعوا\n\n  جلسه‌ی رسیدگی \r\n\nصدور رأی\n")
        self.assertEqual(data, {"items": ["طرح دعوا", "جلسه‌ی رسیدگی", "صدور رأی"]})

    def test_empty(self):
        for value in ("", "\n \n"):
            form = StepsForm(data={"items": value})
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors["items"], ["دست‌کم یک گام بنویسید."])


class TableFormTests(SimpleTestCase):
    def test_valid_table_with_trimming(self):
        data = data_of(TableForm, rows=" اصطلاح |تعریف \nاهلیت|  توانایی داشتن حق")
        self.assertEqual(data, {"header": ["اصطلاح", "تعریف"], "rows": [["اهلیت", "توانایی داشتن حق"]]})

    def test_short_row_is_padded(self):
        data = data_of(TableForm, rows="الف | ب | ج\n۱ | ۲")
        self.assertEqual(data["rows"], [["۱", "۲", ""]])

    def test_long_row_names_the_line(self):
        form = TableForm(data={"rows": "الف | ب\n۱ | ۲\n\n۳ | ۴ | ۵"})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["rows"], ["ردیف 3 بیشتر از سرستون‌ها خانه دارد."])

    def test_header_only(self):
        form = TableForm(data={"rows": "الف | ب\n"})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["rows"], ["دست‌کم یک ردیف زیر سرستون‌ها بنویسید."])


class ConceptMapFormTests(SimpleTestCase):
    def test_two_branches_with_both_separators(self):
        data = data_of(ConceptMapForm, center="اشخاص", branches="حقیقی: اهلیت، اقامتگاه\nحقوقی: ثبت, تابعیت")
        self.assertEqual(data, VALID_DATA[Block.Kind.CONCEPT_MAP])

    def test_branch_without_colon_and_child_with_colon(self):
        data = data_of(ConceptMapForm, center="م", branches="تعریف\nمواد: ماده ۱: کلیات")
        self.assertEqual(
            data["branches"],
            [{"label": "تعریف", "children": []}, {"label": "مواد", "children": ["ماده ۱: کلیات"]}],
        )

    def test_empty_center_or_branches(self):
        form = ConceptMapForm(data={"center": "", "branches": "الف"})
        self.assertFalse(form.is_valid())
        self.assertIn("center", form.errors)
        form = ConceptMapForm(data={"center": "م", "branches": " \n "})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["branches"], ["دست‌کم یک شاخه بنویسید."])
