from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from typing import Dict, Any, Callable, Optional
from datetime import datetime
import atexit
from app.utils.logger import LoggerMixin
from app.redis_client import redis_client

class TaskScheduler(LoggerMixin):
    """Handles scheduled polling and background tasks"""
    
    def __init__(self):
        super().__init__()
        self.scheduler = BackgroundScheduler(
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 300  # 5 minutes
            }
        )
        self.is_running = False
        
        # Register shutdown handler
        atexit.register(self.shutdown)
    
    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            try:
                self.scheduler.start()
                self.is_running = True
                self.log_info("Task scheduler started")
            except Exception as e:
                self.log_error(f"Failed to start scheduler: {str(e)}")
                raise
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.is_running:
            try:
                self.scheduler.shutdown(wait=True)
                self.is_running = False
                self.log_info("Task scheduler shutdown")
            except Exception as e:
                self.log_error(f"Error during scheduler shutdown: {str(e)}")
    
    def add_polling_job(
        self,
        func: Callable,
        job_id: str,
        interval_minutes: int = 60,
        **kwargs
    ) -> bool:
        """Add a polling job that runs at regular intervals"""
        try:
            trigger = IntervalTrigger(minutes=interval_minutes)
            
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                replace_existing=True,
                **kwargs
            )
            
            self.log_info(f"Added polling job '{job_id}' with {interval_minutes} minute interval")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to add polling job '{job_id}': {str(e)}")
            return False
    
    def add_cron_job(
        self,
        func: Callable,
        job_id: str,
        cron_expression: str,
        **kwargs
    ) -> bool:
        """Add a job with cron schedule"""
        try:
            # Parse cron expression (minute, hour, day, month, day_of_week)
            cron_parts = cron_expression.split()
            if len(cron_parts) != 5:
                raise ValueError("Cron expression must have 5 parts")
            
            trigger = CronTrigger(
                minute=cron_parts[0],
                hour=cron_parts[1],
                day=cron_parts[2],
                month=cron_parts[3],
                day_of_week=cron_parts[4]
            )
            
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                replace_existing=True,
                **kwargs
            )
            
            self.log_info(f"Added cron job '{job_id}' with schedule '{cron_expression}'")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to add cron job '{job_id}': {str(e)}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            self.log_info(f"Removed job '{job_id}'")
            return True
        except Exception as e:
            self.log_error(f"Failed to remove job '{job_id}': {str(e)}")
            return False
    
    def get_jobs(self) -> list:
        """Get list of all scheduled jobs"""
        return self.scheduler.get_jobs()
    
    def pause_job(self, job_id: str) -> bool:
        """Pause a scheduled job"""
        try:
            self.scheduler.pause_job(job_id)
            self.log_info(f"Paused job '{job_id}'")
            return True
        except Exception as e:
            self.log_error(f"Failed to pause job '{job_id}': {str(e)}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job"""
        try:
            self.scheduler.resume_job(job_id)
            self.log_info(f"Resumed job '{job_id}'")
            return True
        except Exception as e:
            self.log_error(f"Failed to resume job '{job_id}': {str(e)}")
            return False

class AgworldPoller(LoggerMixin):
    """Handles scheduled polling of Agworld API"""
    
    def __init__(self, scheduler: TaskScheduler):
        super().__init__()
        self.scheduler = scheduler
        self._setup_default_jobs()
    
    def _setup_default_jobs(self):
        """Setup default polling jobs"""
        # Example polling jobs - you'll customize these based on your needs
        
        # Poll for field data every hour
        self.scheduler.add_polling_job(
            func=self.poll_field_data,
            job_id="poll_fields",
            interval_minutes=60
        )
        
        # Poll for activities every 30 minutes
        self.scheduler.add_polling_job(
            func=self.poll_activity_data,
            job_id="poll_activities",
            interval_minutes=30
        )
        
        # Generate daily reports at 8 AM
        self.scheduler.add_cron_job(
            func=self.generate_daily_report,
            job_id="daily_report",
            cron_expression="0 8 * * *"  # 8:00 AM every day
        )
    
    def poll_field_data(self):
        """Poll Agworld for field data"""
        try:
            self.log_info("Starting field data polling")
            
            # Set polling status in Redis
            redis_client.set("polling:fields:status", "running", ex=3600)
            redis_client.set("polling:fields:last_run", datetime.utcnow().isoformat())
            
            # TODO: Implement actual Agworld API call here
            # from app.services.agworld_client import agworld_client
            # field_data = agworld_client.get_fields()
            # processed_data = processor.process_agworld_data(field_data, "field")
            
            self.log_info("Field data polling completed")
            redis_client.set("polling:fields:status", "completed")
            
        except Exception as e:
            self.log_error(f"Field data polling failed: {str(e)}")
            redis_client.set("polling:fields:status", "failed")
            redis_client.set("polling:fields:error", str(e))
    
    def poll_activity_data(self):
        """Poll Agworld for activity data"""
        try:
            self.log_info("Starting activity data polling")
            
            redis_client.set("polling:activities:status", "running", ex=3600)
            redis_client.set("polling:activities:last_run", datetime.utcnow().isoformat())
            
            # TODO: Implement actual Agworld API call here
            # from app.services.agworld_client import agworld_client
            # activity_data = agworld_client.get_activities()
            # processed_data = processor.process_agworld_data(activity_data, "activity")
            
            self.log_info("Activity data polling completed")
            redis_client.set("polling:activities:status", "completed")
            
        except Exception as e:
            self.log_error(f"Activity data polling failed: {str(e)}")
            redis_client.set("polling:activities:status", "failed")
            redis_client.set("polling:activities:error", str(e))
    
    def generate_daily_report(self):
        """Generate and send daily report"""
        try:
            self.log_info("Starting daily report generation")
            
            redis_client.set("report:daily:status", "running", ex=3600)
            redis_client.set("report:daily:last_run", datetime.utcnow().isoformat())
            
            # TODO: Implement report generation
            # from app.services.reporter import reporter
            # report_data = reporter.create_summary_report(processed_data_list)
            # reporter.generate_report(report_data, "email", recipients)
            
            self.log_info("Daily report generation completed")
            redis_client.set("report:daily:status", "completed")
            
        except Exception as e:
            self.log_error(f"Daily report generation failed: {str(e)}")
            redis_client.set("report:daily:status", "failed")
            redis_client.set("report:daily:error", str(e))

# Global scheduler instances
task_scheduler = TaskScheduler()
agworld_poller = AgworldPoller(task_scheduler)
