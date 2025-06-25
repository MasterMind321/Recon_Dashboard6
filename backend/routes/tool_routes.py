from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from ..models.tool_models import ReconTool, ToolUpdate, ToolCategory, InstallationStatus, ToolStatus
from ..data.tool_data import initialize_tools
from ..services.database import get_database

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("", response_model=List[ReconTool])
async def get_all_tools():
    """Get all reconnaissance tools"""
    db = get_database()
    await initialize_tools()  # Ensure tools are initialized
    tools = await db.recon_tools.find().to_list(1000)
    return [ReconTool(**tool) for tool in tools]


@router.get("/category/{category}", response_model=List[ReconTool])
async def get_tools_by_category(category: ToolCategory):
    """Get tools by category"""
    db = get_database()
    await initialize_tools()
    tools = await db.recon_tools.find({"category": category}).to_list(1000)
    return [ReconTool(**tool) for tool in tools]


@router.put("/{tool_id}", response_model=ReconTool)
async def update_tool(tool_id: str, tool_update: ToolUpdate):
    """Update tool status and configuration"""
    db = get_database()
    update_data = {k: v for k, v in tool_update.dict().items() if v is not None}
    if update_data:
        update_data["last_updated"] = datetime.utcnow()
        await db.recon_tools.update_one({"id": tool_id}, {"$set": update_data})
    
    updated_tool = await db.recon_tools.find_one({"id": tool_id})
    if updated_tool:
        return ReconTool(**updated_tool)
    else:
        raise HTTPException(status_code=404, detail="Tool not found")


@router.post("/{tool_id}/install")
async def install_tool(tool_id: str):
    """Initiate tool installation"""
    db = get_database()
    # Update tool status to installing
    await db.recon_tools.update_one(
        {"id": tool_id}, 
        {"$set": {"installation_status": InstallationStatus.UPDATING, "last_updated": datetime.utcnow()}}
    )
    return {"message": "Tool installation initiated", "tool_id": tool_id}


@router.get("/stats")
async def get_tool_stats():
    """Get tool installation and status statistics"""
    db = get_database()
    await initialize_tools()
    
    # Count tools by installation status
    installed_count = await db.recon_tools.count_documents({"installation_status": InstallationStatus.INSTALLED})
    not_installed_count = await db.recon_tools.count_documents({"installation_status": InstallationStatus.NOT_INSTALLED})
    failed_count = await db.recon_tools.count_documents({"installation_status": InstallationStatus.FAILED})
    outdated_count = await db.recon_tools.count_documents({"installation_status": InstallationStatus.OUTDATED})
    
    # Count tools by status
    online_count = await db.recon_tools.count_documents({"tool_status": ToolStatus.ONLINE})
    busy_count = await db.recon_tools.count_documents({"tool_status": ToolStatus.BUSY})
    
    # Count by category
    category_counts = {}
    for category in ToolCategory:
        count = await db.recon_tools.count_documents({"category": category})
        category_counts[category.value] = count
    
    return {
        "installation": {
            "installed": installed_count,
            "not_installed": not_installed_count,
            "failed": failed_count,  
            "outdated": outdated_count
        },
        "status": {
            "online": online_count,
            "busy": busy_count
        },
        "categories": category_counts
    }