from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Enums
class ToolCategory(str, Enum):
    SUBDOMAIN_ENUMERATION = "subdomain_enumeration"
    LIVENESS_FINGERPRINTING = "liveness_fingerprinting"
    JAVASCRIPT_ENDPOINT = "javascript_endpoint"
    VULNERABILITY_SCANNING = "vulnerability_scanning"
    HISTORICAL_DATA = "historical_data"
    DIRECTORY_FUZZING = "directory_fuzzing"
    PORT_SCANNING = "port_scanning"
    CLOUD_RECON = "cloud_recon"
    REPORTING_NOTIFICATION = "reporting_notification"
    UTILITY_MISC = "utility_misc"

class InstallationStatus(str, Enum):
    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    UPDATING = "updating"
    FAILED = "failed"
    OUTDATED = "outdated"

class ToolStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class ToolConfig(BaseModel):
    name: str
    value: Any
    description: Optional[str] = None

class ReconTool(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: ToolCategory
    description: str
    install_command: str
    usage_description: str
    installation_status: InstallationStatus = InstallationStatus.NOT_INSTALLED
    tool_status: ToolStatus = ToolStatus.OFFLINE
    version: Optional[str] = None
    last_updated: Optional[datetime] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    configuration: List[ToolConfig] = []
    icon_color: str = "#06b6d4"  # Default cyan
    category_color: str = "#3b82f6"  # Default blue

class ToolUpdate(BaseModel):
    installation_status: Optional[InstallationStatus] = None
    tool_status: Optional[ToolStatus] = None
    version: Optional[str] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    configuration: Optional[List[ToolConfig]] = None

class ScanResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target: str
    tool_name: str
    category: ToolCategory
    status: str
    results: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    output_file: Optional[str] = None

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
