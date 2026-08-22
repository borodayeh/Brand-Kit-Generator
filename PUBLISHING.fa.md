<div dir="rtl">

# راهنمای انتشار پروژه در گیت‌هاب و PyPI

این سند گام‌به‌گام توضیح می‌دهد چطور نسخهٔ فعلی (`3.0.0`) را روی گیت‌هاب منتشر
کنید. همهٔ دستورها را در ریشهٔ مخزن اجرا کنید.

---

## گام ۰ — پیش از هر چیز: بررسی محلی

</div>

```bash
python -m venv .venv && source .venv/bin/activate   # ویندوز: .venv\Scripts\activate
pip install -e ".[dev]"

ruff check .                            # لینت
mypy                                    # بررسی نوع
pytest                                  # ۹۵ تست
python scripts/validate_templates.py    # اعتبارسنجی قالب‌ها
```

<div dir="rtl">

اگر هر چهار مورد سبز بود، آمادهٔ انتشارید.

---

## گام ۱ — ادغام شاخهٔ کاری در `main`

کارها روی شاخهٔ `arena/01a0298e-brand-kit-generator` انجام شده و روی گیت‌هاب
پوش شده است. یک Pull Request بسازید:

</div>

```bash
gh pr create \
  --base main \
  --head arena/01a0298e-brand-kit-generator \
  --title "v3.0.0 — bug fixes, bilingual CLI, templates, web UI, tests & CI" \
  --body-file CHANGELOG.md
```

<div dir="rtl">

یا از رابط وب: در صفحهٔ مخزن، بنر «Compare & pull request» را بزنید.

سپس ادغام کنید:

</div>

```bash
gh pr merge --squash --delete-branch
git checkout main && git pull
```

<div dir="rtl">

---

## گام ۲ — فعال‌سازی GitHub Actions

ورک‌فلوها از قبل در مسیر درست `.github/workflows/` قرار دارند، پس با اولین پوش
به‌صورت خودکار اجرا می‌شوند. در تب **Actions** مخزن باید اجرای CI را ببینید:
لینت، بررسی نوع، تست روی لینوکس/ویندوز/مک و پایتون ۳٫۹ تا ۳٫۱۳، و ساخت بستهٔ
توزیع.

> اگر تب Actions غیرفعال بود: **Settings → Actions → General → Allow all actions**.

---

## گام ۳ — تنظیمات ظاهری مخزن

این کارها دیده‌شدن پروژه را چند برابر می‌کند:

</div>

```bash
gh repo edit \
  --description "Generate a complete, bilingual (fa/en) brand kit folder structure — CLI + web UI, zero dependencies" \
  --homepage "https://github.com/borodayeh/Brand-Kit-Generator" \
  --add-topic brand-identity \
  --add-topic branding \
  --add-topic cli \
  --add-topic python \
  --add-topic scaffolding \
  --add-topic bilingual \
  --add-topic persian \
  --add-topic rtl \
  --add-topic design-tools
```

<div dir="rtl">

همچنین در **Settings** این‌ها را روشن کنید:

- **Issues** و **Discussions** (برای بازخورد کاربران)
- **Settings → Branches → Add rule** روی `main`: الزام سبز بودن CI پیش از ادغام
- در صفحهٔ اصلی مخزن، بخش **About** را با توضیح و تاپیک‌ها پر کنید

---

## گام ۴ — ساخت تگ و Release

نسخه در `pyproject.toml` و `brand_kit_generator/cli.py` روی `3.0.0` تنظیم شده
است. تگ بزنید و Release بسازید:

</div>

```bash
git tag -a v3.0.0 -m "v3.0.0"
git push origin v3.0.0

gh release create v3.0.0 \
  --title "v3.0.0 — Bilingual CLI, templates & web UI" \
  --notes "$(sed -n '/## \[3.0.0\]/,/## \[2.0.0\]/p' CHANGELOG.md | head -n -1)"
```

<div dir="rtl">

اگر می‌خواهید فایل ZIP آماده هم پیوست کنید:

</div>

```bash
brandkit ./release-demo --brand Demo --template full --zip demo_brand_kit.zip
gh release upload v3.0.0 demo_brand_kit.zip
```

<div dir="rtl">

---

## گام ۵ — انتشار روی PyPI (اختیاری اما توصیه‌شده)

با انجام این گام، هر کسی می‌تواند با `pip install brand-kit-generator` ابزار
شما را نصب کند.

### ۵-۱ روش خودکار و امن (توصیه‌شده)

فایل `publish.yml` از **Trusted Publishing** استفاده می‌کند؛ یعنی هیچ توکنی در
مخزن ذخیره نمی‌شود.

۱. در [pypi.org](https://pypi.org) حساب بسازید و 2FA را فعال کنید.
۲. به **Your projects → Publishing → Add a pending publisher** بروید و پر کنید:

| فیلد | مقدار |
|---|---|
| PyPI Project Name | `brand-kit-generator` |
| Owner | `borodayeh` |
| Repository name | `Brand-Kit-Generator` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

۳. در گیت‌هاب: **Settings → Environments → New environment** با نام `pypi`.
۴. تمام. از این پس هر Release جدید، به‌صورت خودکار روی PyPI منتشر می‌شود.

### ۵-۲ روش دستی

</div>

```bash
pip install build twine
python -m build                 # dist/*.whl و dist/*.tar.gz را می‌سازد
twine check dist/*

# اول روی TestPyPI امتحان کنید:
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ brand-kit-generator

# وقتی مطمئن شدید:
twine upload dist/*
```

<div dir="rtl">

> برای انتشار نسخه‌های بعدی، شمارهٔ نسخه را **هم** در `pyproject.toml` و **هم**
> در `__version__` داخل `brand_kit_generator/cli.py` به‌روز کنید و یک بخش تازه
> به `CHANGELOG.md` اضافه کنید.

---

## گام ۶ — معرفی پروژه (اختیاری)

- در README یک GIF یا اسکرین‌شات از رابط وب اضافه کنید (بیشترین تأثیر را دارد).
- پروژه را در Product Hunt، Reddit (r/Python، r/graphic_design)، لینکدین و
  ویرگول معرفی کنید — به‌خاطر دوزبانه بودن، برای جامعهٔ طراحان ایرانی جذاب است.
- در فایل README گیت‌هاب پروفایل شخصی‌تان به آن لینک بدهید.

---

## چک‌لیست نهایی

- [ ] `ruff`، `mypy`، `pytest` و اعتبارسنجی قالب‌ها سبز هستند
- [ ] PR ادغام شده و `main` به‌روز است
- [ ] CI در تب Actions سبز است
- [ ] توضیح، هوم‌پیج و تاپیک‌های مخزن تنظیم شده‌اند
- [ ] تگ `v3.0.0` و Release ساخته شده است
- [ ] (اختیاری) بسته روی PyPI منتشر شده و `pip install brand-kit-generator` کار می‌کند
- [ ] لینک PyPI و بج نسخه به README اضافه شده است

</div>
