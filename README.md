# Release Monitor 🚀

A release monitoring and changelog aggregation platform that tracks software releases across multiple sources (GitHub, GitLab, npm, PyPI, Docker Hub, and more) with unified release feeds and notifications.

---

## ⚡ Status: Phase 1 In Progress

### ✅ Completed (Phase 1)
- [x] Project structure (backend + frontend)
- [x] FastAPI backend with SQLAlchemy models
- [x] MariaDB database schema
- [x] JWT Authentication (login/register)
- [x] Projects CRUD API
- [x] Releases API with feed endpoint
- [x] Subscriptions API
- [x] React frontend with Vite + TypeScript
- [x] Login/Register pages
- [x] Dashboard with release feed
- [x] Projects listing and detail views
- [x] Docker Compose with MariaDB, Redis, Backend, Frontend

### ⏳ In Progress
- Release fetching from external sources (GitHub, npm, PyPI)
- Email notifications

### 📋 Upcoming (Phase 2+)
- Webhook notifications
- RSS/Atom feeds
- Release comparison
- Statistics dashboard

---

## ⚡ Quick Start

### Prerequisites
- Docker 24+
- Docker Compose 2.20+

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/releasemonitor.git
cd releasemonitor

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d --build

# Access the application
# Frontend: http://localhost
# API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Manual Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
releasemonitor/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/           # API routes
│   │   │   ├── auth.py    # Authentication
│   │   │   ├── projects.py # Project management
│   │   │   ├── releases.py # Release tracking
│   │   │   └── subscriptions.py
│   │   ├── core/          # Core configuration
│   │   │   ├── config.py  # Settings
│   │   │   ├── security.py # JWT auth
│   │   │   └── database.py # SQLAlchemy
│   │   ├── models/        # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── release.py
│   │   │   └── subscription.py
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── ProjectsPage.tsx
│   │   │   ├── ProjectDetailPage.tsx
│   │   │   └── SettingsPage.tsx
│   │   ├── hooks/        # Custom hooks
│   │   └── App.tsx
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

### Environment Variables

```env
# Database
DB_ROOT_PASSWORD=changeme
DB_PASSWORD=password

# Security
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (SMTP) - Optional
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=

# GitHub Token - Optional
GITHUB_TOKEN=

# Frontend URL
FRONTEND_URL=http://localhost:80
```

## 📚 API Documentation

Once running, visit: http://localhost:8000/docs

### Key Endpoints

**Authentication:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (returns JWT)
- `GET /api/auth/me` - Get current user

**Projects:**
- `GET /api/projects` - List projects
- `POST /api/projects` - Add project
- `GET /api/projects/{id}` - Get project details
- `DELETE /api/projects/{id}` - Remove project

**Releases:**
- `GET /api/releases` - List releases
- `GET /api/releases/feed` - Unified feed for subscribed projects
- `GET /api/releases/project/{id}` - Project releases

**Subscriptions:**
- `GET /api/subscriptions` - User subscriptions
- `POST /api/subscriptions` - Subscribe to project
- `DELETE /api/subscriptions/{id}` - Unsubscribe

## 🗄️ Database Schema

### Core Tables
- `users` - User accounts
- `projects` - Monitored software projects
- `releases` - Release entries
- `release_assets` - Downloadable assets
- `subscriptions` - User subscriptions

## 🚀 Tech Stack

| Component | Technology |
|-----------|------------|
| **Database** | MariaDB 11.x |
| **Backend** | Python 3.12 + FastAPI |
| **Frontend** | React 18 + Vite + TypeScript |
| **Cache** | Redis 7 |
| **Containerization** | Docker + Docker Compose |

## 📝 License

MIT License

---

**Status:** Building Phase 1 Core Features | **Last Updated:** 2026-02-08
