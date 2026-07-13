# OSINT Terminal | ترمینال اوسینت

A Clean Architecture CLI and Textual TUI dashboard for personal OSINT tool collections in Kali Linux.
یک داشبورد مبتنی بر ترمینال و رابط گرافیکی متنی (TUI) با معماری پاک (Clean Architecture) برای مدیریت ابزارهای اوسینت در کالی لینوکس.

---

## 🌐 زبان‌ها / Languages
- [Persian (فارسی)](#farsi)
- [English](#english)

---

<a name="farsi"></a>
## 🇮🇷 راهنمای فارسی

این پروژه یک برنامه تحت ترمینال برای کالی لینوکس است که یک مجموعه ابزار اوسینت شخصی شامل ۲۰ دسته‌بندی و بیش از ۲۸۰ ابزار مختلف را به یک داشبورد زیبا، قابل جستجو و پلاگین‌محور تبدیل می‌کند. ساختار پروژه به گونه‌ای طراحی شده است که تا بیش از ۵۰۰ پلاگین را به سادگی و بدون تغییر در هسته برنامه پشتیبانی کند.

منبع اصلی داده‌ها فایل `osint_tools.md` است که کاتالوگ ابزارها را مشخص می‌کند و تمامی متادیتاهای پلاگین‌ها از آن استخراج می‌شوند.

### 🏗️ معماری پروژه (Clean Architecture)

ساختار کد در پوشه `src/osint_terminal/` به چهار لایه اصلی تقسیم می‌شود:

```
src/osint_terminal/
├── domain/           # اینتیتی‌ها، انوم‌ها و پورت‌ها (اینترفیس‌ها) - بدون وابستگی خارجی
├── application/      # یوزکیس‌ها و سرویس‌ها: جستجو، دیسکاوری، اجرا و گزارش‌گیری
├── infrastructure/   # دیتابیس SQLite، بررسی‌کننده دسترسی CLI، کانتینر DI و ایندکس فازی
├── presentation/     # رابط کاربری متنی Textual: داشبورد، پالت دستورات و کلیدهای میانبر
└── plugins/          # پلاگین‌های تولید شده از روی osint_tools.md به تفکیک دسته‌بندی
```

#### قانون وابستگی (Dependency Rule)
وابستگی‌ها فقط به سمت داخل هستند:
`presentation → application → domain` و `infrastructure → domain`.
پلاگین‌ها در مسیر `plugins/*` پروتکل `domain.ports.Plugin` را پیاده‌سازی کرده و به طور پویا بارگذاری می‌شوند.

---

### 🗺️ نقشه راه توسعه (Module Roadmap)

این پروژه به صورت ماژولار و مرحله به مرحله توسعه می‌یابد:

| # | ماژول | وضعیت |
|---|--------|--------|
| ۱ | لایه دامنه (Domain) — اینتیتی‌ها، انوم‌ها، پورت‌ها و اکسپشن‌ها | ✅ تکمیل شده |
| ۲ | زیرساخت (Infrastructure): ریپازیتوری SQLite و کانتینر DI | ⏳ در حال توسعه |
| ۳ | زیرساخت (Infrastructure): بررسی‌کننده CLI و شاخص جستجوی فازی | در انتظار |
| ۴ | استخراج کاتالوگ OSINT از روی `osint_tools.md` | در انتظار |
| ۵ | کلاس‌های پایه پلاگین‌ها بر اساس نوع ابزار (CLI/Online/API) | در انتظار |
| ۶ | ژنراتور پلاگین‌ها (تبدیل کاتالوگ به بیش از ۲۸۰ پلاگین مستقل) | در انتظار |
| ۷ | لایه کاربردی (Application) — یوزکیس‌ها و مدیریت تاریخچه و علاقه‌مندی‌ها | در انتظار |
| ۸ | گزارش‌گیری — خروجی‌های JSON، Markdown و HTML | در انتظار |
| ۹ | لایه نمایش (Presentation) — طراحی داشبورد با Textual و کلیدهای میانبر | در انتظار |
| ۱۰ | راه‌اندازی و تست‌های دود (Smoke Tests) | در انتظار |

---

### 🚀 توسعه و تست‌ها

برای راه‌اندازی محیط توسعه و اجرای تست‌ها دستورات زیر را اجرا کنید:

```bash
# ایجاد محیط مجازی و نصب وابستگی‌ها
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# اجرای تست‌ها
pytest -q

# بررسی استاتیک کد و Type Checking
mypy src/osint_terminal/domain
ruff check src
```

---

<a name="english"></a>
## 🇬🇧 English Guide

**OSINT Terminal** is a terminal-based dashboard application for Kali Linux that structures a personal collection of OSINT tools (derived from `osint_tools.md`, featuring 20 categories and ~280 distinct tools) into a searchable, plugin-based CLI and TUI dashboard. It is engineered to scale to 500+ plugins seamlessly.

The single source of truth is **`osint_tools.md`**. Every plugin's metadata is generated directly from this file.

### 🏗️ Architecture (Clean Architecture, 4 layers)

```
src/osint_terminal/
├── domain/           # Entities, enums, ports (interfaces). Zero external dependencies.
├── application/      # Use cases / services: search, discovery, execution, reporting.
├── infrastructure/    # SQLite repo, CLI availability checker, DI container, fuzzy index.
├── presentation/      # Textual TUI: dashboard, command palette, keyboard shortcuts.
└── plugins/            # Generated plugins, grouped by category.
```

- **Dependency Rule:** Arrows point inward only. High-level policies do not depend on low-level details.
- **Plugin Contract:** All plugins implement `domain.ports.Plugin` protocol and are loaded via dynamic discovery (`domain.ports.PluginDiscovery`), allowing the catalog to scale without modifying core code.

---

### 🗺️ Module Roadmap

| # | Module | Status |
|---|--------|--------|
| 1 | Domain layer — entities, enums, ports, exceptions | ✅ Done |
| 2 | Infrastructure: SQLite repository + DI container | ⏳ Next |
| 3 | Infrastructure: CLI availability checker + fuzzy search index (rapidfuzz) | Pending |
| 4 | OSINT catalogue extraction — structured JSON/YAML parsed from `osint_tools.md` | Pending |
| 5 | Plugin base classes per `ToolType` (CLI / online / API / framework) + output parsers | Pending |
| 6 | Plugin generator — turns the catalogue into ~280+ individual plugin modules | Pending |
| 7 | Application layer — use cases: list/search/run plugins, favorites, history | Pending |
| 8 | Reporting — JSON / Markdown / HTML exporters | Pending |
| 9 | Presentation — Textual dashboard, fuzzy search UI, command palette, keybindings | Pending |
| 10 | Wiring — `main.py`, DI composition root, packaging, smoke tests | Pending |

---

### 🚀 Development & Testing

Setting up the project and running tests:

```bash
# Set up a virtual environment and install dev dependencies
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest -q

# Code quality checks
mypy src/osint_terminal/domain
ruff check src
```
