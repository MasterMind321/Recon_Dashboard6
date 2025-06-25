from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class LivenessTool(str, Enum):
    HTTPX = "httpx"
    CDNCHECK = "cdncheck"
    TLSX = "tlsx"
    GOWITNESS = "gowitness"
    WAFW00F = "wafw00f"
    WHATWEB = "whatweb"
    WAPPALYZER = "wappalyzer"
    CMSEEK = "cmseek"

class LivenessStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Some tools failed but others succeeded

class TLSInfo(BaseModel):
    issuer: Optional[str] = None
    subject: Optional[str] = None
    san: List[str] = Field(default_factory=list)
    expires: Optional[datetime] = None
    signature_algorithm: Optional[str] = None
    version: Optional[str] = None

class TechStackInfo(BaseModel):
    cms: Optional[str] = None
    server: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    javascript_libraries: List[str] = Field(default_factory=list)
    analytics: List[str] = Field(default_factory=list)

class CDNWAFInfo(BaseModel):
    cdn_provider: Optional[str] = None
    waf_provider: Optional[str] = None
    is_behind_cdn: bool = False
    is_behind_waf: bool = False
    waf_type: Optional[str] = None

class LivenessResult(BaseModel):
    subdomain: str
    is_alive: bool = False
    status_code: Optional[int] = None
    response_time: Optional[float] = None  # in seconds
    content_length: Optional[int] = None
    title: Optional[str] = None
    server: Optional[str] = None
    location: Optional[str] = None
    tls_info: Optional[TLSInfo] = None
    tech_stack: Optional[TechStackInfo] = None
    cdn_waf_info: Optional[CDNWAFInfo] = None
    screenshot_base64: Optional[str] = None  # Base64 encoded screenshot
    checked_by: List[LivenessTool] = Field(default_factory=list)
    last_checked: datetime = Field(default_factory=datetime.utcnow)
    response_headers: Dict[str, str] = Field(default_factory=dict)

class LivenessToolResult(BaseModel):
    tool: LivenessTool
    status: str  # "success", "failed", "timeout"
    execution_time: float  # seconds
    hosts_checked: int
    alive_hosts: int
    error_message: Optional[str] = None
    raw_output: Optional[str] = None

class LivenessJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_id: str
    domain: str
    subdomains: List[str] = Field(default_factory=list)
    status: LivenessStatus = LivenessStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_hosts: int = 0
    alive_hosts: int = 0
    tools_executed: List[LivenessToolResult] = Field(default_factory=list)
    results: List[LivenessResult] = Field(default_factory=list)
    notes: Optional[str] = None

class StartLivenessRequest(BaseModel):
    tools: Optional[List[LivenessTool]] = None  # If None, use all tools
    include_screenshots: bool = True
    include_tech_stack: bool = True
    include_tls_info: bool = True
    notes: Optional[str] = None

class LivenessStats(BaseModel):
    total_jobs: int
    active_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_hosts_checked: int
    total_alive_hosts: int
    by_status: Dict[str, int]
    by_tool_success_rate: Dict[str, float]
    avg_execution_time: float
    most_reliable_tool: Optional[str] = None
    tech_stack_distribution: Dict[str, int]
    cdn_waf_distribution: Dict[str, int]

class LivenessSearchRequest(BaseModel):
    target_id: Optional[str] = None
    domain: Optional[str] = None
    limit: int = 100
    offset: int = 0
    alive_only: bool = True
    with_screenshots: bool = False
    with_tech_stack: bool = False