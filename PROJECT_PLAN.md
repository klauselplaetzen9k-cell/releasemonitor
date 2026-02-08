# Release Monitor - Project Plan

## Overview
A release monitoring and changelog aggregation tool similar to **Release monitoring platform** that tracks software releases across multiple sources (GitHub, GitLab, npm, PyPI, Docker Hub, etc.) and provides unified release feeds with changelog summaries.

## Tech Stack
| Component | Technology |
|-----------|------------|
| **Database** | MariaDB 11.x |
| **Backend** | Python 3.12 + FastAPI |
| **ORM** | SQLAlchemy 2.0 |
| **Frontend** | React 18 + Vite + TypeScript |
| **Containerization** | Docker + Docker Compose |
| **API Documentation** | OpenAPI/Swagger |

## Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      Release Monitor                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   MariaDB   │    │   Backend   │    │   Frontend  │     │
│  │   (port     │    │  (port     │    │  (Nginx)    │     │
│  │   3306)     │◄──►│   8000)    │◄──►│   (port 80) │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                                   │
│         │                  ▼                                   │
│         │         ┌─────────────┐                              │
│         │         │   Celery    │  (Async task queue)         │
│         │         │  Workers    │                              │
│         │         └─────────────┘                              │
│         │                  │                                   │
│         │                  ▼                                   │
│         │         ┌─────────────┐                              │
│         │         │   Redis     │  (Broker & Cache)            │
│         │         │  (port 6379)│                              │
│         │         └─────────────┘                              │
│         │                                                     │
│         ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐      │
│  │              Release Sources                          │      │
│  │  GitHub, GitLab, npm, PyPI, Docker Hub, Crates.io   │      │
│  └─────────────────────────────────────────────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema (MariaDB)

### Core Tables

#### `projects` - Monitored software projects
| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT | Primary key |
| name | VARCHAR(255) | Project name |
| source | ENUM | github, gitlab, npm, pypi, docker, crates |
| external_id | VARCHAR(255) | External ID from source |
| repo_url | VARCHAR(500) | Repository URL |
| description | TEXT | Project description |
| avatar_url | VARCHAR(500) | Project avatar |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |

#### `releases` - Release entries
| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT | Primary key |
| project_id | INT FK | Reference to project |
| version | VARCHAR(100) | Semantic version |
| release_date | DATETIME | Release date |
| changelog | LONGTEXT | Full changelog (markdown) |
| changelog_url | VARCHAR(500) | URL to changelog |
| tag_name | VARCHAR(255) | Git tag name |
| draft | BOOLEAN | Is draft release |
| prerelease | BOOLEAN | Is prerelease |
| created_at | DATETIME | Creation timestamp |

#### `release_assets` - Downloadable assets
| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT | Primary key |
| release_id | INT FK | Reference to release |
| name | VARCHAR(255) | Asset name |
| download_url | VARCHAR(500) | Asset download URL |
| size | BIGINT | File size in bytes |
| content_type | VARCHAR(100) | MIME type |

#### `users` - User accounts
| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT | Primary key |
| email | VARCHAR(255) UNIQUE | User email |
| password_hash | VARCHAR(255) | bcrypt hash |
| first_name | VARCHAR(100) | First name |
| last_name | VARCHAR(100) | Last name |
| is_active | BOOLEAN | Account active status |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |

#### `subscriptions` - User subscriptions to projects
| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT | Primary key |
| user_id | INT FK | Reference to user |
| project_id | INT FK | Reference to project |
| notify_email | BOOLEAN | Email notifications |
| notify_webhook | BOOLEAN | Webhook notifications |
| webhook_url | VARCHAR(500) | Webhook endpoint |
| created_at | DATETIME | Creation timestamp |

#### `webhooks` - Outbound webhook deliveries
| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT | Primary key |
| subscription_id | INT FK | Reference to subscription |
| event_type | VARCHAR(50) | release, prerelease, asset |
| payload | JSON | Webhook payload |
| status | ENUM | pending, sent, failed |
| attempts | INT | Number of delivery attempts |
| last_attempt_at | DATETIME | Last attempt timestamp |
| error_message | TEXT | Error if failed |

