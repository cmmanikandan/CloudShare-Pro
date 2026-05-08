# 🚀 CloudShare Pro

**CloudShare Pro** is a modern, minimalist, and high-performance SaaS platform for secure and instant file sharing. Built with a clean "Linear/Notion" inspired light theme, it offers professional tools for individuals and teams to move files across the globe in seconds.

![CloudShare Pro Banner](https://images.unsplash.com/photo-1614850523296-e8c1d4704a96?auto=format&fit=crop&w=1200&q=80)

## ✨ Features

-   **💎 Minimalist UI**: Clean, light-themed interface designed for focus and speed.
-   **🔒 Secure Sharing**: Password protection and auto-expiry dates for all shares.
*   **📂 Multi-file Support**: Batch upload and share multiple files with a single link.
*   **📲 Instant mobile Access**: Built-in QR code generator for seamless cross-device transfers.
*   **🤖 AI Telegram Bot**: Integrated bot for real-time notifications, file management, and AI-powered support.
*   **📧 Email Integration**: Professional HTML email templates for sharing files directly from the dashboard.
*   **⚡ P2P Transfer**: Direct browser-to-browser transfers for maximum privacy and unlimited size.
*   **📊 Pro Analytics**: Track downloads and storage usage with a clean, modern dashboard.

## 🛠️ Tech Stack

-   **Backend**: Flask (Python 3.11+)
-   **Database**: SQLAlchemy (SQLite/PostgreSQL/MySQL)
-   **Storage**: Cloudinary API
-   **Bot Engine**: python-telegram-bot (v20+)
-   **Mail**: Flask-Mail (SMTP)
-   **Frontend**: Tailwind CSS, Bootstrap Icons, GSAP
-   **Deployment**: Docker & Docker Compose

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/cmmanikandan/CloudShare-Pro.git
cd CloudShare-Pro
```

### 2. Configure Environment
Create a `.env` file in the root directory:
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
```

### 3. Deploy with Docker
```bash
docker-compose up --build -d
```

## 📈 Dashboard

The platform includes a comprehensive **Admin Panel** and **User Dashboard** to manage your files, monitor system health, and track sharing activity in real-time.

---

Built with ❤️ by [CloudShare Pro Team]
