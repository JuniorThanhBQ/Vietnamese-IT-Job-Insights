import os
import sys
from celery import Celery

# Add backend and root directories to path so we can import app modules and crawler modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# pylint: disable=wrong-import-position
from celery.schedules import crontab
from backend.app.config import settings


celery_app = Celery(
    "crawler",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["crawler.tasks"],
)

# Apply strict memory limits and other optimizations for low-spec developer environment
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    # Enforce strict memory limits for child processes to prevent memory leaks from Playwright/Chromium
    worker_max_memory_per_child=250000,  # 250MB in KB
    worker_max_tasks_per_child=10,
    worker_prefetch_multiplier=1,
)

# Celery Beat scheduler configuration
celery_app.conf.beat_schedule = {
    "crawl-jobs-every-night": {
        "task": "crawler.tasks.crawl_all_task",
        "schedule": crontab(hour=2, minute=0),
        "args": (5,),
    },
}


if __name__ == "__main__":
    celery_app.start()
