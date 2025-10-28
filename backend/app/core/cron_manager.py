import uuid
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.config import setup_colored_logging
from typing import List, Dict
from datetime import datetime

logger = setup_colored_logging()

class CronManager:
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs: Dict[str, dict] = {}
        self._task_processor = None
    
    def add_aggregation_job(self, func, name: str = "Unnamed Job"):
        """Add a job that runs at fixed intervals"""
        id = str(uuid.uuid4())
        job_id = f"{name}_{id}"
        
        job = self.scheduler.add_job(
            func,
            trigger='cron',
            minute=0,
            hour='4-23/2',
            id=job_id,
            name=name,
            replace_existing=True
        )
        
        self.jobs[job_id] = {
            'name': name,
            'next_run': job._get_run_times
        }
        
        logger.info(f"📅 Scheduled job '{name}' to run every 4 hours (4am - midnight)")
        return job_id
    
    def add_one_time_job(self, func, name: str = "Unnamed Startup Job"):
        """Add a job that runs once on startup"""
        job_id = f"{name}_startup"
        
        job = self.scheduler.add_job(
            func,
            trigger='date',  # Run once at a specific time
            run_date=datetime.now(),  # Run immediately
            id=job_id,
            name=name,
            replace_existing=True
        )
        
        self.jobs[job_id] = {
            'name': name,
            'type': 'startup',
            'next_run': job._get_run_times
        }
        
        logger.info(f"🚀 Scheduled startup job '{name}' to run immediately")
        return job_id
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("\n\n\n🚀 Started APScheduler\n\n\n")
        else:
            logger.info("ℹ️ APScheduler already running")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("🛑 Stopped APScheduler")
        else:
            logger.info("ℹ️ APScheduler already stopped")
    
    def get_status(self) -> List[dict]:
        """Get status of all jobs"""
        status = []
        for job in self.scheduler.get_jobs():
            status.append({
                'id': job.id,
                'name': job.name,
                'next_run': job._get_run_times.isoformat() if job._get_run_times else None,
                'last_run': job.last_run_time.isoformat() if hasattr(job, 'last_run_time') and job.last_run_time else None
            })
        return status
    
    @property
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self.scheduler.running

cron_manager = CronManager()