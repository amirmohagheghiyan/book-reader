# product.md

Approved product context for assistants: the idea and what has actually been
built. It is not approval to build every planned capability; each capability
is built through its own approved OpenSpec change. Prompt 1 filled this file
from the owner's idea; brackets mean «not decided yet».

## Product

- **Name:** جزوه‌ساز
- **One sentence:** «جزوه‌ساز» کتاب‌های تخصصیِ ماهانه‌ی یک دانشجو را یک‌جا
  نگه می‌دارد و پیگیری می‌کند، و از فایل PDF هر کتاب قطور، با کمک هوش مصنوعی،
  یک جزوه‌ی خلاصه و تصویری می‌سازد که به Word و PDF خروجی گرفته می‌شود.
- **Language and direction:** Persian, right-to-left.

## People Who Use It

- صاحب محصول: یک دانشجو که هر ماه باید چند کتاب تخصصی رشته‌ی تحصیلی‌اش را
  بخواند. فقط همین یک نفر از محصول استفاده می‌کند.
- There is no login in this workshop version: everyone who opens the local
  address sees and can change the same data.

## Problem and Goal

- **Problem:** کتاب‌های تخصصی قطورند و خواندنشان خسته‌کننده است. پیگیری
  این‌که هر ماه کدام کتاب‌ها باید خوانده شود و کدام تمام شده، جایی یک‌جا
  ندارد.
- **Goal:** خواندن کتاب‌های تخصصی منظم‌تر و لذت‌بخش‌تر شود: کتاب‌های هر ماه
  یک‌جا ثبت و دنبال شوند، و برای هر کتاب یک جزوه‌ی خلاصه و تصویری ساخته شود
  که به‌جای خواندن کامل کتاب، بشود آن را خواند و به‌صورت Word یا PDF نگه داشت.

## Owner Decisions (2026-11-06)

- آپلود فایل PDF کتاب روی همین دستگاه مجاز است. فایل روی همین کامپیوتر
  ذخیره می‌شود؛ فقط PDF پذیرفته می‌شود.
- تنها اتصال شبکه‌ای محصول، تماس با یک سرویس هوش مصنوعی است که آدرس و
  مدلش در فایل `.env` تنظیم می‌شود. فعلاً Google AI Studio، بعداً Ollama
  روی همین دستگاه؛ تعویض سرویس فقط با تغییر `.env` انجام می‌شود.
- بسته‌های پایتون فقط با تأیید صاحب محصول اضافه می‌شوند و هر بسته در
  OpenSpec change خودش.
- جزوه از **بلوک‌های مرتب** ساخته می‌شود (مثلاً عنوان، خلاصه‌ی متن، نکته‌ها،
  نمودار)؛ ترتیب بلوک‌ها بخشی از جزوه است.
- نمودارهای جزوه **ساختاری**‌اند، نه تصویر تولیدشده: نقشه‌ی مفهومی، مراحل
  (گام‌به‌گام)، و جدول. محصول آن‌ها را از داده‌ی ساختاری می‌کشد.
- خروجی جزوه: فایل Word (`.docx`) و PDF.

## Planned Capabilities (in build order; none of 2–4 built yet)

1. **کتابخانه‌ی ماهانه:** کاربر هر کتاب را با نام، نویسنده، ماهِ مطالعه و
   وضعیت («در صف»، «در حال خواندن»، «تمام‌شده») ثبت می‌کند، فهرست کتاب‌ها را
   می‌بیند و هر کتاب را ویرایش یا با تأیید حذف می‌کند.
2. **آپلود PDF کتاب:** کاربر برای هر کتاب فایل PDF آن را از همین دستگاه
   بارگذاری می‌کند، می‌بیند کدام کتاب فایل دارد، و می‌تواند فایل را عوض یا
   با تأیید حذف کند. فایل غیر PDF با پیام خطا رد می‌شود.
3. **ساخت جزوه با هوش مصنوعی:** کاربر برای کتابی که PDF دارد «ساخت جزوه» را
   می‌زند. محصول متن کتاب را به سرویس هوش مصنوعیِ تنظیم‌شده در `.env`
   می‌فرستد و یک جزوه از بلوک‌های مرتب می‌سازد که نمودارهای ساختاری
   (نقشه‌ی مفهومی، مراحل، جدول) هم دارد. جزوه در محصول نمایش داده می‌شود؛
   خطای سرویس (قطع اینترنت، کلید نامعتبر) با پیام روشن نشان داده می‌شود.
