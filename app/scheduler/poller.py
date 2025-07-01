from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

from app.services.agworld_client import agworld_client
from app.services.processor import processor
from app.services.reporter import reporter
from app.services.notifier import notifier
from app.redis_client import redis_client
from app.utils.logger import LoggerMixin

class AgworldPoller(LoggerMixin):
    """Handles scheduled polling of Agworld API data"""
    
    def __init__(self):
        super().__init__()
        self.cache_ttl = 3600  # 1 hour
    
    def poll_field_data(self):
        """Poll field data from Agworld API"""
        try:
            self.log_info("Starting field data polling")
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
                    self.cache_ttl, 
                    json.dumps(processed_fields, default=str)
                )
                
                self.log_info(f"Successfully polled and cached {len(processed_fields)} fields")
                redis_client.set("polling:fields:status", "completed")
                redis_client.delete("polling:fields:error")
            else:
                self.log_warning("No field data received from API")
                redis_client.set("polling:fields:status", "no_data")
                
        except Exception as e:
            error_msg = f"Field polling failed: {str(e)}"
            self.log_error(error_msg)
            redis_client.set("polling:fields:status", "error")
            redis_client.set("polling:fields:error", error_msg)
    
    def poll_activity_data(self):
        """Poll activity data from Agworld API"""
        try:
            self.log_info("Starting activity data polling")
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
                    self.cache_ttl, 
                    json.dumps(processed_activities, default=str)
                )
                
                self.log_info(f"Successfully polled and cached {len(processed_activities)} activities")
                redis_client.set("polling:activities:status", "completed")
                redis_client.delete("polling:activities:error")
            else:
                self.log_warning("No activity data received from API")
                redis_client.set("polling:activities:status", "no_data")
                
        except Exception as e:
            error_msg = f"Activity polling failed: {str(e)}"
            self.log_error(error_msg)
            redis_client.set("polling:activities:status", "error")
            redis_client.set("polling:activities:error", error_msg)
    
    def poll_crop_data(self):
        """Poll crop data from Agworld API"""
        try:
            self.log_info("Starting crop data polling")
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
                    self.cache_ttl, 
                    json.dumps(processed_crops, default=str)
                )
                
                self.log_info(f"Successfully polled and cached {len(processed_crops)} crops")
                redis_client.set("polling:crops:status", "completed")
                redis_client.delete("polling:crops:error")
            else:
                self.log_warning("No crop data received from API")
                redis_client.set("polling:crops:status", "no_data")
                
        except Exception as e:
            error_msg = f"Crop polling failed: {str(e)}"
            self.log_error(error_msg)
            redis_client.set("polling:crops:status", "error")
            redis_client.set("polling:crops:error", error_msg)
    
    def generate_daily_report(self):
        """Generate daily summary report"""
        try:
            self.log_info("Starting daily report generation")
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
                        self.log_info(f"Added {len(parsed_data)} {source_name} records to report")
                    except json.JSONDecodeError as e:
                        self.log_error(f"Failed to parse cached {source_name} data: {e}")
            
            if combined_data:
                # Generate report
                report_data = reporter.create_summary_report(combined_data)
                
                # Generate PDF
                result = reporter.generate_report(
                    report_data, 
                    format_type="pdf"
                )
                
                if result.get("success"):
                    self.log_info("Daily report generated successfully")
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
                else:
                    error_msg = f"Report generation failed: {result.get('errors', 'Unknown error')}"
                    self.log_error(error_msg)
                    redis_client.set("report:daily:status", "error")
                    redis_client.set("report:daily:error", error_msg)
            else:
                self.log_warning("No data available for daily report")
                redis_client.set("report:daily:status", "no_data")
                
        except Exception as e:
            error_msg = f"Daily report generation failed: {str(e)}"
            self.log_error(error_msg)
            redis_client.set("report:daily:status", "error")
            redis_client.set("report:daily:error", error_msg)
    
    def cleanup_cache(self):
        """Clean up old cache entries"""
        try:
            self.log_info("Starting cache cleanup")
            
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
            
            self.log_info(f"Cache cleanup completed. Removed {cleaned_count} old entries")
            
        except Exception as e:
            self.log_error(f"Cache cleanup failed: {str(e)}")

class TaskScheduler(LoggerMixin):
    """Manages scheduled tasks using APScheduler"""
    
    def __init__(self):
        super().__init__()
        self.scheduler = BackgroundScheduler()
        self.poller = AgworldPoller()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Set up scheduled jobs"""
        try:
            # Field data polling - every hour
            self.scheduler.add_job(
                func=self.poller.poll_field_data,
                trigger=IntervalTrigger(hours=1),
                id="poll_fields",
                name="Poll Field Data",
                replace_existing=True
            )
            
            # Activity data polling - every 30 minutes
            self.scheduler.add_job(
                func=self.poller.poll_activity_data,
                trigger=IntervalTrigger(minutes=30),
                id="poll_activities",
                name="Poll Activity Data",
                replace_existing=True
            )
            
            # Crop data polling - every 2 hours
            self.scheduler.add_job(
                func=self.poller.poll_crop_data,
                trigger=IntervalTrigger(hours=2),
                id="poll_crops",
                name="Poll Crop Data",
                replace_existing=True
            )
            
            # Daily report generation - every day at 8:00 AM
            self.scheduler.add_job(
                func=self.poller.generate_daily_report,
                trigger=CronTrigger(hour=8, minute=0),
                id="daily_report",
                name="Generate Daily Report",
                replace_existing=True
            )
            
            # Cache cleanup - every day at 2:00 AM
            self.scheduler.add_job(
                func=self.poller.cleanup_cache,
                trigger=CronTrigger(hour=2, minute=0),
                id="cache_cleanup",
                name="Cache Cleanup",
                replace_existing=True
            )
            
            self.log_info("Scheduled jobs configured successfully")
            
        except Exception as e:
            self.log_error(f"Failed to setup scheduled jobs: {str(e)}")
    
    def start(self):
        """Start the scheduler"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                self.log_info("Task scheduler started successfully")
            else:
                self.log_info("Task scheduler is already running")
        except Exception as e:
            self.log_error(f"Failed to start scheduler: {str(e)}")
            raise
    
    def shutdown(self):
        """Shutdown the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                self.log_info("Task scheduler stopped successfully")
            else:
                self.log_info("Task scheduler is not running")
        except Exception as e:
            self.log_error(f"Failed to shutdown scheduler: {str(e)}")
    
    def get_jobs(self):
        """Get list of all scheduled jobs"""
        return self.scheduler.get_jobs()
    
    @property
    def is_running(self):
        """Check if scheduler is running"""
        return self.scheduler.running

# Global instances
task_scheduler = TaskScheduler()
agworld_poller = AgworldPoller()
