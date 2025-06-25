from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
import logging

from ..models.liveness_models import (
    LivenessJob, StartLivenessRequest, LivenessStats,
    LivenessSearchRequest, LivenessResult, LivenessTool
)
from ..services.database import get_database
from ..services.liveness_service import liveness_service

router = APIRouter(tags=["liveness"])
logger = logging.getLogger(__name__)

@router.post("/targets/{target_id}/check-liveness", response_model=LivenessJob)
async def start_liveness_check(
    target_id: str, 
    request: StartLivenessRequest,
    background_tasks: BackgroundTasks
):
    """Start liveness check and fingerprinting for a target's subdomains"""
    try:
        db = get_database()
        
        # Check if target exists
        target = await db.targets.find_one({"id": target_id})
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Get subdomains from latest enumeration job
        enumeration_job = await db.enumeration_jobs.find_one(
            {"target_id": target_id, "status": {"$in": ["completed", "partial"]}},
            sort=[("completed_at", -1)]
        )
        
        if not enumeration_job or not enumeration_job.get("subdomains"):
            raise HTTPException(
                status_code=400, 
                detail="No subdomains found for this target. Please run subdomain enumeration first."
            )
        
        # Extract subdomain list
        subdomains = [sub["subdomain"] for sub in enumeration_job["subdomains"]]
        
        # Check if there's already a running liveness job
        existing_job = await db.liveness_jobs.find_one({
            "target_id": target_id,
            "status": {"$in": ["pending", "running"]}
        })
        if existing_job:
            raise HTTPException(
                status_code=400, 
                detail="Liveness check already running for this target"
            )
        
        # Create initial job record
        job = LivenessJob(
            target_id=target_id,
            domain=target["domain"],
            subdomains=subdomains,
            status="pending",
            notes=request.notes,
            total_hosts=len(subdomains)
        )
        
        # Insert job into database
        await db.liveness_jobs.insert_one(job.dict())
        
        # Start liveness check in background
        tools = request.tools if request.tools else list(LivenessTool)
        background_tasks.add_task(
            liveness_service.check_liveness_and_fingerprint,
            subdomains,
            target_id,
            target["domain"],
            tools,
            request.include_screenshots,
            request.include_tech_stack,
            request.include_tls_info
        )
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting liveness check: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/targets/{target_id}/liveness-results", response_model=List[LivenessResult])
async def get_target_liveness_results(
    target_id: str,
    limit: int = 100,
    offset: int = 0,
    alive_only: bool = True,
    with_screenshots: bool = False,
    with_tech_stack: bool = False
):
    """Get liveness check results for a target"""
    try:
        db = get_database()
        
        # Check if target exists
        target = await db.targets.find_one({"id": target_id})
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Get the latest completed liveness job
        job = await db.liveness_jobs.find_one(
            {"target_id": target_id, "status": {"$in": ["completed", "partial"]}},
            sort=[("completed_at", -1)]
        )
        
        if not job:
            return []
        
        # Extract results from job
        results = job.get("results", [])
        
        # Apply filters
        if alive_only:
            results = [r for r in results if r.get("is_alive") == True]
        
        if not with_screenshots:
            # Remove screenshot data to reduce response size
            results = [{k: v for k, v in r.items() if k != "screenshot_base64"} for r in results]
        
        if not with_tech_stack:
            # Remove tech stack data if not requested
            results = [{k: v for k, v in r.items() if k != "tech_stack"} for r in results]
        
        # Apply pagination
        paginated_results = results[offset:offset + limit]
        
        # Convert to LivenessResult objects
        result = []
        for result_data in paginated_results:
            try:
                result.append(LivenessResult(**result_data))
            except Exception as e:
                logger.error(f"Error converting result data: {e}")
                continue
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching liveness results: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/liveness-jobs/{job_id}", response_model=LivenessJob)
async def get_liveness_job(job_id: str):
    """Get details of a specific liveness job"""
    try:
        db = get_database()
        
        job = await db.liveness_jobs.find_one({"id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Liveness job not found")
        
        # Remove MongoDB _id from the response
        job.pop("_id", None)
        return LivenessJob(**job)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching liveness job: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/targets/{target_id}/liveness-jobs", response_model=List[LivenessJob])
async def get_target_liveness_jobs(target_id: str, limit: int = 10):
    """Get liveness jobs for a target"""
    try:
        db = get_database()
        
        # Check if target exists
        target = await db.targets.find_one({"id": target_id})
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Get liveness jobs for this target
        jobs = await db.liveness_jobs.find(
            {"target_id": target_id}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Convert to LivenessJob objects
        result = []
        for job in jobs:
            job.pop("_id", None)
            result.append(LivenessJob(**job))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching liveness jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/liveness/stats", response_model=LivenessStats)
async def get_liveness_stats():
    """Get overall liveness check statistics"""
    try:
        db = get_database()
        
        # Get all liveness jobs
        jobs = await db.liveness_jobs.find().to_list(1000)
        
        if not jobs:
            return LivenessStats(
                total_jobs=0,
                active_jobs=0,
                completed_jobs=0,
                failed_jobs=0,
                total_hosts_checked=0,
                total_alive_hosts=0,
                by_status={},
                by_tool_success_rate={},
                avg_execution_time=0,
                tech_stack_distribution={},
                cdn_waf_distribution={}
            )
        
        # Calculate statistics
        total_jobs = len(jobs)
        active_jobs = len([j for j in jobs if j.get("status") in ["pending", "running"]])
        completed_jobs = len([j for j in jobs if j.get("status") == "completed"])
        failed_jobs = len([j for j in jobs if j.get("status") == "failed"])
        
        total_hosts_checked = sum(j.get("total_hosts", 0) for j in jobs)
        total_alive_hosts = sum(j.get("alive_hosts", 0) for j in jobs)
        
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
        
        # Find most reliable tool
        most_reliable_tool = None
        if by_tool_success_rate:
            most_reliable_tool = max(
                by_tool_success_rate.keys(),
                key=lambda t: by_tool_success_rate[t]
            )
        
        # Calculate tech stack distribution
        tech_stack_distribution = {}
        cdn_waf_distribution = {}
        
        for job in jobs:
            for result in job.get("results", []):
                # Tech stack distribution
                tech_stack = result.get("tech_stack", {})
                if tech_stack:
                    cms = tech_stack.get("cms")
                    server = tech_stack.get("server")
                    if cms:
                        tech_stack_distribution[f"CMS: {cms}"] = tech_stack_distribution.get(f"CMS: {cms}", 0) + 1
                    if server:
                        tech_stack_distribution[f"Server: {server}"] = tech_stack_distribution.get(f"Server: {server}", 0) + 1
                
                # CDN/WAF distribution
                cdn_waf = result.get("cdn_waf_info", {})
                if cdn_waf:
                    cdn_provider = cdn_waf.get("cdn_provider")
                    waf_provider = cdn_waf.get("waf_provider")
                    if cdn_provider:
                        cdn_waf_distribution[f"CDN: {cdn_provider}"] = cdn_waf_distribution.get(f"CDN: {cdn_provider}", 0) + 1
                    if waf_provider:
                        cdn_waf_distribution[f"WAF: {waf_provider}"] = cdn_waf_distribution.get(f"WAF: {waf_provider}", 0) + 1
        
        return LivenessStats(
            total_jobs=total_jobs,
            active_jobs=active_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            total_hosts_checked=total_hosts_checked,
            total_alive_hosts=total_alive_hosts,
            by_status=by_status,
            by_tool_success_rate=by_tool_success_rate,
            avg_execution_time=avg_execution_time,
            most_reliable_tool=most_reliable_tool,
            tech_stack_distribution=tech_stack_distribution,
            cdn_waf_distribution=cdn_waf_distribution
        )
        
    except Exception as e:
        logger.error(f"Error fetching liveness stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/liveness-tools/install")
async def install_liveness_tools(background_tasks: BackgroundTasks):
    """Install all liveness/fingerprinting tools"""
    try:
        # Start installation in background
        background_tasks.add_task(liveness_service.install_all_tools)
        
        return {
            "message": "Liveness tools installation started",
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Error starting liveness tools installation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/liveness-tools/status")
async def get_liveness_tools_status():
    """Get installation status of all liveness/fingerprinting tools"""
    try:
        status = {}
        for tool in LivenessTool:
            status[tool.value] = await liveness_service.check_tool_installation(tool)
        
        return {
            "tools": status,
            "total_tools": len(LivenessTool),
            "installed_tools": sum(1 for installed in status.values() if installed)
        }
        
    except Exception as e:
        logger.error(f"Error checking liveness tools status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")