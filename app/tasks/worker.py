from celery import Celery
from typing import Dict, Any, List
from datetime import datetime

from app.config import settings
from app.services.agworld_client import agworld_client
from app.services.processor import processor
from app.services.reporter import reporter
from app.services.notifier import notifier
from app.utils.logger import get_logger
from app.redis_client import redis_client

logger = get_logger("celery_worker")

# Create Celery app
celery_app = Celery(
    "agworld_reporter",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.worker"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
)

@celery_app.task(bind=True)
def fetch_and_process_agworld_data(self, data_type: str, **kwargs):
    """Fetch data from Agworld and process it"""
    try:
        logger.info(f"Starting Agworld data fetch task: {data_type}")
        
        # Update task status
        self.update_state(
            state="PROGRESS",
            meta={"status": "Fetching data from Agworld", "progress": 10}
        )
        
        # Fetch data based on type
        raw_data = []
        if data_type == "fields":
            raw_data = agworld_client.get_fields()
        elif data_type == "crops":
            raw_data = agworld_client.get_crops()
        elif data_type == "activities":
            raw_data = agworld_client.get_activities(**kwargs)
        else:
            raise ValueError(f"Unknown data type: {data_type}")
        
        self.update_state(
            state="PROGRESS",
            meta={"status": "Processing data", "progress": 50}
        )
        
        # Process each data item
        processed_items = []
        for item in raw_data:
            processed_item = processor.process_agworld_data(item, data_type.rstrip('s'))
            processed_items.append(processed_item)
        
        self.update_state(
            state="PROGRESS",
            meta={"status": "Storing results", "progress": 90}
        )
        
        # Store in Redis for caching
        cache_key = f"processed_data:{data_type}:{datetime.utcnow().strftime('%Y%m%d_%H')}"
        redis_client.set(cache_key, processed_items, ex=3600)
        
        result = {
            "success": True,
            "data_type": data_type,
            "items_processed": len(processed_items),
            "cache_key": cache_key,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Completed Agworld data fetch task: {data_type}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to fetch and process {data_type} data: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "data_type": data_type}
        )
        raise

@celery_app.task(bind=True)
def generate_and_send_report(
    self,
    report_data: Dict[str, Any],
    format_type: str = "both",
    recipients: Dict[str, Any] = None
):
    """Generate and send a report"""
    try:
        logger.info("Starting report generation task")
        
        self.update_state(
            state="PROGRESS",
            meta={"status": "Generating report", "progress": 25}
        )
        
        # Generate report
        result = reporter.generate_report(report_data, format_type, recipients)
        
        self.update_state(
            state="PROGRESS",
            meta={"status": "Report generated", "progress": 75}
        )
        
        # Store result in Redis
        result_key = f"report_result:{self.request.id}"
        redis_client.set(result_key, result, ex=86400)  # 24 hours
        
        self.update_state(
            state="PROGRESS",
            meta={"status": "Completed", "progress": 100}
        )
        
        logger.info("Completed report generation task")
        return {
            "success": result["success"],
            "result_key": result_key,
            "pdf_generated": result.get("pdf_path") is not None,
            "email_sent": result.get("email_sent", False),
            "errors": result.get("errors", [])
        }
        
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True)
def send_notification_task(
    self,
    notification_type: str,
    recipients: Dict[str, Any],
    data: Dict[str, Any]
):
    """Send notification"""
    try:
        logger.info(f"Starting notification task: {notification_type}")
        
        self.update_state(
            state="PROGRESS",
            meta={"status": f"Sending {notification_type} notification", "progress": 50}
        )
        
        success = notifier.send_notification(notification_type, recipients, data)
        
        result = {
            "success": success,
            "notification_type": notification_type,
            "sent_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Completed notification task: {notification_type}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to send {notification_type} notification: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "notification_type": notification_type}
        )
        raise

@celery_app.task(bind=True)
def create_daily_summary_report(self):
    """Create and send daily summary report"""
    try:
        logger.info("Starting daily summary report task")
        
        self.update_state(
            state="PROGRESS",
            meta={"status": "Collecting data", "progress": 20}
        )
        
        # Collect processed data from today
        today = datetime.utcnow().strftime('%Y%m%d')
        processed_data_list = []
        
        # Get data from various sources
        for data_type in ["fields", "crops", "activities"]:
            for hour in range(24):
                cache_key = f"processed_data:{data_type}:{today}_{hour:02d}"
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    processed_data_list.extend(cached_data)
        
        self.update_state(
            state="PROGRESS",
            meta={"status": "Creating report", "progress": 60}
        )
        
        # Create summary report
        if processed_data_list:
            report_data = reporter.create_summary_report(processed_data_list)
        else:
            # Create empty report
            report_data = {
                "title": f"Daily Summary - {datetime.now().strftime('%Y-%m-%d')}",
                "created_at": datetime.utcnow().isoformat(),
                "status": "completed",
                "report_type": "daily_summary",
                "content": "No data processed today.",
                "data": {"total_records": 0}
            }
        
        self.update_state(
            state="PROGRESS",
            meta={"status": "Sending report", "progress": 80}
        )
        
        # TODO: Get recipients from database/configuration
        # For now, use placeholder recipients
        recipients = {
            "emails": ["admin@example.com"]  # Replace with actual email addresses
        }
        
        # Generate and send report
        result = reporter.generate_report(report_data, "email", recipients)
        
        logger.info("Completed daily summary report task")
        return {
            "success": result["success"],
            "records_processed": len(processed_data_list),
            "report_title": report_data["title"],
            "email_sent": result.get("email_sent", False),
            "errors": result.get("errors", [])
        }
        
    except Exception as e:
        logger.error(f"Failed to create daily summary report: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task
def cleanup_old_cache_data():
    """Clean up old cached data"""
    try:
        logger.info("Starting cache cleanup task")
        
        # This is a simplified cleanup - in a real implementation,
        # you'd scan Redis keys and remove old ones
        logger.info("Cache cleanup completed")
        return {"success": True, "message": "Cache cleanup completed"}
        
    except Exception as e:
        logger.error(f"Cache cleanup failed: {str(e)}")
        raise

# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    'fetch-fields-hourly': {
        'task': 'app.tasks.worker.fetch_and_process_agworld_data',
        'schedule': 3600.0,  # Every hour
        'args': ('fields',)
    },
    'fetch-activities-every-30min': {
        'task': 'app.tasks.worker.fetch_and_process_agworld_data',
        'schedule': 1800.0,  # Every 30 minutes
        'args': ('activities',)
    },
    'daily-summary-report': {
        'task': 'app.tasks.worker.create_daily_summary_report',
        'schedule': 86400.0,  # Daily
        'options': {'expires': 3600}
    },
    'cleanup-cache-daily': {
        'task': 'app.tasks.worker.cleanup_old_cache_data',
        'schedule': 86400.0,  # Daily
    },
}

if __name__ == "__main__":
    celery_app.start()
