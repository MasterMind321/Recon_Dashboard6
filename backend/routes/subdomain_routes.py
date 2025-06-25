from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
import logging

from ..models.subdomain_models import (
    EnumerationJob, StartEnumerationRequest, EnumerationStats,
    SubdomainSearchRequest, SubdomainResult, SubdomainTool
)
from ..services.database import get_database
from ..services.subdomain_service import subdomain_service

router = APIRouter(tags=["subdomains"])
logger = logging.getLogger(__name__)

@router.post("/targets/{target_id}/enumerate-subdomains", response_model=EnumerationJob)
async def start_subdomain_enumeration(
    target_id: str, 
    request: StartEnumerationRequest,
    background_tasks: BackgroundTasks
):
    """Start subdomain enumeration for a target"""
    try:
        db = get_database()
        
        # Check if target exists
        target = await db.targets.find_one({"id": target_id})
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Check if there's already a running enumeration job
        existing_job = await db.enumeration_jobs.find_one({
            "target_id": target_id,
            "status": {"$in": ["pending", "running"]}
        })
        if existing_job:
            raise HTTPException(
                status_code=400, 
                detail="Enumeration already running for this target"
            )
        
        # Create initial job record
        job = EnumerationJob(
            target_id=target_id,
            domain=target["domain"],
            status="pending",
            notes=request.notes
        )
        
        # Insert job into database
        await db.enumeration_jobs.insert_one(job.dict())
        
        # Start enumeration in background
        tools = request.tools if request.tools else list(SubdomainTool)
        background_tasks.add_task(
            subdomain_service.enumerate_subdomains,
            target["domain"],
            target_id,
            tools
        )
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting subdomain enumeration: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/targets/{target_id}/subdomains", response_model=List[SubdomainResult])
async def get_target_subdomains(
    target_id: str,
    limit: int = 100,
    offset: int = 0,
    alive_only: bool = False
):
    """Get discovered subdomains for a target"""
    try:
        db = get_database()
        
        # Check if target exists
        target = await db.targets.find_one({"id": target_id})
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Get the latest completed enumeration job
        job = await db.enumeration_jobs.find_one(
            {"target_id": target_id, "status": {"$in": ["completed", "partial"]}},
            sort=[("completed_at", -1)]
        )
        
        if not job:
            return []
        
        # Extract subdomains from job
        subdomains = job.get("subdomains", [])
        
        # Apply filters
        if alive_only:
            subdomains = [s for s in subdomains if s.get("is_alive") == True]
        
        # Apply pagination
        total_subdomains = subdomains[offset:offset + limit]
        
        # Convert to SubdomainResult objects
        result = []
        for sub_data in total_subdomains:
            result.append(SubdomainResult(**sub_data))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching subdomains: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/enumeration-jobs/{job_id}", response_model=EnumerationJob)
async def get_enumeration_job(job_id: str):
    """Get details of a specific enumeration job"""
    try:
        db = get_database()
        
        job = await db.enumeration_jobs.find_one({"id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Enumeration job not found")
        
        # Remove MongoDB _id from the response
        job.pop("_id", None)
        return EnumerationJob(**job)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching enumeration job: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/targets/{target_id}/enumeration-jobs", response_model=List[EnumerationJob])
async def get_target_enumeration_jobs(target_id: str, limit: int = 10):
    """Get enumeration jobs for a target"""
    try:
        db = get_database()
        
        # Check if target exists
        target = await db.targets.find_one({"id": target_id})
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Get enumeration jobs for this target
        jobs = await db.enumeration_jobs.find(
            {"target_id": target_id}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Convert to EnumerationJob objects
        result = []
        for job in jobs:
            job.pop("_id", None)
            result.append(EnumerationJob(**job))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching enumeration jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/subdomains/stats", response_model=EnumerationStats)
async def get_enumeration_stats():
    """Get overall enumeration statistics"""
    try:
        db = get_database()
        
        # Get all enumeration jobs
        jobs = await db.enumeration_jobs.find().to_list(1000)
        
        if not jobs:
            return EnumerationStats(
                total_jobs=0,
                active_jobs=0,
                completed_jobs=0,
                failed_jobs=0,
                total_subdomains_discovered=0,
                by_status={},
                by_tool_success_rate={},
                avg_execution_time=0
            )
        
        # Calculate statistics
        total_jobs = len(jobs)
        active_jobs = len([j for j in jobs if j.get("status") in ["pending", "running"]])
        completed_jobs = len([j for j in jobs if j.get("status") == "completed"])
        failed_jobs = len([j for j in jobs if j.get("status") == "failed"])
        
        total_subdomains = sum(j.get("unique_subdomains", 0) for j in jobs)
        
        # Group by status
        by_status = {}
        for job in jobs:
            status = job.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
        
        # Calculate tool success rates
        tool_stats = {}
        for job in jobs:
            for tool_result in job.get("tools_executed", []):
                tool_name = tool_result.get("tool")
                if tool_name not in tool_stats:
                    tool_stats[tool_name] = {"success": 0, "total": 0}
                tool_stats[tool_name]["total"] += 1
                if tool_result.get("status") == "success":
                    tool_stats[tool_name]["success"] += 1
        
        by_tool_success_rate = {}
        for tool, stats in tool_stats.items():
            if stats["total"] > 0:
                by_tool_success_rate[tool] = stats["success"] / stats["total"]
        
        # Calculate average execution time
        execution_times = []
        for job in jobs:
            if job.get("started_at") and job.get("completed_at"):
                start = job["started_at"]
                end = job["completed_at"]
                if isinstance(start, str):
                    from datetime import datetime
                    start = datetime.fromisoformat(start)
                    end = datetime.fromisoformat(end)
                execution_times.append((end - start).total_seconds())
        
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # Find most productive tool
        most_productive_tool = None
        if tool_stats:
            most_productive_tool = max(
                tool_stats.keys(),
                key=lambda t: tool_stats[t]["success"]
            )
        
        return EnumerationStats(
            total_jobs=total_jobs,
            active_jobs=active_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            total_subdomains_discovered=total_subdomains,
            by_status=by_status,
            by_tool_success_rate=by_tool_success_rate,
            avg_execution_time=avg_execution_time,
            most_productive_tool=most_productive_tool
        )
        
    except Exception as e:
        logger.error(f"Error fetching enumeration stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/tools/install")
async def install_enumeration_tools(background_tasks: BackgroundTasks):
    """Install all subdomain enumeration tools"""
    try:
        # Start installation in background
        background_tasks.add_task(subdomain_service.install_all_tools)
        
        return {
            "message": "Tool installation started",
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Error starting tool installation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/tools/status")
async def get_tools_status():
    """Get installation status of all subdomain enumeration tools"""
    try:
        status = {}
        for tool in SubdomainTool:
            status[tool.value] = await subdomain_service.check_tool_installation(tool)
        
        return {
            "tools": status,
            "total_tools": len(SubdomainTool),
            "installed_tools": sum(1 for installed in status.values() if installed)
        }
        
    except Exception as e:
        logger.error(f"Error checking tools status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")