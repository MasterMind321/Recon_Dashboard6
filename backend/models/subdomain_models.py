from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class SubdomainTool(str, Enum):
    SUBFINDER = "subfinder"
    AMASS = "amass"
    CRTSH = "crtsh"
    PUREDNS = "puredns"
    DNSX = "dnsx"
    GOTATOR = "gotator"
    DNSGEN = "dnsgen"
    GITHUB_SUBDOMAINS = "github-subdomains"
    MAPCIDR = "mapcidr"
    ASNLOOKUP = "asnlookup"

class EnumerationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Some tools failed but others succeeded

class SubdomainResult(BaseModel):
    subdomain: str
    discovered_by: List[SubdomainTool]  # Which tools found this subdomain
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    ip_addresses: List[str] = Field(default_factory=list)
    is_alive: Optional[bool] = None
    status_code: Optional[int] = None
    technologies: List[str] = Field(default_factory=list)

class ToolResult(BaseModel):
    tool: SubdomainTool
    status: str  # "success", "failed", "timeout"
    execution_time: float  # seconds
    subdomains_found: int
    error_message: Optional[str] = None
    raw_output: Optional[str] = None

class EnumerationJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_id: str
    domain: str
    status: EnumerationStatus = EnumerationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_subdomains: int = 0
    unique_subdomains: int = 0
    tools_executed: List[ToolResult] = Field(default_factory=list)
    subdomains: List[SubdomainResult] = Field(default_factory=list)
    notes: Optional[str] = None

class StartEnumerationRequest(BaseModel):
    tools: Optional[List[SubdomainTool]] = None  # If None, use all tools
    notes: Optional[str] = None

class EnumerationStats(BaseModel):
    total_jobs: int
    active_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_subdomains_discovered: int
    by_status: Dict[str, int]
    by_tool_success_rate: Dict[str, float]
    avg_execution_time: float
    most_productive_tool: Optional[str] = None

class SubdomainSearchRequest(BaseModel):
    target_id: Optional[str] = None
    domain: Optional[str] = None
    limit: int = 100
    offset: int = 0
    alive_only: bool = False