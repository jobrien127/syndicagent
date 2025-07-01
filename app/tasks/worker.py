from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

from app.config import settings
from app.services.agworld_client import agworld_client
from app.services.processor import processor
from app.services.reporter import reporter
from app.services.notifier import notifier
from app.redis_client import redis_client
from app.utils.logger import get_logger

# Create Celery app
celery_app = Celery(
    "agworld_reporter",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.tasks.worker']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'poll-field-data': {
        'task': 'app.tasks.worker.poll_field_data',
        'schedule': 3600.0,  # Every hour
    },
    'poll-activity-data': {
        'task': 'app.tasks.worker.poll_activity_data',
        'schedule': 1800.0,  # Every 30 minutes
    },
    'poll-crop-data': {
        'task': 'app.tasks.worker.poll_crop_data',
        'schedule': 7200.0,  # Every 2 hours
    },
    'generate-daily-report': {
        'task': 'app.tasks.worker.generate_daily_report',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8:00 AM
    },
    'cleanup-cache': {
        'task': 'app.tasks.worker.cleanup_cache',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2:00 AM
    },
}

logger = get_logger("celery_worker")

@celery_app.task(bind=True, name='app.tasks.worker.poll_field_data')
def poll_field_data(self):
    """Celery task to poll field data from Agworld API"""
    try:
        logger.info("Starting field data polling task")
        redis_client.set("polling:fields:status", "running")
        redis_client.set("polling:fields:last_run", datetime.utcnow().isoformat())
        
        # Fetch field data
        field_data = agworld_client.get_fields()
        
        if field_data:
            # Process the data
            processed_fields = []
            for field in field_data:
                processed_field = processor.process_agworld_data(field, "field")
                processed_fields.append(processed_field)
            
            # Cache processed data
            cache_key = "agworld:fields:latest"
            redis_client.setex(
                cache_key, 
                3600,  # 1 hour TTL
                json.dumps(processed_fields, default=str)
            )
            
            logger.info(f"Successfully polled and cached {len(processed_fields)} fields")
            redis_client.set("polling:fields:status", "completed")
            redis_client.delete("polling:fields:error")
            
            return {"success": True, "count": len(processed_fields)}
        else:
            logger.warning("No field data received from API")
            redis_client.set("polling:fields:status", "no_data")
            return {"success": False, "error": "No data received"}
            
    except Exception as e:
        error_msg = f"Field polling failed: {str(e)}"
        logger.error(error_msg)
        redis_client.set("polling:fields:status", "error")
        redis_client.set("polling:fields:error", error_msg)
        
        # Retry task with exponential backoff
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='app.tasks.worker.poll_activity_data')
def poll_activity_data(self):
    """Celery task to poll activity data from Agworld API"""
    try:
        logger.info("Starting activity data polling task")
        redis_client.set("polling:activities:status", "running")
        redis_client.set("polling:activities:last_run", datetime.utcnow().isoformat())
        
        # Fetch activity data
        activity_data = agworld_client.get_activities()
        
        if activity_data:
            # Process the data
            processed_activities = []
            for activity in activity_data:
                processed_activity = processor.process_agworld_data(activity, "activity")
                processed_activities.append(processed_activity)
            
            # Cache processed data
            cache_key = "agworld:activities:latest"
            redis_client.setex(
                cache_key, 
                3600,  # 1 hour TTL
                json.dumps(processed_activities, default=str)
            )
            
            logger.info(f"Successfully polled and cached {len(processed_activities)} activities")
            redis_client.set("polling:activities:status", "completed")
            redis_client.delete("polling:activities:error")
            
            return {"success": True, "count": len(processed_activities)}
        else:
            logger.warning("No activity data received from API")
            redis_client.set("polling:activities:status", "no_data")
            return {"success": False, "error": "No data received"}
            
    except Exception as e:
        error_msg = f"Activity polling failed: {str(e)}"
        logger.error(error_msg)
        redis_client.set("polling:activities:status", "error")
        redis_client.set("polling:activities:error", error_msg)
        
        # Retry task with exponential backoff
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='app.tasks.worker.poll_crop_data')
def poll_crop_data(self):
    """Celery task to poll crop data from Agworld API"""
    try:
        logger.info("Starting crop data polling task")
        redis_client.set("polling:crops:status", "running")
        redis_client.set("polling:crops:last_run", datetime.utcnow().isoformat())
        
        # Fetch crop data
        crop_data = agworld_client.get_crops()
        
        if crop_data:
            # Process the data
            processed_crops = []
            for crop in crop_data:
                processed_crop = processor.process_agworld_data(crop, "crop")
                processed_crops.append(processed_crop)
            
            # Cache processed data
            cache_key = "agworld:crops:latest"
            redis_client.setex(
                cache_key, 
                3600,  # 1 hour TTL
                json.dumps(processed_crops, default=str)
            )
            
            logger.info(f"Successfully polled and cached {len(processed_crops)} crops")
            redis_client.set("polling:crops:status", "completed")
            redis_client.delete("polling:crops:error")
            
            return {"success": True, "count": len(processed_crops)}
        else:
            logger.warning("No crop data received from API")
            redis_client.set("polling:crops:status", "no_data")
            return {"success": False, "error": "No data received"}
            
    except Exception as e:
        error_msg = f"Crop polling failed: {str(e)}"
        logger.error(error_msg)
        redis_client.set("polling:crops:status", "error")
        redis_client.set("polling:crops:error", error_msg)
        
        # Retry task with exponential backoff
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='app.tasks.worker.generate_daily_report')
def generate_daily_report(self):
    """Celery task to generate daily summary report"""
    try:
        logger.info("Starting daily report generation task")
        redis_client.set("report:daily:status", "running")
        redis_client.set("report:daily:last_run", datetime.utcnow().isoformat())
        
        # Gather data from cache
        data_sources = {
            "fields": "agworld:fields:latest",
            "activities": "agworld:activities:latest",
            "crops": "agworld:crops:latest"
        }
        
        combined_data = []
        for source_name, cache_key in data_sources.items():
            cached_data = redis_client.get(cache_key)
            if cached_data:
                try:
                    parsed_data = json.loads(cached_data)
                    combined_data.extend(parsed_data)
                    logger.info(f"Added {len(parsed_data)} {source_name} records to report")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse cached {source_name} data: {e}")
        
        if combined_data:
            # Generate report
            report_data = reporter.create_summary_report(combined_data)
            
            # Generate PDF
            result = reporter.generate_report(
                report_data, 
                format_type="pdf"
            )
            
            if result.get("success"):
                logger.info("Daily report generated successfully")
                redis_client.set("report:daily:status", "completed")
                redis_client.delete("report:daily:error")
                
                # Store report metadata in cache
                report_metadata = {
                    "file_path": result.get("file_path"),
                    "generated_at": datetime.utcnow().isoformat(),
                    "record_count": len(combined_data)
                }
                redis_client.setex(
                    "report:daily:latest", 
                    86400,  # 24 hours
                    json.dumps(report_metadata, default=str)
                )
                
                return {"success": True, "file_path": result.get("file_path")}
            else:
                error_msg = f"Report generation failed: {result.get('errors', 'Unknown error')}"
                logger.error(error_msg)
                redis_client.set("report:daily:status", "error")
                redis_client.set("report:daily:error", error_msg)
                return {"success": False, "error": error_msg}
        else:
            logger.warning("No data available for daily report")
            redis_client.set("report:daily:status", "no_data")
            return {"success": False, "error": "No data available"}
            
    except Exception as e:
        error_msg = f"Daily report generation failed: {str(e)}"
        logger.error(error_msg)
        redis_client.set("report:daily:status", "error")
        redis_client.set("report:daily:error", error_msg)
        
        # Retry task with exponential backoff
        raise self.retry(exc=e, countdown=300, max_retries=2)  # 5 minute delay, 2 retries

