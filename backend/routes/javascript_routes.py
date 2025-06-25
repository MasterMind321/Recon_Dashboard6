from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
import logging

from ..models.javascript_models import (
    JavaScriptDiscoveryJob, StartJavaScriptDiscoveryRequest, JavaScriptDiscoveryStats,
    JavaScriptSearchRequest, JavaScriptDiscoveryResult, JavaScriptTool, EndpointInfo,
    KeywordInfo, JSFileInfo
)
from ..services.database import get_database
from ..services.javascript_service import javascript_service

router = APIRouter(tags=["javascript"])
logger = logging.getLogger(__name__)

@router.post("/targets/{target_id}/analyze-javascript", response_model=JavaScriptDiscoveryJob)
async def start_javascript_analysis(
    target_id: str, 
    request: StartJavaScriptDiscoveryRequest,
    background_tasks: BackgroundTasks
):
    """Start JavaScript discovery and endpoint analysis for a target's subdomains"""
    try:
        db = get_database()
        
        # Check if target exists
        target = await db.targets.find_one({"id": target_id})
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Get live subdomains from latest liveness job
        liveness_job = await db.liveness_jobs.find_one(
            {"target_id": target_id, "status": {"$in": ["completed", "partial"]}},
            sort=[("completed_at", -1)]
        )
        
        if not liveness_job or not liveness_job.get("results"):
            raise HTTPException(
                status_code=400, 
                detail="No live subdomains found for this target. Please run liveness check first."
            )
        
        # Extract live subdomain list
        live_subdomains = [
            result["subdomain"] for result in liveness_job["results"] 
            if result.get("is_alive", False)
        ]
        
        if not live_subdomains:
            raise HTTPException(
                status_code=400, 
                detail="No live subdomains found. Please ensure liveness check has found live hosts."
            )
        
        # Check if there's already a running JavaScript analysis job
        existing_job = await db.javascript_jobs.find_one({
            "target_id": target_id,
            "status": {"$in": ["pending", "running"]}
        })
        if existing_job:
            raise HTTPException(
                status_code=400, 
                detail="JavaScript analysis already running for this target"
            )
        
        # Create initial job record
        job = JavaScriptDiscoveryJob(
            target_id=target_id,
            domain=target["domain"],
            subdomains=live_subdomains,
            status="pending",
            notes=request.notes,
            total_hosts=len(live_subdomains)
        )
        
        # Insert job into database
        await db.javascript_jobs.insert_one(job.dict())
        
        # Start JavaScript analysis in background
        tools = request.tools if request.tools else list(JavaScriptTool)
        background_tasks.add_task(
            javascript_service.analyze_javascript_files,
            live_subdomains,
            target_id,
            target["domain"],
            tools,
            request.include_external_js,
            request.deep_analysis,
            request.keyword_extraction
        )
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting JavaScript analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/targets/{target_id}/javascript-results", response_model=List[JavaScriptDiscoveryResult])
async def get_target_javascript_results(
    target_id: str,
    limit: int = 100,
    offset: int = 0,
    include_external: bool = False,
    min_confidence: float = 0.0
):
    """Get JavaScript analysis results for a target"""
    try:
        db = get_database()
        
        # Check if target exists
        target = await db.targets.find_one({"id": target_id})
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Get the latest completed JavaScript analysis job
        job = await db.javascript_jobs.find_one(
            {"target_id": target_id, "status": {"$in": ["completed", "partial"]}},
            sort=[("completed_at", -1)]
        )
        
        if not job:
            return []
        
        # Extract results from job
        results = job.get("results", [])
        
        # Apply filters
        filtered_results = []
        for result_data in results:
            try:
                result = JavaScriptDiscoveryResult(**result_data)
                
                # Filter endpoints by confidence
                if min_confidence > 0.0:
                    result.endpoints = [
                        ep for ep in result.endpoints 
                        if ep.confidence_score >= min_confidence
                    ]
                
                # Filter keywords by confidence
                if min_confidence > 0.0:
                    result.keywords = [
                        kw for kw in result.keywords 
                        if kw.confidence_score >= min_confidence
                    ]
                
                # Filter external JS files if not requested
                if not include_external:
                    result.js_files = [
                        js for js in result.js_files 
                        if not js.is_external
                    ]
                
                # Update totals after filtering
                result.total_js_files = len(result.js_files)
                result.total_endpoints = len(result.endpoints)
                result.total_keywords = len(result.keywords)
                
                filtered_results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing result data: {e}")
                continue
        
        # Apply pagination
        paginated_results = filtered_results[offset:offset + limit]
        
        return paginated_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching JavaScript results: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/targets/{target_id}/endpoints", response_model=List[EndpointInfo])
