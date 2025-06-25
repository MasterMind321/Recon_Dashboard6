from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
import logging

from ..models.target_models import (
    Target, CreateTargetRequest, UpdateTargetRequest, TargetStats, 
    TargetStatus, TargetType, ScanSeverity
)
from ..services.database import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/targets", response_model=List[Target])
async def get_targets(
    status: Optional[TargetStatus] = None,
    type: Optional[TargetType] = None
):
    """Get all targets with optional filtering"""
    try:
        db = get_database()
        filter_query = {}
        
        if status:
            filter_query["status"] = status
        if type:
            filter_query["type"] = type
            
        targets = list(db.targets.find(filter_query))
        
        # Convert MongoDB documents to Target models
        result = []
        for target in targets:
            target["_id"] = str(target["_id"]) if "_id" in target else None
            # Remove MongoDB _id from the response
            target.pop("_id", None)
            result.append(Target(**target))
            
        return result
        
    except Exception as e:
        logger.error(f"Error fetching targets: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/targets", response_model=Target)
async def create_target(target_request: CreateTargetRequest):
    """Create a new target"""
    try:
        db = get_database()
        
        # Check if target already exists
        existing = db.targets.find_one({"domain": target_request.domain})
        if existing:
            raise HTTPException(status_code=400, detail="Target already exists")
        
        # Create new target
        target = Target(
            domain=target_request.domain,
            type=target_request.type,
            workflow=target_request.workflow,
            notes=target_request.notes
        )
        
        # Insert into database
        target_dict = target.dict()
        db.targets.insert_one(target_dict)
        
        return target
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating target: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/targets/{target_id}", response_model=Target)
async def get_target(target_id: str):
    """Get a specific target by ID"""
    try:
        db = get_database()
        target = db.targets.find_one({"id": target_id})
        
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
            
        # Remove MongoDB _id from the response
        target.pop("_id", None)
        return Target(**target)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching target: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/targets/{target_id}", response_model=Target)
async def update_target(target_id: str, update_request: UpdateTargetRequest):
    """Update a target"""
    try:
        db = get_database()
        
        # Find existing target
        existing = db.targets.find_one({"id": target_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Prepare update data
        update_data = {}
        if update_request.domain is not None:
            update_data["domain"] = update_request.domain
        if update_request.type is not None:
            update_data["type"] = update_request.type
        if update_request.status is not None:
            update_data["status"] = update_request.status
        if update_request.workflow is not None:
            update_data["workflow"] = update_request.workflow
        if update_request.notes is not None:
            update_data["notes"] = update_request.notes
            
        update_data["updated_at"] = datetime.utcnow()
        
        # Update in database
        db.targets.update_one({"id": target_id}, {"$set": update_data})
        
        # Fetch and return updated target
        updated_target = db.targets.find_one({"id": target_id})
        updated_target.pop("_id", None)
        return Target(**updated_target)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating target: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/targets/{target_id}")
async def delete_target(target_id: str):
    """Delete a target"""
    try:
        db = get_database()
        
        # Check if target exists
        existing = db.targets.find_one({"id": target_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Delete the target
        result = db.targets.delete_one({"id": target_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Target not found")
            
        # Also delete related scan results
        db.scan_results.delete_many({"target": existing["domain"]})
        
        return {"message": "Target deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting target: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/targets/{target_id}/scan")
async def start_scan(target_id: str):
    """Start a scan for the target"""
    try:
        db = get_database()
        
        # Find the target
        target = db.targets.find_one({"id": target_id})
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Update target status to scanning
        db.targets.update_one(
            {"id": target_id}, 
            {
                "$set": {
                    "status": TargetStatus.SCANNING,
                    "last_scan": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Here you would typically trigger your actual scanning workflow
        # For now, we'll just update the status
        
        # Fetch and return updated target
        updated_target = db.targets.find_one({"id": target_id})
        updated_target.pop("_id", None)
        return Target(**updated_target)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting scan: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/targets/stats", response_model=TargetStats)
async def get_target_stats():
    """Get target statistics"""
    try:
        db = get_database()
        
        # Get all targets
        targets = list(db.targets.find())
        
        # Calculate statistics
        total_targets = len(targets)
        active_scans = len([t for t in targets if t.get("status") == "scanning"])
        total_subdomains = sum(t.get("subdomains", 0) for t in targets)
        total_vulnerabilities = sum(t.get("vulnerabilities", 0) for t in targets)
        
        # Group by status
        by_status = {}
        for status in TargetStatus:
            by_status[status.value] = len([t for t in targets if t.get("status") == status.value])
        
        # Group by type
        by_type = {}
        for target_type in TargetType:
            by_type[target_type.value] = len([t for t in targets if t.get("type") == target_type.value])
        
        # Group by severity
        by_severity = {}
        for severity in ScanSeverity:
            by_severity[severity.value] = len([t for t in targets if t.get("severity") == severity.value])
        
        return TargetStats(
            total_targets=total_targets,
            active_scans=active_scans,
            total_subdomains=total_subdomains,
            total_vulnerabilities=total_vulnerabilities,
            by_status=by_status,
            by_type=by_type,
            by_severity=by_severity
        )
        
    except Exception as e:
        logger.error(f"Error fetching target stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")