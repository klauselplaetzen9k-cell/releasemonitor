from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import auth_router, projects_router, releases_router, subscriptions_router
from app.api.admin import router as admin_router
from app.api.webhooks import router as webhooks_router
from app.api.feeds import router as feeds_router
from app.api.categories import router as categories_router
from app.api.teams import router as teams_router
from app.core.database import engine

settings = get_settings()

app = FastAPI(
    title="Release Monitor API",
    description="Track releases from GitHub, GitLab, npm, PyPI, Docker Hub, and more",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(releases_router, prefix="/api")
app.include_router(subscriptions_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(webhooks_router, prefix="/api")
app.include_router(feeds_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(teams_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    from app.core.database import Base
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    from app.services.email import init_email_service, email_service
    init_email_service()
    print(f"[Startup] Email service: {'Enabled' if email_service.is_configured() else 'Disabled (no SMTP config)'}")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "name": "Release Monitor API",
        "version": "1.0.0",
        "docs": "/docs"
    }