## Features

### Phase 1 - Core Features (MVP)
| # | Feature | Description |
|---|---------|-------------|
| 1 | **Project Management** | Add/remove projects from various sources |
| 2 | **Release Tracking** | Automatically fetch releases from configured sources |
| 3 | **Release Feed** | Unified chronological feed of all releases |
| 4 | **Changelog Display** | Render changelogs in markdown |
| 5 | **Search & Filter** | Search projects, filter by source/type |
| 6 | **User Registration** | Create accounts |
| 7 | **Project Subscriptions** | Subscribe to project releases |
| 8 | **Email Notifications** | Email alerts for new releases |

### Phase 2 - Enhanced Features
| # | Feature | Description |
|---|---------|-------------|
| 9 | **Webhook Notifications** | HTTP callbacks for integrations |
| 10 | **Release Diff** | Compare versions/changelogs |
| 11 | **RSS/Atom Feeds** | Standard feed formats |
| 12 | **Slack/Discord Integration** | Bot notifications |
| 13 | **Statistics Dashboard** | Release frequency charts |
| 14 | **API Access** | Public API for release data |
| 15 | **Rate Limiting** | API rate limits |

### Phase 3 - Advanced Features
| # | Feature | Description |
|---|---------|-------------|
| 16 | **AI Summarization** | LLM-powered changelog summaries |
| 17 | **Categories/Tags** | Organize projects |
| 18 | **Dependency Tracking** | Alert when dependencies update |
| 19 | **Security Advisories** | Link to CVE databases |
| 20 | **Team Workspaces** | Multi-tenant organization |

## API Endpoints (FastAPI)

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login |
| POST | /api/auth/refresh | Refresh token |
| POST | /api/auth/logout | Logout |
| GET | /api/auth/me | Current user |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/projects | List projects |
| POST | /api/projects | Add project |
| GET | /api/projects/{id} | Get project |
| PUT | /api/projects/{id} | Update project |
| DELETE | /api/projects/{id} | Remove project |
| GET | /api/projects/search | Search projects |
| GET | /api/projects/sources | List sources |

### Releases
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/releases | List releases |
| GET | /api/releases/{id} | Get release |
| GET | /api/projects/{id}/releases | Project releases |
| GET | /api/releases/feed | RSS/Atom feed |

### Subscriptions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/subscriptions | User subscriptions |
| POST | /api/subscriptions | Subscribe to project |
| DELETE | /api/subscriptions/{id} | Unsubscribe |
| PUT | /api/subscriptions/{id} | Update settings |

### Webhooks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/webhooks/{uuid} | Receive webhook |

## Release Sources Integration

### Supported Sources
| Source | API | Rate Limit |
|--------|-----|------------|
| GitHub | REST + GraphQL | 5000/hr |
| GitLab | REST | 3600/hr |
| npm | Registry API | Unlimited |
| PyPI | JSON API | Unlimited |
| Docker Hub | Registry API | 200/hr |
| Crates.io | JSON API | Unlimited |
| Maven Central | Metadata API | Unlimited |

### Source Adapters Pattern
```python
class ReleaseSource(ABC):
    @abstractmethod
    async def get_releases(self, project_id: str) -> List[Release]:
        """Fetch releases from source"""
    
    @abstractmethod
    async def parse_release(self, raw_data: dict) -> Release:
        """Parse raw data to Release model"""
```

## Docker Compose Configuration

