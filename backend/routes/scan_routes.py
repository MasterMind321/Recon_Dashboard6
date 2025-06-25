from fastapi import APIRouter
from typing import List, Optional
from ..models.scan_models import ScanResult, StatusCheck, StatusCheckCreate
from ..services.database import get_database

router = APIRouter(tags=["scans"])


@router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    db = get_database()
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj


@router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    db = get_database()
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]


@router.get("/scan-results", response_model=List[ScanResult])
async def get_scan_results(target: Optional[str] = None, tool_name: Optional[str] = None):
    """Get scan results with optional filtering"""
    db = get_database()
    filter_query = {}
    if target:
        filter_query["target"] = {"$regex": target, "$options": "i"}
    if tool_name:
        filter_query["tool_name"] = tool_name
    
    results = await db.scan_results.find(filter_query).sort("start_time", -1).to_list(100)
    return [ScanResult(**result) for result in results]


@router.post("/scan-results", response_model=ScanResult)
async def create_scan_result(scan_result: ScanResult):
    """Create a new scan result"""
    db = get_database()
    await db.scan_results.insert_one(scan_result.dict())
    return scan_result