from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.rate_limit import InMemoryRateLimiter
from app.routers import auth, users, books, borrows, admin

logger = get_logger(__name__)
settings = get_settings()
auth_rate_limiter = InMemoryRateLimiter(
    limit=settings.auth_rate_limit_requests,
    window_seconds=settings.auth_rate_limit_window_seconds,
)
AUTH_RATE_LIMITED_PATHS = {
    ("POST", "/api/auth/login"),
    ("POST", "/api/auth/register"),
}


def create_scheduler():
    """Initialize and configure the background task scheduler.
    
    Sets up a job to check for overdue books and send notifications
    every day at 9:00 AM.
    """
    from apscheduler.schedulers.background import BackgroundScheduler
    from app.services.borrow_service import BorrowService
    from app.services.notification_service import NotificationService
    from app.repositories.user_repo import UserRepository

    def check_overdue():
        """Check for overdue books and send SMS notifications.
        
        Runs daily at 9:00 AM. Wrapped in try/except to prevent
        scheduler from crashing on transient errors.
        """
        try:
            overdue = BorrowService().overdue_borrows()
            repo = UserRepository()
            svc = NotificationService()
            count = 0
            for borrow in overdue:
                user = repo.find_by_id(borrow.user_id)
                if user:
                    try:
                        svc.send_overdue_sms(user, borrow)
                        count += 1
                    except Exception as e:
                        logger.error(f"Failed to send SMS for user_id={user.id}: {e}")
            logger.info(f"Overdue notification job completed: {count} notifications sent")
        except Exception as e:
            logger.error(f"Overdue notification job failed: {e}", exc_info=True)

    scheduler = BackgroundScheduler()
    scheduler.add_job(check_overdue, "cron", hour=9, minute=0)
    return scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager: startup and shutdown.
    
    On startup:
    - Ensure data directory exists
    - Initialize and start background scheduler
    
    On shutdown:
    - Gracefully shutdown the scheduler
    """
    settings = get_settings()
    settings.validate_security()
    settings.ensure_data_dir()
    logger.info(f"Data directory ready: {settings.data_dir}")
    
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Background scheduler started (overdue check at 09:00 daily)")
    
    yield
    
    scheduler.shutdown()
    logger.info("Background scheduler shut down")


app = FastAPI(
    title="Library Management System",
    version="0.1.0",
    description="OOP library management system with FastAPI, file-based persistence, and audit logging",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):(3000|5173|8080)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def limit_auth_requests(request: Request, call_next):
    route_key = (request.method.upper(), request.url.path)
    if route_key in AUTH_RATE_LIMITED_PATHS:
        forwarded_for = request.headers.get("x-forwarded-for", "")
        client_ip = forwarded_for.split(",", 1)[0].strip()
        if not client_ip and request.client:
            client_ip = request.client.host

        key = f"{client_ip or 'unknown'}:{route_key[0]}:{route_key[1]}"
        allowed, retry_after = auth_rate_limiter.is_allowed(key)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many authentication requests. Please try again later."},
                headers={"Retry-After": str(retry_after)},
            )

    return await call_next(request)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)
app.include_router(borrows.router)
app.include_router(admin.router)

@app.get("/health")
def health():
    return {"status": "ok"}


# Serve frontend files in production and local single-server mode
frontend_path = Path("frontend")
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
