from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import get_settings
from app.core.logger import get_logger
from app.routers import auth, users, books, borrows, admin

logger = get_logger(__name__)


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
                        logger.error(f"Failed to send SMS to {user.email}: {e}")
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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)
app.include_router(borrows.router)
app.include_router(admin.router)

# Serve frontend static files if built
frontend_path = Path("frontend/dist")
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


@app.get("/health")
def health():
    return {"status": "ok"}