async def get_target_endpoints(
    target_id: str,
    limit: int = 100,
    offset: int = 0,
    min_confidence: float = 0.5,
    endpoint_type: Optional[str] = None
):
    """Get discovered endpoints for a target"""
    try:
        db = get_database()
        
        # Check if target exists
        target = await db.targets.find_one({"id": target_id})
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Get the latest completed JavaScript analysis job
        job = await db.javascript_jobs.find_one(
            {"target_id": target_id, "status": {"$in": ["completed", "partial"]}},
            sort=[("completed_at", -1)]
        )
        
        if not job:
            return []
        
        # Extract all endpoints from all results
        all_endpoints = []
        for result_data in job.get("results", []):
            try:
                result = JavaScriptDiscoveryResult(**result_data)
                for endpoint in result.endpoints:
                    if endpoint.confidence_score >= min_confidence:
                        if not endpoint_type or endpoint.endpoint_type == endpoint_type:
                            all_endpoints.append(endpoint)
            except Exception as e:
                logger.error(f"Error processing endpoint data: {e}")
                continue
        
        # Sort by confidence score (highest first)
        all_endpoints.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Apply pagination
        paginated_endpoints = all_endpoints[offset:offset + limit]
        
        return paginated_endpoints
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching endpoints: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/targets/{target_id}/keywords", response_model=List[KeywordInfo])
async def get_target_keywords(
    target_id: str,
    limit: int = 100,
    offset: int = 0,
    min_confidence: float = 0.5,
    keyword_type: Optional[str] = None
):
    """Get discovered sensitive keywords for a target"""
    try:
        db = get_database()
        
        # Check if target exists
        target = await db.targets.find_one({"id": target_id})
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Get the latest completed JavaScript analysis job
        job = await db.javascript_jobs.find_one(
            {"target_id": target_id, "status": {"$in": ["completed", "partial"]}},
            sort=[("completed_at", -1)]
        )
        
        if not job:
            return []
        
        # Extract all keywords from all results
        all_keywords = []
        for result_data in job.get("results", []):
            try:
                result = JavaScriptDiscoveryResult(**result_data)
                for keyword in result.keywords:
                    if keyword.confidence_score >= min_confidence:
                        if not keyword_type or keyword.keyword_type == keyword_type:
                            all_keywords.append(keyword)
            except Exception as e:
                logger.error(f"Error processing keyword data: {e}")
                continue
        
        # Sort by confidence score (highest first)
        all_keywords.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Apply pagination
        paginated_keywords = all_keywords[offset:offset + limit]
        
        return paginated_keywords
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching keywords: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/javascript-jobs/{job_id}", response_model=JavaScriptDiscoveryJob)
async def get_javascript_job(job_id: str):
    """Get details of a specific JavaScript analysis job"""
    try:
        db = get_database()
        
        job = await db.javascript_jobs.find_one({"id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="JavaScript analysis job not found")
        
        # Remove MongoDB _id from the response
        job.pop("_id", None)
        return JavaScriptDiscoveryJob(**job)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching JavaScript job: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/targets/{target_id}/javascript-jobs", response_model=List[JavaScriptDiscoveryJob])
async def get_target_javascript_jobs(target_id: str, limit: int = 10):
    """Get JavaScript analysis jobs for a target"""
    try:
        db = get_database()
        
        # Check if target exists
        target = await db.targets.find_one({"id": target_id})
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Get JavaScript analysis jobs for this target
        jobs = await db.javascript_jobs.find(
            {"target_id": target_id}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Convert to JavaScriptDiscoveryJob objects
        result = []
        for job in jobs:
            job.pop("_id", None)
            result.append(JavaScriptDiscoveryJob(**job))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching JavaScript jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/javascript/stats", response_model=JavaScriptDiscoveryStats)
async def get_javascript_stats():
    """Get overall JavaScript analysis statistics"""
    try:
        db = get_database()
        
        # Get all JavaScript analysis jobs
        jobs = await db.javascript_jobs.find().to_list(1000)
        
        if not jobs:
            return JavaScriptDiscoveryStats(
                total_jobs=0,
                active_jobs=0,
                completed_jobs=0,
                failed_jobs=0,
                total_hosts_analyzed=0,
                total_js_files_discovered=0,
                total_endpoints_discovered=0,
                total_keywords_discovered=0,
                by_status={},
                by_tool_success_rate={},
                avg_execution_time=0,
                endpoint_type_distribution={},
                keyword_type_distribution={},
                top_discovered_endpoints=[]
            )
        
        # Calculate statistics
        total_jobs = len(jobs)
        active_jobs = len([j for j in jobs if j.get("status") in ["pending", "running"]])
        completed_jobs = len([j for j in jobs if j.get("status") == "completed"])
        failed_jobs = len([j for j in jobs if j.get("status") == "failed"])
        
        total_hosts_analyzed = sum(j.get("total_hosts", 0) for j in jobs)
        total_js_files_discovered = sum(j.get("total_js_files", 0) for j in jobs)
        total_endpoints_discovered = sum(j.get("total_endpoints", 0) for j in jobs)
        total_keywords_discovered = sum(j.get("total_keywords", 0) for j in jobs)
        
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
        if by_tool_success_rate:
            most_productive_tool = max(
                by_tool_success_rate.keys(),
                key=lambda t: by_tool_success_rate[t]
            )
        
        # Calculate endpoint type distribution
        endpoint_type_distribution = {}
        keyword_type_distribution = {}
        all_endpoints = []
        
        for job in jobs:
            for result in job.get("results", []):
                # Endpoint type distribution
                for endpoint in result.get("endpoints", []):
                    endpoint_type = endpoint.get("endpoint_type", "unknown")
                    endpoint_type_distribution[endpoint_type] = endpoint_type_distribution.get(endpoint_type, 0) + 1
                    all_endpoints.append(endpoint.get("url", ""))
                
                # Keyword type distribution
                for keyword in result.get("keywords", []):
                    keyword_type = keyword.get("keyword_type", "unknown")
                    keyword_type_distribution[keyword_type] = keyword_type_distribution.get(keyword_type, 0) + 1
        
        # Get top discovered endpoints (most common)
        from collections import Counter
        endpoint_counter = Counter(all_endpoints)
        top_discovered_endpoints = [endpoint for endpoint, count in endpoint_counter.most_common(10)]
        
        return JavaScriptDiscoveryStats(
            total_jobs=total_jobs,
            active_jobs=active_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            total_hosts_analyzed=total_hosts_analyzed,
            total_js_files_discovered=total_js_files_discovered,
            total_endpoints_discovered=total_endpoints_discovered,
            total_keywords_discovered=total_keywords_discovered,
            by_status=by_status,
            by_tool_success_rate=by_tool_success_rate,
            avg_execution_time=avg_execution_time,
            most_productive_tool=most_productive_tool,
            endpoint_type_distribution=endpoint_type_distribution,
            keyword_type_distribution=keyword_type_distribution,
            top_discovered_endpoints=top_discovered_endpoints
        )
        
    except Exception as e:
        logger.error(f"Error fetching JavaScript stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/javascript-tools/install")
async def install_javascript_tools(background_tasks: BackgroundTasks):
    """Install all JavaScript discovery tools"""
    try:
        # Start installation in background
        background_tasks.add_task(javascript_service.install_all_tools)
        
        return {
            "message": "JavaScript tools installation started",
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Error starting JavaScript tools installation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/javascript-tools/status")
async def get_javascript_tools_status():
    """Get installation status of all JavaScript discovery tools"""
    try:
        status = {}
        for tool in JavaScriptTool:
            status[tool.value] = await javascript_service.check_tool_installation(tool)
        
        return {
            "tools": status,
            "total_tools": len(JavaScriptTool),
            "installed_tools": sum(1 for installed in status.values() if installed)
        }
        
    except Exception as e:
        logger.error(f"Error checking JavaScript tools status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")