@celery_app.task(bind=True, name='app.tasks.worker.cleanup_cache')
def cleanup_cache(self):
    """Celery task to clean up old cache entries"""
    try:
        logger.info("Starting cache cleanup task")
        
        # Define patterns for keys to clean
        patterns = [
            "agworld:*:processed:*",
            "report:*:temp:*",
            "polling:*:old:*"
        ]
        
        cleaned_count = 0
        for pattern in patterns:
            keys = redis_client.keys(pattern)
            if keys:
                for key in keys:
                    # Check if key is older than 24 hours
                    ttl = redis_client.ttl(key)
                    if ttl == -1 or ttl > 86400:  # No TTL or > 24 hours
                        redis_client.delete(key)
                        cleaned_count += 1
        
        logger.info(f"Cache cleanup completed. Removed {cleaned_count} old entries")
        return {"success": True, "cleaned_count": cleaned_count}
        
    except Exception as e:
        logger.error(f"Cache cleanup failed: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=2)

@celery_app.task(bind=True, name='app.tasks.worker.generate_custom_report')
def generate_custom_report(self, report_data: Dict[str, Any], format_type: str = "both", recipients: Dict[str, Any] = None):
    """Celery task to generate a custom report"""
    try:
        logger.info("Starting custom report generation task")
        
        # Generate the report
        result = reporter.generate_report(report_data, format_type, recipients)
        
        if result.get("success"):
            logger.info("Custom report generated successfully")
            return result
        else:
            logger.error(f"Custom report generation failed: {result.get('errors')}")
            return result
            
    except Exception as e:
        error_msg = f"Custom report generation failed: {str(e)}"
        logger.error(error_msg)
        raise self.retry(exc=e, countdown=60, max_retries=2)

@celery_app.task(bind=True, name='app.tasks.worker.process_data_batch')
def process_data_batch(self, data_batch: List[Dict[str, Any]], data_type: str):
    """Celery task to process a batch of data"""
    try:
        logger.info(f"Starting batch processing of {len(data_batch)} {data_type} records")
        
        processed_records = []
        for record in data_batch:
            try:
                processed_record = processor.process_agworld_data(record, data_type)
                processed_records.append(processed_record)
            except Exception as e:
                logger.error(f"Failed to process record {record.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(processed_records)} of {len(data_batch)} records")
        return {"success": True, "processed_count": len(processed_records), "total_count": len(data_batch)}
        
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        raise self.retry(exc=e, countdown=30, max_retries=2)

# For backwards compatibility
app = celery_app
