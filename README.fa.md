# مولد کیت برند (Brand Kit Generator)

[![CI](https://github.com/borodayeh/Brand-Kit-Generator/actions/workflows/ci.yml/badge.svg)](https://github.com/borodayeh/Brand-Kit-Generator/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[English](README.md) · **فارسی**

<div dir="rtl">

یک ابزار پایتون بدون هیچ وابستگی خارجی که یک ساختار پوشه‌ای کامل و حرفه‌ای برای
«کیت برند» می‌سازد؛ داخل هر پوشه یک `README.md` دوزبانه (فارسی/انگلیسی) می‌گذارد،
یک رابط خط فرمان کامل دارد و یک رابط وب محلی اختیاری هم ارائه می‌کند.

</div>

```bash
brandkit ./MyBrand --brand Acme --template startup --lang fa --zip
```

---

<div dir="rtl">

## ویژگی‌ها

- **چهار قالب آماده:** `full` (۵۵ پوشه، در سطح آژانس)، `minimal`، `startup` و `agency`.
- **اعلانی:** کل درخت پوشه‌ها در JSON تعریف شده؛ برای سفارشی‌سازی نیازی به تغییر کد نیست.
- **دوزبانگی واقعی:** هم مستندات تولیدشده و هم خودِ ابزار فارسی و انگلیسی صحبت می‌کنند. متن فارسی داخل `<div dir="rtl">` قرار می‌گیرد تا درست راست‌به‌چپ نمایش داده شود.
- **آگاه از نام برند:** با `--brand "Acme"` عبارت `{brand}` در نام پوشه‌ها، عنوان‌ها و توضیحات جایگزین می‌شود.
- **ایمن به‌صورت پیش‌فرض:** فایل‌های موجود هرگز بازنویسی نمی‌شوند مگر با `--force`.
- **مسیرهای محصور:** نام پوشه‌ها پاک‌سازی و اعتبارسنجی می‌شوند؛ یک فایل ساختار خراب یا مخرب نمی‌تواند بیرون از پوشهٔ مقصد بنویسد.
- **چندسکویی:** کاراکترهای غیرمجاز ویندوز، نام‌های رزروشده، نقطه و فاصلهٔ انتهایی و خطر مسیرهای طولانی مدیریت شده‌اند. CI روی لینوکس، ویندوز و مک اجرا می‌شود.
- **امکانات جانبی:** فایل فهرست `MANIFEST.md`، آرشیو `--zip` و `--git-init` با قواعد Git LFS.
- **رابط وب:** با `brandkit --web` یک صفحهٔ دوزبانه و سازگار با RTL باز می‌شود که پیش‌نمایش زندهٔ درخت و دانلود ZIP دارد — همچنان بدون هیچ وابستگی.
- **تست‌شده:** ۹۵ تست pytest به‌همراه ruff، mypy و اعتبارسنجی JSON Schema در CI.

## نصب

</div>

```bash
pip install brand-kit-generator     # پس از انتشار روی PyPI
```

<div dir="rtl">

یا مستقیماً از روی مخزن:

</div>

```bash
git clone https://github.com/borodayeh/Brand-Kit-Generator.git
cd Brand-Kit-Generator
pip install .
```

<div dir="rtl">

اصلاً نمی‌خواهید نصب کنید؟ اسکریپت به‌صورت مستقل هم کار می‌کند:

</div>

```bash
python create_brand_kit.py ./MyBrand
```

<div dir="rtl">

نیازمند **پایتون ۳٫۹ یا بالاتر** و بدون هیچ پکیج جانبی.

## نحوهٔ استفاده

</div>

```bash
# حالت تعاملی: مسیر را می‌پرسد
brandkit

# مستقیم
brandkit ./MyBrand

# کیت استارتاپی برای «Acme»، فقط فارسی، به‌همراه فایل فشرده
brandkit ./MyBrand --brand Acme --template startup --lang fa --zip

# پیش‌نمایش بدون نوشتن روی دیسک
brandkit ./MyBrand --dry-run --verbose

# ساختار سفارشی، بدون فایل نمونه و بدون فهرست
brandkit ./MyBrand --structure my_structure.json --no-samples --no-manifest

# آمادهٔ تحویل: مخزن گیت با قواعد LFS برای فایل‌های باینری
brandkit ./ClientKit --template agency --brand Contoso --git-init

# نمایش قالب‌های آماده
brandkit --list-templates

# رابط وب محلی روی http://localhost:8000
brandkit --web
```

<div dir="rtl">

سه دستور زیر معادل یکدیگرند: `brandkit …` و `python -m brand_kit_generator …`
و `python create_brand_kit.py …`. ابزار را می‌توانید از **هر پوشه‌ای** اجرا کنید.

### گزینه‌ها

| گزینه | توضیح |
|---|---|
| `path` | پوشهٔ مقصد (اگر ندهید پرسیده می‌شود). `~` و متغیرهای محیطی تفسیر می‌شوند. |
| `-t`, `--template NAME` | قالب آماده: `full` (پیش‌فرض)، `minimal`، `startup`، `agency`. |
| `-s`, `--structure FILE` | فایل ساختار سفارشی (بر `--template` اولویت دارد). |
| `-b`, `--brand NAME` | مقداری که جایگزین `{brand}` می‌شود. |
| `-l`, `--lang {fa,en,both}` | زبان مستندات تولیدشده و رابط ابزار. پیش‌فرض: تشخیص خودکار. |
| `-f`, `--force` | بازنویسی فایل‌هایی که از قبل وجود دارند. |
| `-n`, `--dry-run` | نمایش نتیجه بدون نوشتن روی دیسک. |
| `--no-samples` | بدون ساخت فایل‌های نمونه. |
| `--no-manifest` | بدون ساخت `MANIFEST.md`. |
| `-z`, `--zip [FILE]` | ساخت فایل فشرده (نام پیش‌فرض: `<brand>_brand_kit.zip`). |
| `--git-init` | اجرای `git init` در مقصد و افزودن قواعد Git LFS برای فایل‌های باینری. |
| `--list-templates` | نمایش قالب‌های آماده و خروج. |
| `--web` | اجرای رابط وب محلی (`--host` و `--port`). |
| `-v`, `--verbose` / `-q`, `--quiet` | خروجی بیشتر / کمتر. |
| `-V`, `--version` | نمایش نسخه. |

### تشخیص خودکار زبان

اگر `--lang` را ندهید، زبان از اولین متغیر مقداردهی‌شده از میان
`BRANDKIT_LANG`، `LC_ALL`، `LC_MESSAGES` و `LANG` خوانده می‌شود. اگر زبان
مشخصاً فارسی یا انگلیسی نباشد، خروجی **دوزبانه** خواهد بود.

</div>

```bash
BRANDKIT_LANG=fa brandkit ./MyBrand
```

<div dir="rtl">

### کدهای خروج

| کد | معنی |
|---|---|
| `0` | موفقیت |
| `1` | پایان یافت، اما یک یا چند گره با خطا مواجه شد |
| `2` | ورودی نامعتبر (قالب ناشناخته، فایل ساختار ناموجود یا خراب، مسیر خالی) |
| `130` | لغو توسط کاربر (Ctrl-C یا بسته بودن ورودی) |

## قالب‌ها

| نام | تعداد پوشه | مناسبِ |
|---|---|---|
| `full` | ۵۵ | سطح آژانس؛ حقوقی، استراتژی، بصری، موشن، صوت، قالب‌ها، دستورالعمل‌ها و آرشیو |
| `minimal` | ۵ | فریلنسرها و تیم‌های کوچک |
| `startup` | ۱۵ | محصول‌محور: پایه‌های برند، رابط محصول، ورود به بازار، حقوقی |
| `agency` | ۱۹ | تحویل به مشتری: کشف، کانسپت، هویت نهایی، فایل‌های تولید |

</div>

```
Ultimate_Brand_Kit/                      (قالب full)
├── 00_Legal_&_Licensing/                حقوقی و مجوزها
├── 01_Brand_Strategy_&_Verbal_Identity/ استراتژی برند و هویت کلامی
├── 02_Visual_Identity_Core/             هستهٔ هویت بصری
│   ├── 01_Logos/
│   ├── 02_Color_Palettes/
│   ├── 03_Typography/
│   └── 04_Visual_System/
├── 03_Motion_&_Audio_Identity/          هویت متحرک و صوتی
├── 04_Templates_&_Assets/               قالب‌ها و دارایی‌ها
├── 05_Brand_Guidelines/                 دستورالعمل‌های برند
└── 06_Archive_&_Historical_Data/        آرشیو و داده‌های تاریخی
```

<div dir="rtl">

نمونهٔ یک `README.md` تولیدشده با `--lang fa`:

</div>

```markdown
# لوگوی اصلی

<div dir="rtl">

نسخه اصلی و اولیه لوگو.

</div>
```

---

<div dir="rtl">

## رابط وب

</div>

```bash
brandkit --web                      # http://127.0.0.1:8000
brandkit --web --host 0.0.0.0 --port 3000
```

<div dir="rtl">

نام برند، قالب و زبان را انتخاب کنید، درخت پوشه‌ها را به‌صورت زنده ببینید و
سپس کیت را به‌شکل ZIP دانلود کنید. ساخته‌شده روی `http.server` — بدون Flask و
بدون npm.

## سفارشی‌سازی ساختار

هر گره این کلیدها را می‌پذیرد:

| کلید | الزامی | توضیح |
|---|---|---|
| `path` | خیر | نام پوشه روی دیسک. پیش‌فرض: کلید JSON. از `{brand}` پشتیبانی می‌کند. |
| `title_en` / `title_fa` | خیر | عنوان خوانا. پیش‌فرض: نام کلید. |
| `description_en` / `description_fa` | توصیه‌شده | متن اصلی README آن پوشه. |
| `sample_files` | خیر | نام فایل‌های نمونه‌ای که ساخته می‌شوند. |
| `subdirs` | خیر | گره‌های تودرتو با همین قالب. |

بلوک `$meta` در بالاترین سطح (`name_en`، `name_fa`، `default_brand`، `version`)
خودِ قالب را توصیف می‌کند و هنگام ساخت درخت نادیده گرفته می‌شود.

اعتبارسنجی با:

</div>

```bash
python scripts/validate_templates.py
```

<div dir="rtl">

کلیدهای ناشناخته، گره‌هایی که شیء نیستند، نوع نادرست `sample_files` و نام‌هایی
که روی فایل‌سیستم‌های غیرحساس به حروف تداخل دارند، پیش از نوشتن هر چیزی با
پیام روشن رد می‌شوند.

## نکات ایمنی

- **ایدمپوتنت است:** اجرای دوباره پوشه‌های جدید را اضافه می‌کند و به README هایی
  که ویرایش کرده‌اید دست نمی‌زند. `--force` را فقط وقتی بزنید که واقعاً بخواهید
  بازنشانی شوند.
- **بدون فرار از مسیر:** `../`، مسیرهای مطلق و جداکننده‌های داخل نام گره‌ها به یک
  جزء نام ایمن تبدیل می‌شوند و هر مسیر نهایی بررسی می‌شود که داخل مقصد بماند.

## توسعه

</div>

```bash
pip install -e ".[dev]"
ruff check . && mypy && pytest && python scripts/validate_templates.py
```

<div dir="rtl">

فایل‌های [`CONTRIBUTING.md`](CONTRIBUTING.md)، [`CHANGELOG.md`](CHANGELOG.md) و
گزارش بررسی فنی [`REVIEW.md`](REVIEW.md) را هم ببینید.

## انتشار

راهنمای گام‌به‌گام انتشار پروژه روی گیت‌هاب و PyPI در فایل
[`PUBLISHING.fa.md`](PUBLISHING.fa.md) آمده است.

## لایسنس

[MIT](LICENSE) © borodayeh

</div>
