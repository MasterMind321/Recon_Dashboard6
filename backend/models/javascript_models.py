from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class JavaScriptTool(str, Enum):
    SUBJS = "subjs"
    XNLINKFINDER = "xnlinkfinder"
    LINKFINDER = "linkfinder"
    GETJSWORDS = "getjswords"
    JSPARSER = "jsparser"
    JSBEAUTIFIER = "jsbeautifier"

class JavaScriptDiscoveryStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Some tools failed but others succeeded

class EndpointType(str, Enum):
    API = "api"
    AJAX = "ajax"
    WEBSOCKET = "websocket"
    GRAPHQL = "graphql"
    REST = "rest"
    JSONRPC = "jsonrpc"
    UNKNOWN = "unknown"

class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    UNKNOWN = "UNKNOWN"

class JSFileInfo(BaseModel):
    url: str
    size: Optional[int] = None
    content_type: Optional[str] = None
    source_page: str  # Which page/subdomain this JS was found on
    is_external: bool = False  # Whether it's hosted on external domain
    is_minified: bool = False
    discovered_by: List[JavaScriptTool] = Field(default_factory=list)
    extracted_at: datetime = Field(default_factory=datetime.utcnow)

class EndpointInfo(BaseModel):
    url: str
    method: HTTPMethod = HTTPMethod.UNKNOWN
    endpoint_type: EndpointType = EndpointType.UNKNOWN
    parameters: List[str] = Field(default_factory=list)
    source_js_file: str  # Which JS file this endpoint was found in
    confidence_score: float = 0.0  # 0.0 to 1.0, how confident we are this is a real endpoint
    discovered_by: List[JavaScriptTool] = Field(default_factory=list)
    extracted_at: datetime = Field(default_factory=datetime.utcnow)

class KeywordInfo(BaseModel):
    keyword: str
    context: str  # Surrounding context where keyword was found
    keyword_type: str  # "api_key", "password", "token", "secret", "config", etc.
    source_js_file: str
    confidence_score: float = 0.0
    discovered_by: List[JavaScriptTool] = Field(default_factory=list)
    extracted_at: datetime = Field(default_factory=datetime.utcnow)

class JavaScriptDiscoveryResult(BaseModel):
    subdomain: str
    js_files: List[JSFileInfo] = Field(default_factory=list)
    endpoints: List[EndpointInfo] = Field(default_factory=list)
    keywords: List[KeywordInfo] = Field(default_factory=list)
    total_js_files: int = 0
    total_endpoints: int = 0
    total_keywords: int = 0
    checked_by: List[JavaScriptTool] = Field(default_factory=list)
    last_checked: datetime = Field(default_factory=datetime.utcnow)

class JavaScriptToolResult(BaseModel):
    tool: JavaScriptTool
    status: str  # "success", "failed", "timeout"
    execution_time: float  # seconds
    hosts_checked: int
    js_files_found: int
    endpoints_found: int
    keywords_found: int
    error_message: Optional[str] = None
    raw_output: Optional[str] = None

class JavaScriptDiscoveryJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_id: str
    domain: str
    subdomains: List[str] = Field(default_factory=list)
    status: JavaScriptDiscoveryStatus = JavaScriptDiscoveryStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_hosts: int = 0
    total_js_files: int = 0
    total_endpoints: int = 0
    total_keywords: int = 0
    tools_executed: List[JavaScriptToolResult] = Field(default_factory=list)
    results: List[JavaScriptDiscoveryResult] = Field(default_factory=list)
    notes: Optional[str] = None

class StartJavaScriptDiscoveryRequest(BaseModel):
    tools: Optional[List[JavaScriptTool]] = None  # If None, use all tools
    include_external_js: bool = False  # Whether to analyze external JS files
    deep_analysis: bool = True  # Whether to beautify and deeply analyze JS
    keyword_extraction: bool = True  # Whether to extract sensitive keywords
    notes: Optional[str] = None

class JavaScriptDiscoveryStats(BaseModel):
    total_jobs: int
    active_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_hosts_analyzed: int
    total_js_files_discovered: int
    total_endpoints_discovered: int
    total_keywords_discovered: int
    by_status: Dict[str, int]
    by_tool_success_rate: Dict[str, float]
    avg_execution_time: float
    most_productive_tool: Optional[str] = None
    endpoint_type_distribution: Dict[str, int]
    keyword_type_distribution: Dict[str, int]
    top_discovered_endpoints: List[str] = Field(default_factory=list)

class JavaScriptSearchRequest(BaseModel):
    target_id: Optional[str] = None
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    endpoint_type: Optional[EndpointType] = None
    keyword_type: Optional[str] = None
    limit: int = 100
    offset: int = 0
    include_external: bool = False
    min_confidence: float = 0.0