# 🌐 OSINT Toolkit: Professional Kali Linux Terminal Dashboard & Plugin Architecture

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org)
[![Platform](https://img.shields.io/badge/platform-Kali%20Linux%20%7C%20Linux-darkgreen.svg)](https://www.kali.org)
[![UI Framework](https://img.shields.io/badge/UI-Textual-orange.svg)](https://github.com/Textualize/textual)
[![Architecture](https://img.shields.io/badge/Architecture-Clean%20Architecture-brightgreen.svg)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

A professional command-line terminal application and visual dashboard designed for **Kali Linux** and security researchers. This toolkit acts as a central command center for over **30 pre-configured OSINT tools**, organized with a robust plugin-based architecture and a clean Terminal User Interface (TUI).

---

## 🌍 Language Versions / نسخه‌های زبان
- [English](#-english-documentation)
- [فارسی (Persian)](#-راهنمای-فارسی)

---

## 🇬🇧 English Documentation

### ✨ Key Features
- **Centralized OSINT Directory**: Seamlessly access, search, and manage over 30+ top-tier OSINT tools (e.g., *ShadowMap, TGStat, What's My Name, PimEyes, ExifTool, Overpass Turbo*).
- **Beautiful TUI Dashboard**: Built with the modern `Textual` and `Rich` frameworks, providing an interactive, keyboard-navigable dashboard directly inside your Linux terminal.
- **Dynamic Plugin Architecture**: Easily extend the suite by writing your own OSINT tools and scripts, which integrate dynamically as plugins.
- **Advanced Searching**: Fuzzy match and real-time category filtering (Network, Social Media, Geographic, Search, Vulnerability, Data, Web) to locate the precise tool instantly.
- **Reporting System**: Generate comprehensive reports of your target investigations in **HTML**, **JSON**, and **Markdown** formats directly from the terminal.
- **Database-Driven Storage**: Fully backed by `aiosqlite` for asynchronous, resilient storage of tool definitions, active statuses, execution logs, and configurations.
- **Automatic Tool Discovery**: Integrated CLI detector that identifies which local command-line tools (such as `exiftool`) are already installed on your Kali system.

---

### 🏛 Clean Architecture Overview
This repository strictly adheres to **Clean Architecture** principles to separate concerns, improve testability, and ensure scalability:

```
src/osint_toolkit/
│
├── 🌀 domain/              # Enterprise Business Rules & Models
│   ├── models/            # Pure entities: ToolInfo, ToolCategory, ToolStatus, ToolType
│   ├── exceptions/        # Domain-specific error exceptions
│   └── interfaces.py      # Abstract repository definitions
│
├── ⚙️ application/         # Application Business Rules
│   ├── usecases/          # Core workflows: ToolManagement, PluginExecution, ReportGeneration
│   └── services/          # Abstract application helpers (search services, report formatting)
│
├── 🔌 infrastructure/      # Frameworks, Tools & Database Adapters
│   ├── storage/           # SQLite database implementation with aiosqlite
│   ├── plugins/           # Registry, factories, and base classes for extendable plugins
│   ├── parsers/           # Log parsers and data extractors
│   ├── cli_detection/     # Environment & subprocess wrappers to check local tool existence
│   └── di/                # ServiceContainer & dependency injection wire-up
│
└── 🖥 presentation/        # User Interface / Delivery Mechanisms
    ├── tui/               # Textual TUI panels, widgets, CSS style sheets (`osint_toolkit.tcss`)
    └── cli/               # Command-line entrypoints
```

---

### 🚀 Getting Started

#### Prerequisites
- Python `3.11` or higher (Kali Linux default is highly supported)
- Git

#### Installation
1. Clone the repository into your preferred directory:
   ```bash
   git clone https://github.com/yourusername/osint-terminal.git
   cd osint-terminal
   ```

2. Install dependencies in editable mode along with developer tools:
   ```bash
   pip install -e ".[dev]"
   ```

#### Launching the Application
Launch the graphical Textual terminal app with:
```bash
python3 -m osint_toolkit
```

---

### 🔌 Writing Custom Plugins
You can easily extend the dashboard by creating your own plugins under `src/osint_toolkit/infrastructure/plugins/`. Simply inherit from `BasePlugin` and register your new utility:

```python
from osint_toolkit.infrastructure.plugins.base import BasePlugin

class MyCustomOSINTPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="MyTool",
            description="A custom OSINT script targeting unique APIs.",
            # Additional metadata...
        )
```

---

### 🧪 Quality & Tests
Execute the pytest suite to ensure clean, bug-free runs:
```bash
pytest
```
Check static code quality using Ruff:
```bash
ruff check src
```

---

## 🇮🇷 راهنمای فارسی

### 🛠 ابزار جامع اوپن‌سورس اطلاعاتی (OSINT) برای لینوکس کالی
این پروژه یک ابزار ترمینال پیشرفته و داشبورد بصری برای سیستم‌عامل کالی لینوکس است که به منظور مدیریت، جستجو و اجرای یکپارچه بیش از **۳۰ ابزار برتر در حوزه OSINT** طراحی شده است. معماری این برنامه با تکیه بر اصول **Clean Architecture** به صورت ماژولار و مبتنی بر افزونه (Plugin-based) پیاده‌سازی شده است.

---

### ✨ قابلیت‌های کلیدی
- **داشبورد زیبا در ترمینال (TUI)**: طراحی شده با فریم‌ورک‌های مدرن `Textual` و `Rich` جهت ناوبری آسان با کیبورد.
- **معماری افزونه‌محور (Plugin-based)**: قابلیت افزودن آسان اسکریپت‌ها و متدهای اختصاصی شما به عنوان ابزارهای جدید.
- **جستجوی پیشرفته و فازی**: فیلتر کردن هوشمند ابزارها بر اساس دسته‌بندی‌ها (شبکه‌های اجتماعی، جغرافیایی، ایمیل، دیتابیس‌ها، ابزارهای شبکه و تحلیل وب‌سایت).
- **سیستم گزارش‌گیری**: خروجی مستقیم اطلاعات و نتایج بررسی‌ها در قالب فرمت‌های **HTML**، **JSON** و **Markdown**.
- **ذخیره‌سازی بهینه**: پیاده‌سازی دیتابیس غیرهمزمان به صورت امن با کمک `aiosqlite`.
- **شناسایی خودکار ابزارهای محلی**: بررسی خودکار سیستم کالی جهت تشخیص ابزارهای خط فرمان از پیش نصب‌شده (مانند `ExifTool`).

---

### 📂 ساختار معماری پاک (Clean Architecture)
این پروژه بر اساس اصول مهندسی نرم‌افزارUncle Bob پیاده‌سازی شده و از لایه‌های زیر تشکیل گردیده است:
- **لایه دامنه (Domain)**: شامل مدل‌ها، انوم‌ها و موجودیت‌های اصلی برنامه بدون وابستگی بیرونی.
- **لایه کاربرد (Application)**: سناریوها و Use Caseهای اصلی نظیر تولید گزارش، جستجو و اجرای پلاگین‌ها.
- **لایه زیرساخت (Infrastructure)**: درگاه‌های ارتباطی با دیتابیس SQLite، رجیستری پلاگین‌ها و شناسایی خودکار ابزارهای ترمینال.
- **لایه ارائه (Presentation)**: کدهای داشبورد ترمینال و فایل‌های استایل CSS برنامه (`osint_toolkit.tcss`).

---

### 🚀 نحوه راه‌اندازی و اجرا

#### پیش‌نیازها
- پایتون نسخه `۳.۱۱` یا بالاتر
- سیستم‌عامل لینوکس (کالی لینوکس به شدت توصیه می‌شود)

#### نصب و اجرا
۱. مخزن را کلون کنید:
   ```bash
   git clone https://github.com/yourusername/osint-terminal.git
   cd osint-terminal
   ```

۲. نیازمندی‌ها و پکیج‌های توسعه‌دهنده را نصب کنید:
   ```bash
   pip install -e ".[dev]"
   ```

۳. برنامه را اجرا کنید:
   ```bash
   python3 -m osint_toolkit
   ```

---

### 📝 لایسنس و مشارکت
توسعه و بهینه‌سازی این برنامه تحت قوانین مشارکت آزاد انجام می‌شود. خوشحال می‌شویم اگر افزونه‌های جدیدی به بخش پلاگین‌ها اضافه کنید یا کدهای برنامه را بهبود بخشید!