```yaml
version: '3.8'

services:
  mariadb:
    image: mariadb:11.4
    container_name: releasemonitor-db
    environment:
      MARIADB_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MARIADB_DATABASE: releasemonitor
      MARIADB_USER: ${DB_USER}
      MARIADB_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mariadb_data:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - releasemonitor-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: releasemonitor-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - releasemonitor-network
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: releasemonitor-backend
    environment:
      DATABASE_URL: mariadb+pymysql://${DB_USER}:${DB_PASSWORD}@mariadb:3306/releasemonitor
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      ALGORITHM: ${ALGORITHM}
      ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES}
      SMTP_HOST: ${SMTP_HOST}
      SMTP_PORT: ${SMTP_PORT}
      SMTP_USER: ${SMTP_USER}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
    ports:
      - "8000:8000"
    depends_on:
      mariadb:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - uploads_data:/app/uploads
    networks:
      - releasemonitor-network
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: releasemonitor-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - releasemonitor-network
    restart: unless-stopped

volumes:
  mariadb_data:
  redis_data:
  uploads_data:

networks:
  releasemonitor-network:
    driver: bridge
```

## Implementation Timeline

### Week 1 - Foundation
| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Project setup, Docker Compose | Running containers |
| 2 | Database models (SQLAlchemy) | ORM models |
| 3 | Auth system (JWT) | Login/Register APIs |
| 4 | Project CRUD + GitHub source | Add/list projects |
| 5 | Release fetching + display | Release feed |

### Week 2 - Core Features
| Day | Task | Deliverable |
|-----|------|-------------|
| 6 | Additional sources (npm, PyPI) | Multi-source support |
| 7 | Search & filtering | Search APIs |
| 8 | User subscriptions | Subscribe feature |
| 9 | Email notifications | SMTP integration |
| 10 | Frontend - Project list | React project page |

### Week 3 - Frontend + Polish
| Day | Task | Deliverable |
|-----|------|-------------|
| 11 | Frontend - Release detail | Release view |
| 12 | Frontend - User settings | Settings page |
| 13 | Frontend - Responsive design | Mobile support |
| 14 | Testing + Bug fixes | Stable release |

### Week 4 - Advanced Features
| Day | Task | Deliverable |
|-----|------|-------------|
| 15 | Webhook notifications | Webhook system |
| 16 | RSS/Atom feeds | Feed endpoints |
| 17 | Statistics dashboard | Charts |
| 18 | API documentation | Swagger UI |
| 19 | Deployment script | Production setup |

## Development Setup

### Prerequisites
- Docker 24+
- Docker Compose 2.20+
- Python 3.12 (for local dev)
- Node.js 20+ (for local dev)

### Quick Start
```bash
# Clone repository
git clone https://github.com/yourusername/releasemonitor.git
cd releasemonitor

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost
# API: http://localhost:8000/api
# API Docs: http://localhost:8000/docs
```

### Local Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Environment Variables

```env
# Database
DB_ROOT_PASSWORD=your_root_password
DB_USER=releasemonitor
DB_PASSWORD=your_db_password
DATABASE_URL=mariadb+pymysql://releasemonitor:your_db_password@mariadb:3306/releasemonitor

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (SMTP)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_smtp_user
SMTP_PASSWORD=your_smtp_password

# GitHub (for release fetching)
GITHUB_TOKEN=your_github_token

# Frontend URL
FRONTEND_URL=http://localhost
```

## File Structure
```
releasemonitor/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── releases.py
│   │   │   └── subscriptions.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   └── release.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   └── release.py
│   │   ├── services/
│   │   │   ├── sources/
│   │   │   │   ├── github.py
│   │   │   │   ├── npm.py
│   │   │   │   └── pypi.py
│   │   │   ├── fetcher.py
│   │   │   └── notifications.py
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── utils/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Estimated Effort
| Phase | Features | Effort |
|-------|----------|--------|
| Phase 1 | Core features (1-8) | 2 weeks |
| Phase 2 | Enhanced features (9-15) | 2 weeks |
| Phase 3 | Advanced features (16-20) | 2 weeks |
| **Total** | **All 20 features** | **6 weeks** |

## Next Steps
1. ✅ Project plan created
2. ⬜ Initialize repository with backend/frontend structure
3. ⬜ Set up Docker Compose with MariaDB, Redis
4. ⬜ Implement backend with FastAPI
5. ⬜ Build frontend with React
6. ⬜ Deploy to staging

---
**Created:** 2026-02-08
**Status:** Ready for implementation
