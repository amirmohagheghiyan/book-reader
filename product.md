# product.md

Approved product context for assistants: the idea and what has actually been
built. It is not approval to build every planned capability; each capability
is built through its own approved OpenSpec change. Prompt 1 filled this file
from the owner's idea; brackets mean «not decided yet».

## Product

- **Name:** جزوه‌ساز
- **One sentence:** «جزوه‌ساز» کتاب‌های تخصصیِ ماهانه‌ی یک دانشجو را یک‌جا
  نگه می‌دارد و پیگیری می‌کند، تا در آینده از هر کتاب قطور یک جزوه‌ی خلاصه و
  تصویری بسازد که خواندنش لذت‌بخش‌تر باشد.
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
  یک‌جا ثبت و دنبال شوند، و در چشم‌انداز محصول، خلاصه و جزوه‌ی تصویری هر
  کتاب به‌جای خواندن کامل آن در دسترس باشد.

## Planned Capabilities (vision, not yet built)

1. **کتابخانه‌ی ماهانه:** کاربر هر کتاب را با نام، نویسنده، ماهِ مطالعه و
   وضعیت («در صف»، «در حال خواندن»، «تمام‌شده») ثبت می‌کند، فهرست کتاب‌ها را
   می‌بیند و هر کتاب را ویرایش یا با تأیید حذف می‌کند.
2. **آپلود کتاب و خلاصه‌سازی خودکار:** کاربر فایل کتاب را بارگذاری می‌کند و
   محصول آن را خلاصه و جزوه‌نویسی می‌کند. این قابلیت به آپلود فایل و اتصال
   به یک سرویس هوش مصنوعی نیاز دارد که هر دو خارج از محدوده‌ی کارگاه
   (`AGENTS.md`) هستند؛ فقط چشم‌انداز است و بدون تصمیم و تأیید صریح کاربر
   برای تغییر محدوده ساخته نمی‌شود.
3. **جزوه‌ی یکپارچه‌ی تصویری:** خلاصه‌ی هر کتاب با نمودار و گراف‌های گرافیکی
   در یک فایل یکپارچه کنار هم قرار می‌گیرد. مانند قابلیت ۲، چشم‌انداز است و
   به تصمیم جداگانه درباره‌ی محدوده نیاز دارد.

Only the first capability is built in the workshop.

## Information the Product Keeps

- **کتاب:** نام، نویسنده، ماهِ مطالعه، وضعیت («در صف»، «در حال خواندن»،
  «تمام‌شده»). جزئیات دقیق فیلدها در OpenSpec change همان قابلیت تصمیم‌گیری
  می‌شود.

## Out of Scope

- Publishing on the internet, user accounts and login, email, payments,
  connecting to other services.
- در نسخه‌ی کارگاه: آپلود فایل کتاب، خلاصه‌سازی خودکار یا هر اتصال به هوش
  مصنوعی، تولید فایل خروجی (مانند PDF)، و استفاده‌ی چند نفر با داده‌ی جدا.

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
- برای قابلیت‌های ۲ و ۳: خروجی نهایی چه شکلی باشد (صفحه‌ی وب، PDF)؟ خلاصه از
  چه سرویسی بیاید؟ این‌ها به تغییر محدوده‌ی `AGENTS.md` نیاز دارند.

## Delivery Status (verified facts only)

| Capability | Status | Change name |
| --- | --- | --- |
| Documents aligned + Django/Bootstrap base | built | — (prompt 1) |
| Design system: font, logo, `/design-system/` | built | — (prompt 2) |
| کتابخانه‌ی ماهانه | not built | — |

Update this table only after a step is verified (and, for OpenSpec changes,
archived).
