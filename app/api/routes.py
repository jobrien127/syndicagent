from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.database import get_db
from app.models.report import Report, ReportCreate, ReportUpdate, ReportResponse
from app.services.processor import processor
from app.services.reporter import reporter
from app.services.notifier import notifier
from app.scheduler.poller import task_scheduler, agworld_poller
from app.redis_client import redis_client
from app.utils.logger import get_logger

# Create router
router = APIRouter(prefix="/api/v1", tags=["api"])
logger = get_logger("api_routes")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = "ok"
        try:
            # This will be implemented when you set up the database
            pass
        except Exception:
            db_status = "error"
        
        # Check Redis connection
        redis_status = "ok" if redis_client.ping() else "error"
        
        # Check scheduler status
        scheduler_status = "running" if task_scheduler.is_running else "stopped"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": db_status,
                "redis": redis_status,
                "scheduler": scheduler_status
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

# Reports endpoints
@router.get("/reports", response_model=List[ReportResponse])
async def get_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of reports"""
    try:
        # TODO: Implement database query when you set up the models
        # reports = db.query(Report).offset(skip).limit(limit).all()
        # return reports
        
        # Placeholder response
        return []
    except Exception as e:
        logger.error(f"Failed to get reports: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve reports")

@router.post("/reports", response_model=ReportResponse)
async def create_report(
    report: ReportCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new report"""
    try:
        # TODO: Implement database creation when you set up the models
        # db_report = Report(**report.dict())
        # db.add(db_report)
        # db.commit()
        # db.refresh(db_report)
        
        # Schedule report generation in background
        background_tasks.add_task(generate_report_background, report.dict())
        
        # Placeholder response
        return {
            "id": 1,
            "title": report.title,
            "content": report.content,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "report_type": report.report_type,
            "recipients": report.recipients,
            "is_active": True
        }
    except Exception as e:
        logger.error(f"Failed to create report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create report")

@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get a specific report"""
    try:
        # TODO: Implement database query when you set up the models
        # report = db.query(Report).filter(Report.id == report_id).first()
        # if not report:
        #     raise HTTPException(status_code=404, detail="Report not found")
        # return report
        
        # Placeholder response
        return {
            "id": report_id,
            "title": "Sample Report",
            "content": "Sample content",
            "status": "completed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "report_type": "daily",
            "recipients": None,
            "is_active": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report {report_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve report")

# Data processing endpoints
@router.post("/data/process")
async def process_data(
    data: Dict[str, Any],
    data_type: str = "generic"
):
    """Process raw data"""
    try:
        processed_data = processor.process_agworld_data(data, data_type)
        return {
            "success": True,
            "processed_data": processed_data,
            "message": f"Successfully processed {data_type} data"
        }
    except Exception as e:
        logger.error(f"Failed to process data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process data")

@router.post("/reports/generate")
async def generate_report_endpoint(
    background_tasks: BackgroundTasks,
    report_data: Dict[str, Any],
    format_type: str = "both",
    recipients: Optional[Dict[str, Any]] = None
):
    """Generate a report"""
    try:
        # Schedule report generation in background
        background_tasks.add_task(
            generate_report_background,
            report_data,
            format_type,
            recipients
        )
        
        return {
            "success": True,
            "message": "Report generation started",
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Failed to start report generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start report generation")

# Scheduler management endpoints
@router.get("/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status"""
    try:
        jobs = task_scheduler.get_jobs()
        job_info = []
        
        for job in jobs:
            job_info.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "scheduler_running": task_scheduler.is_running,
            "total_jobs": len(jobs),
            "jobs": job_info
        }
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get scheduler status")

@router.post("/scheduler/start")
async def start_scheduler():
    """Start the task scheduler"""
    try:
        if not task_scheduler.is_running:
            task_scheduler.start()
            return {"success": True, "message": "Scheduler started"}
        else:
            return {"success": True, "message": "Scheduler already running"}
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start scheduler")

@router.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the task scheduler"""
    try:
        if task_scheduler.is_running:
            task_scheduler.shutdown()
            return {"success": True, "message": "Scheduler stopped"}
        else:
            return {"success": True, "message": "Scheduler already stopped"}
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stop scheduler")

# Polling status endpoints
@router.get("/polling/status")
async def get_polling_status():
    """Get status of all polling jobs"""
    try:
        status_data = {}
        
        # Get field polling status
        field_status = redis_client.get("polling:fields:status") or "unknown"
        field_last_run = redis_client.get("polling:fields:last_run")
        field_error = redis_client.get("polling:fields:error")
        
        status_data["fields"] = {
            "status": field_status,
            "last_run": field_last_run,
            "error": field_error
        }
        
        # Get activity polling status
        activity_status = redis_client.get("polling:activities:status") or "unknown"
        activity_last_run = redis_client.get("polling:activities:last_run")
        activity_error = redis_client.get("polling:activities:error")
        
        status_data["activities"] = {
            "status": activity_status,
            "last_run": activity_last_run,
            "error": activity_error
        }
        
        # Get daily report status
        report_status = redis_client.get("report:daily:status") or "unknown"
        report_last_run = redis_client.get("report:daily:last_run")
        report_error = redis_client.get("report:daily:error")
        
        status_data["daily_report"] = {
            "status": report_status,
            "last_run": report_last_run,
            "error": report_error
        }
        
        return status_data
        
    except Exception as e:
        logger.error(f"Failed to get polling status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get polling status")

@router.post("/polling/trigger/{job_type}")
async def trigger_polling_job(
    job_type: str,
    background_tasks: BackgroundTasks
):
    """Manually trigger a polling job"""
    try:
        if job_type == "fields":
            background_tasks.add_task(agworld_poller.poll_field_data)
        elif job_type == "activities":
            background_tasks.add_task(agworld_poller.poll_activity_data)
        elif job_type == "daily_report":
            background_tasks.add_task(agworld_poller.generate_daily_report)
        else:
            raise HTTPException(status_code=400, detail="Invalid job type")
        
        return {
            "success": True,
            "message": f"Triggered {job_type} polling job"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger {job_type} job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger {job_type} job")

# Background task functions
async def generate_report_background(
    report_data: Dict[str, Any],
    format_type: str = "both",
    recipients: Optional[Dict[str, Any]] = None
):
    """Background task for report generation"""
    try:
        logger.info("Starting background report generation")
        result = reporter.generate_report(report_data, format_type, recipients)
        
        if result["success"]:
            logger.info("Background report generation completed successfully")
        else:
            logger.error(f"Background report generation failed: {result['errors']}")
            
    except Exception as e:
        logger.error(f"Background report generation error: {str(e)}")

# Include router in main app
def include_routes(app):
    """Include routes in the main FastAPI app"""
    app.include_router(router)