4. **خروجی Word و PDF:** کاربر جزوه‌ی ساخته‌شده را به‌صورت فایل Word
   (`.docx`) یا PDF دانلود می‌کند؛ متن فارسی راست‌به‌چپ و نمودارها در فایل
   خروجی حفظ می‌شوند.

Each capability is built through its own approved OpenSpec change. A
capability that needs a new Python package (reading PDF text, calling the AI
service, writing Word or PDF) gets that package approved inside its change,
one package per change (`AGENTS.md`).

## Information the Product Keeps

- **کتاب:** نام، نویسنده، ماهِ مطالعه، وضعیت («در صف»، «در حال خواندن»،
  «تمام‌شده»)، و فایل PDF (از قابلیت ۲). جزئیات دقیق فیلدها در OpenSpec
  change همان قابلیت تصمیم‌گیری می‌شود.
- **جزوه:** برای هر کتاب، فهرستی مرتب از بلوک‌ها؛ هر بلوک یک نوع (عنوان،
  متن، نکته، نقشه‌ی مفهومی، مراحل، جدول) و محتوای خودش را دارد. نمودارها
  به‌صورت داده‌ی ساختاری نگه داشته می‌شوند، نه عکس.
- **تنظیمات هوش مصنوعی:** در فایل `.env` روی همین دستگاه، نه در پایگاه داده
  و نه در صفحه‌ای از محصول.

## Out of Scope

- Publishing on the internet, user accounts and login, email, payments,
  connecting to any service other than the single AI service above.
- آپلود فایل‌هایی جز PDF، ذخیره‌ی فایل در فضای ابری، تصویرسازی با هوش
  مصنوعی (نمودارها فقط ساختاری‌اند)، خروجی‌هایی جز Word و PDF، و
  استفاده‌ی چند نفر با داده‌ی جدا.

## Tone and Wording

- [not decided by the owner yet] Until then, the temporary default is the
  plain, friendly Persian of `design.md` («ذخیره»، «افزودن»، «حذف»); product
  words: «کتاب», «ماهِ مطالعه», «وضعیت», «جزوه».

## Open Questions

- رشته‌ی تحصیلی و نوع کتاب‌ها چیست؟ (برای واژگان و مثال‌های صفحه‌ها)
- لحن محصول دوستانه باشد یا رسمی؟ کلمه‌ای هست که ترجیح دهید یا نخواهید؟
- به‌جز نام، نویسنده، ماه و وضعیت، چیز دیگری برای هر کتاب لازم است؟ (مثلاً
  تعداد صفحات، فصل‌ها، یادداشت کوتاه)
- «ماهِ مطالعه» چطور وارد می‌شود؟ متن آزاد مثل «آبان ۱۴۰۴» یا انتخاب از
  فهرست ماه‌های شمسی؟ (تاریخ شمسی به کتابخانه‌ی جداگانه و تأیید نیاز دارد)
- فهرست کتاب‌ها بر اساس ماه گروه‌بندی شود یا یک فهرست ساده باشد؟
- برای جزوه: آیا کاربر می‌تواند بلوک‌ها را ویرایش، جابه‌جا یا حذف کند، یا
  جزوه فقط خوانده و دانلود می‌شود؟ برای هر کتاب یک جزوه کافی است یا چند
  نسخه؟
- برای کتاب‌های خیلی قطور: کل کتاب یک‌باره به هوش مصنوعی داده شود یا فصل به
  فصل؟ (روی هزینه و زمان اثر دارد)
- خروجی Word و PDF با همان فونت و رنگ‌های `design.md` باشد یا ساده‌تر؟

## Delivery Status (verified facts only)

| Capability | Status | Change name |
| --- | --- | --- |
| Documents aligned + Django/Bootstrap base | built | — (prompt 1) |
| Design system: font, logo, `/design-system/` | built | — (prompt 2) |
| کتابخانه‌ی ماهانه | not built | — |
| آپلود PDF کتاب | not built | — |
| ساخت جزوه با هوش مصنوعی | not built | — |
| خروجی Word و PDF | not built | — |

Update this table only after a step is verified (and, for OpenSpec changes,
archived).
