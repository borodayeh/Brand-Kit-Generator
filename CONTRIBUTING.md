# Contributing / راهنمای مشارکت

Thanks for helping improve Brand Kit Generator!
از اینکه به بهبود این پروژه کمک می‌کنید سپاسگزاریم.

## Development setup

```bash
git clone https://github.com/borodayeh/Brand-Kit-Generator.git
cd Brand-Kit-Generator
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Before opening a pull request

```bash
ruff check .                          # lint
mypy                                  # type check
pytest                                # tests
python scripts/validate_templates.py  # templates vs JSON schema
```

All four must pass; CI runs them on Linux, Windows and macOS with Python
3.9 – 3.13.

## Adding or editing a template

1. Drop a new file in `brand_kit_generator/templates/<name>.json`.
2. Include a `$meta` block with `name_en`, `name_fa` and `default_brand`.
3. Every node needs **all four** of `title_en`, `title_fa`,
   `description_en`, `description_fa` — the bilingual test enforces this.
4. Use `{brand}` where the brand name belongs.
5. Run `python scripts/validate_templates.py`.

## Style

- Python: 4 spaces, ≤ 100 columns, type hints on public functions, ruff-clean.
- Every user-facing string goes into `MESSAGES` with both `en` and `fa`.
- Persian text in generated Markdown must be wrapped in `<div dir="rtl">`.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).

## Reporting bugs

Open an issue with your OS, Python version, the exact command you ran and the
full output. `--verbose` output is especially helpful.

---

<div dir="rtl">

## نکات مهم برای مشارکت‌کنندگان فارسی‌زبان

- هر رشتهٔ متنی که به کاربر نمایش داده می‌شود باید در دیکشنری `MESSAGES` هم
  نسخهٔ انگلیسی و هم نسخهٔ فارسی داشته باشد.
- متن فارسی در فایل‌های مارک‌داون تولیدشده باید داخل `<div dir="rtl">` قرار
  بگیرد تا درست نمایش داده شود.
- در قالب‌ها هر گره باید هر چهار کلید `title_en`، `title_fa`،
  `description_en` و `description_fa` را داشته باشد؛ تست خودکار این را بررسی
  می‌کند.
- پیش از ارسال PR، چهار دستور بالا (ruff، mypy، pytest و اعتبارسنجی قالب‌ها)
  را اجرا کنید.

</div>
