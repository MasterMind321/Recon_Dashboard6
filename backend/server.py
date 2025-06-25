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

# Import subdomain routes
from .routes.subdomain_routes import router as subdomain_router


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

# Initialize tools data
RECON_TOOLS_DATA = [
    # 🟦 1. Subdomain Enumeration
    {"name": "subfinder", "category": ToolCategory.SUBDOMAIN_ENUMERATION, "description": "Passive subdomain discovery", "install_command": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest", "usage_description": "Fast passive subdomain enumeration tool", "icon_color": "#3b82f6", "category_color": "#3b82f6"},
    {"name": "amass", "category": ToolCategory.SUBDOMAIN_ENUMERATION, "description": "Active/passive subdomain enum", "install_command": "go install -v github.com/owasp-amass/amass/v4/...@master", "usage_description": "In-depth attack surface mapping and asset discovery", "icon_color": "#3b82f6", "category_color": "#3b82f6"},
    {"name": "crt.sh parser", "category": ToolCategory.SUBDOMAIN_ENUMERATION, "description": "Certificate Transparency search", "install_command": "pip install crtsh", "usage_description": "Certificate transparency log search", "icon_color": "#3b82f6", "category_color": "#3b82f6"},
    {"name": "puredns", "category": ToolCategory.SUBDOMAIN_ENUMERATION, "description": "DNS resolution + wildcard detection", "install_command": "go install github.com/d3mondev/puredns/v2@latest", "usage_description": "Fast domain resolver and subdomain bruteforcing tool", "icon_color": "#3b82f6", "category_color": "#3b82f6"},
    {"name": "dnsx", "category": ToolCategory.SUBDOMAIN_ENUMERATION, "description": "Fast DNS resolution", "install_command": "go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest", "usage_description": "Fast and multi-purpose DNS toolkit", "icon_color": "#3b82f6", "category_color": "#3b82f6"},
    {"name": "gotator", "category": ToolCategory.SUBDOMAIN_ENUMERATION, "description": "Subdomain permutation", "install_command": "go install github.com/Josue87/gotator@latest", "usage_description": "Generate DNS wordlists through permutations", "icon_color": "#3b82f6", "category_color": "#3b82f6"},
    {"name": "dnsgen", "category": ToolCategory.SUBDOMAIN_ENUMERATION, "description": "Wordlist-based permutations", "install_command": "pip install dnsgen", "usage_description": "Generate combinations of domain names based on wordlists", "icon_color": "#3b82f6", "category_color": "#3b82f6"},
    {"name": "github-subdomains", "category": ToolCategory.SUBDOMAIN_ENUMERATION, "description": "GitHub scraping for subdomains", "install_command": "go install github.com/gwen001/github-subdomains@latest", "usage_description": "Find subdomains from GitHub", "icon_color": "#3b82f6", "category_color": "#3b82f6"},
    {"name": "mapcidr", "category": ToolCategory.SUBDOMAIN_ENUMERATION, "description": "ASN to CIDR mapping", "install_command": "go install -v github.com/projectdiscovery/mapcidr/cmd/mapcidr@latest", "usage_description": "Utility for performing multiple operations for a given subnet/CIDR ranges", "icon_color": "#3b82f6", "category_color": "#3b82f6"},
    {"name": "asnlookup", "category": ToolCategory.SUBDOMAIN_ENUMERATION, "description": "ASN to IP/Subdomain correlation", "install_command": "pip install asnlookup", "usage_description": "Lookup ASN and organization information", "icon_color": "#3b82f6", "category_color": "#3b82f6"},

    # 🟩 2. Liveness, Fingerprinting & Screenshots
    {"name": "httpx", "category": ToolCategory.LIVENESS_FINGERPRINTING, "description": "Liveness check with response info", "install_command": "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest", "usage_description": "Fast and multi-purpose HTTP toolkit", "icon_color": "#10b981", "category_color": "#10b981"},
    {"name": "cdncheck", "category": ToolCategory.LIVENESS_FINGERPRINTING, "description": "CDN and WAF fingerprinting", "install_command": "Built into httpx", "usage_description": "CDN and WAF detection utility", "icon_color": "#10b981", "category_color": "#10b981"},
    {"name": "tlsx", "category": ToolCategory.LIVENESS_FINGERPRINTING, "description": "TLS certificate info gathering", "install_command": "go install github.com/projectdiscovery/tlsx/cmd/tlsx@latest", "usage_description": "Fast and configurable TLS grabber", "icon_color": "#10b981", "category_color": "#10b981"},
    {"name": "gowitness", "category": ToolCategory.LIVENESS_FINGERPRINTING, "description": "Web screenshots of live hosts", "install_command": "go install github.com/sensepost/gowitness@latest", "usage_description": "Web screenshot utility using Chrome Headless", "icon_color": "#10b981", "category_color": "#10b981"},
    {"name": "wafw00f", "category": ToolCategory.LIVENESS_FINGERPRINTING, "description": "Detect WAF in front of site", "install_command": "pip install wafw00f", "usage_description": "Identify and fingerprint Web Application Firewall products", "icon_color": "#10b981", "category_color": "#10b981"},
    {"name": "whatweb", "category": ToolCategory.LIVENESS_FINGERPRINTING, "description": "Web tech stack detection", "install_command": "apt install whatweb", "usage_description": "Web scanner that recognizes web technologies", "icon_color": "#10b981", "category_color": "#10b981"},
    {"name": "wappalyzer", "category": ToolCategory.LIVENESS_FINGERPRINTING, "description": "Alternative to WhatWeb (Node.js)", "install_command": "npm install -g wappalyzer-cli", "usage_description": "Identify technologies used on websites", "icon_color": "#10b981", "category_color": "#10b981"},
    {"name": "CMSeeK", "category": ToolCategory.LIVENESS_FINGERPRINTING, "description": "CMS fingerprinting and CVE mapping", "install_command": "git clone https://github.com/Tuhinshubhra/CMSeeK", "usage_description": "CMS detection and exploitation suite", "icon_color": "#10b981", "category_color": "#10b981"},

    # 🟨 3. JavaScript/Endpoint Discovery
    {"name": "subjs", "category": ToolCategory.JAVASCRIPT_ENDPOINT, "description": "Extract JS URLs from HTML", "install_command": "go install -v github.com/lc/subjs@latest", "usage_description": "Fetches javascript files from a list of URLS or subdomains", "icon_color": "#f59e0b", "category_color": "#f59e0b"},
    {"name": "xnLinkFinder", "category": ToolCategory.JAVASCRIPT_ENDPOINT, "description": "Extract endpoints from JS", "install_command": "pip install xnLinkFinder", "usage_description": "Discovery of endpoints in JavaScript files", "icon_color": "#f59e0b", "category_color": "#f59e0b"},
    {"name": "linkfinder", "category": ToolCategory.JAVASCRIPT_ENDPOINT, "description": "Regex-based endpoint extractor from JS", "install_command": "pip install linkfinder", "usage_description": "Discover endpoints and their parameters in JavaScript files", "icon_color": "#f59e0b", "category_color": "#f59e0b"},
    {"name": "getjswords", "category": ToolCategory.JAVASCRIPT_ENDPOINT, "description": "Parameter & keyword discovery in JS", "install_command": "git clone https://github.com/m4ll0k/GetJSWords", "usage_description": "Extract words from JavaScript files", "icon_color": "#f59e0b", "category_color": "#f59e0b"},
    {"name": "JSParser", "category": ToolCategory.JAVASCRIPT_ENDPOINT, "description": "Static JS analysis (regex)", "install_command": "pip install jsparser", "usage_description": "Parse JavaScript files for URLs and endpoints", "icon_color": "#f59e0b", "category_color": "#f59e0b"},
    {"name": "jsbeautifier", "category": ToolCategory.JAVASCRIPT_ENDPOINT, "description": "Beautify/minify JS for parsing", "install_command": "pip install jsbeautifier", "usage_description": "Beautify, unpack or deobfuscate JavaScript", "icon_color": "#f59e0b", "category_color": "#f59e0b"},

    # 🟥 4. Vulnerability Scanning
    {"name": "dalfox", "category": ToolCategory.VULNERABILITY_SCANNING, "description": "XSS scanner (param/context-aware)", "install_command": "go install github.com/hahwul/dalfox/v2@latest", "usage_description": "Powerful open-source XSS scanner and utility", "icon_color": "#ef4444", "category_color": "#ef4444"},
    {"name": "XSStrike", "category": ToolCategory.VULNERABILITY_SCANNING, "description": "XSS detection via headless browser", "install_command": "git clone https://github.com/s0md3v/XSStrike && pip install -r requirements.txt", "usage_description": "Advanced XSS detection suite", "icon_color": "#ef4444", "category_color": "#ef4444"},
    {"name": "sqlmap", "category": ToolCategory.VULNERABILITY_SCANNING, "description": "SQLi scanner (auto-detection)", "install_command": "apt install sqlmap", "usage_description": "Automatic SQL injection and database takeover tool", "icon_color": "#ef4444", "category_color": "#ef4444"},
    {"name": "crlfuzz", "category": ToolCategory.VULNERABILITY_SCANNING, "description": "CRLF Injection tester", "install_command": "go install github.com/dwisiswant0/crlfuzz/cmd/crlfuzz@latest", "usage_description": "Fast tool to scan CRLF vulnerability", "icon_color": "#ef4444", "category_color": "#ef4444"},
    {"name": "qsreplace", "category": ToolCategory.VULNERABILITY_SCANNING, "description": "Replace values in URLs (open redirect)", "install_command": "go install github.com/tomnomnom/qsreplace@latest", "usage_description": "Accept URLs on stdin, replace all query string values with a user-supplied value", "icon_color": "#ef4444", "category_color": "#ef4444"},
    {"name": "nuclei", "category": ToolCategory.VULNERABILITY_SCANNING, "description": "Vulnerability templated scanner", "install_command": "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest", "usage_description": "Fast and customizable vulnerability scanner", "icon_color": "#ef4444", "category_color": "#ef4444"},
    {"name": "nuclei-templates", "category": ToolCategory.VULNERABILITY_SCANNING, "description": "Template repo for nuclei", "install_command": "git clone https://github.com/projectdiscovery/nuclei-templates", "usage_description": "Community-curated list of templates for nuclei", "icon_color": "#ef4444", "category_color": "#ef4444"},

    # 🟪 5. Historical Data & Archive Recon
    {"name": "gau", "category": ToolCategory.HISTORICAL_DATA, "description": "Get all URLs (Wayback, etc.)", "install_command": "go install github.com/lc/gau/v2/cmd/gau@latest", "usage_description": "Fetch known URLs from AlienVault's Open Threat Exchange, the Wayback Machine, and Common Crawl", "icon_color": "#8b5cf6", "category_color": "#8b5cf6"},
    {"name": "waybackurls", "category": ToolCategory.HISTORICAL_DATA, "description": "Archived URLs from Internet Archive", "install_command": "go install github.com/tomnomnom/waybackurls@latest", "usage_description": "Fetch all the URLs that the Wayback Machine knows about for a domain", "icon_color": "#8b5cf6", "category_color": "#8b5cf6"},
    {"name": "urless", "category": ToolCategory.HISTORICAL_DATA, "description": "Fast historical URL fetching", "install_command": "go install github.com/xnl-h4ck3r/urless@latest", "usage_description": "De-duplicate URLs and filter out uninteresting URLs", "icon_color": "#8b5cf6", "category_color": "#8b5cf6"},

    # 🟧 6. Directory & File Fuzzing
    {"name": "ffuf", "category": ToolCategory.DIRECTORY_FUZZING, "description": "Directory brute-forcing & fuzzing", "install_command": "go install github.com/ffuf/ffuf/v2@latest", "usage_description": "Fast web fuzzer written in Go", "icon_color": "#f97316", "category_color": "#f97316"},
    {"name": "feroxbuster", "category": ToolCategory.DIRECTORY_FUZZING, "description": "Recursive fuzzing", "install_command": "apt install feroxbuster", "usage_description": "Fast content discovery tool written in Rust", "icon_color": "#f97316", "category_color": "#f97316"},
    {"name": "dirsearch", "category": ToolCategory.DIRECTORY_FUZZING, "description": "Python-based dir scanning", "install_command": "git clone https://github.com/maurosoria/dirsearch", "usage_description": "Web path scanner", "icon_color": "#f97316", "category_color": "#f97316"},
    {"name": "byp4xx", "category": ToolCategory.DIRECTORY_FUZZING, "description": "403 bypass techniques", "install_command": "go install github.com/lobuhi/byp4xx@latest", "usage_description": "40X/HTTP bypasser in Go", "icon_color": "#f97316", "category_color": "#f97316"},

    # 🟫 7. Port Scanning & Network Enumeration
    {"name": "nmap", "category": ToolCategory.PORT_SCANNING, "description": "Port scanning & service detection", "install_command": "apt install nmap", "usage_description": "Network discovery and security auditing", "icon_color": "#a16207", "category_color": "#a16207"},
    {"name": "smap", "category": ToolCategory.PORT_SCANNING, "description": "Fast nmap-compatible port scanner", "install_command": "go install github.com/projectdiscovery/smap/cmd/smap@latest", "usage_description": "Drop-in replacement for Nmap powered by Shodan.io", "icon_color": "#a16207", "category_color": "#a16207"},
    {"name": "naabu", "category": ToolCategory.PORT_SCANNING, "description": "Lightweight port scanner", "install_command": "go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest", "usage_description": "Fast port scanner written in go with focus on reliability and simplicity", "icon_color": "#a16207", "category_color": "#a16207"},
    {"name": "masscan", "category": ToolCategory.PORT_SCANNING, "description": "Ultra-fast port scanning", "install_command": "apt install masscan", "usage_description": "TCP port scanner, spews SYN packets asynchronously", "icon_color": "#a16207", "category_color": "#a16207"},
    {"name": "brutespray", "category": ToolCategory.PORT_SCANNING, "description": "Brute-force SSH, RDP, FTP, etc.", "install_command": "git clone https://github.com/x90skysn3k/brutespray", "usage_description": "Brute-forcing tool that can be used during penetration tests", "icon_color": "#a16207", "category_color": "#a16207"},

    # 🟦 8. Cloud & S3 Recon
    {"name": "s3scanner", "category": ToolCategory.CLOUD_RECON, "description": "Public bucket enumeration", "install_command": "go install github.com/sa7mon/s3scanner@latest", "usage_description": "Scan for misconfigured S3 buckets across S3-compatible APIs", "icon_color": "#0ea5e9", "category_color": "#0ea5e9"},
    {"name": "cloud_enum", "category": ToolCategory.CLOUD_RECON, "description": "AWS/Azure/GCP asset recon", "install_command": "git clone https://github.com/initstring/cloud_enum", "usage_description": "Multi-cloud OSINT tool designed to enumerate public resources", "icon_color": "#0ea5e9", "category_color": "#0ea5e9"},

    # 🟨 9. Reporting, Output, & Notification
    {"name": "notify", "category": ToolCategory.REPORTING_NOTIFICATION, "description": "Send alerts (Slack, Email, etc.)", "install_command": "go install -v github.com/projectdiscovery/notify/cmd/notify@latest", "usage_description": "Stream the output of several tools and publish it to different platforms", "icon_color": "#eab308", "category_color": "#eab308"},
    {"name": "unfurl", "category": ToolCategory.REPORTING_NOTIFICATION, "description": "URL parsing", "install_command": "go install github.com/tomnomnom/unfurl@latest", "usage_description": "Extract specific parts of URLs", "icon_color": "#eab308", "category_color": "#eab308"},
    {"name": "anew", "category": ToolCategory.REPORTING_NOTIFICATION, "description": "Deduplication utility", "install_command": "go install github.com/tomnomnom/anew@latest", "usage_description": "Tool for adding new lines to files, skipping duplicates", "icon_color": "#eab308", "category_color": "#eab308"},
    {"name": "interactsh-client", "category": ToolCategory.REPORTING_NOTIFICATION, "description": "OOB XSS, SSRF detection", "install_command": "go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest", "usage_description": "Out-of-band interaction gathering server and client library", "icon_color": "#eab308", "category_color": "#eab308"},

    # ⚙️ 10. Utility / Miscellaneous
    {"name": "fav-up", "category": ToolCategory.UTILITY_MISC, "description": "Favicon hashing (for CDN asset tracking)", "install_command": "git clone https://github.com/pielco11/fav-up", "usage_description": "IP lookup by favicon", "icon_color": "#6b7280", "category_color": "#6b7280"},
    {"name": "analyticsrelationships", "category": ToolCategory.UTILITY_MISC, "description": "Google Analytics asset tracking", "install_command": "git clone https://github.com/Josue87/AnalyticsRelationships", "usage_description": "Get related domains from Google Analytics IDs", "icon_color": "#6b7280", "category_color": "#6b7280"},
    {"name": "dsieve", "category": ToolCategory.UTILITY_MISC, "description": "Filter domains/subs by pattern", "install_command": "go install github.com/trickest/dsieve@latest", "usage_description": "Filter and enrich a list of subdomains by level", "icon_color": "#6b7280", "category_color": "#6b7280"},
    {"name": "cdnstake", "category": ToolCategory.UTILITY_MISC, "description": "Identify vulnerable CNAMEs", "install_command": "go install github.com/EdOverflow/cdnstake@latest", "usage_description": "Subdomain takeover vulnerability scanner", "icon_color": "#6b7280", "category_color": "#6b7280"},
    {"name": "inscope", "category": ToolCategory.UTILITY_MISC, "description": "Scope filtering engine", "install_command": "go install github.com/tomnomnom/inscope@latest", "usage_description": "Filter URLs to only include in-scope targets", "icon_color": "#6b7280", "category_color": "#6b7280"},
    {"name": "enumerepo", "category": ToolCategory.UTILITY_MISC, "description": "Git repo recon", "install_command": "git clone https://github.com/trickest/enumerepo", "usage_description": "List all public repositories for a user/organization", "icon_color": "#6b7280", "category_color": "#6b7280"},
    {"name": "gitleaks", "category": ToolCategory.UTILITY_MISC, "description": "Git secret scanning", "install_command": "go install github.com/gitleaks/gitleaks/v8@latest", "usage_description": "Detect and prevent secrets in git repos", "icon_color": "#6b7280", "category_color": "#6b7280"},
    {"name": "trufflehog", "category": ToolCategory.UTILITY_MISC, "description": "Advanced git leak scanner", "install_command": "pip install trufflehog", "usage_description": "Find credentials accidentally committed to git repos", "icon_color": "#6b7280", "category_color": "#6b7280"},
    {"name": "gitdorks_go", "category": ToolCategory.UTILITY_MISC, "description": "GitHub dork scanner", "install_command": "go install github.com/damit5/gitdorks_go@latest", "usage_description": "Scan github for sensitive information", "icon_color": "#6b7280", "category_color": "#6b7280"},
]

async def initialize_tools():
    """Initialize tools in database if not already present"""
    for tool_data in RECON_TOOLS_DATA:
        existing_tool = await db.recon_tools.find_one({"name": tool_data["name"]})
        if not existing_tool:
            tool = ReconTool(**tool_data)
            await db.recon_tools.insert_one(tool.dict())

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "ReconFlow API is running"}

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

# Tool Management Routes
@api_router.get("/tools", response_model=List[ReconTool])
async def get_all_tools():
    """Get all reconnaissance tools"""
    await initialize_tools()  # Ensure tools are initialized
    tools = await db.recon_tools.find().to_list(1000)
    return [ReconTool(**tool) for tool in tools]

@api_router.get("/tools/category/{category}", response_model=List[ReconTool])
async def get_tools_by_category(category: ToolCategory):
    """Get tools by category"""
    await initialize_tools()
    tools = await db.recon_tools.find({"category": category}).to_list(1000)
    return [ReconTool(**tool) for tool in tools]

@api_router.put("/tools/{tool_id}", response_model=ReconTool)
async def update_tool(tool_id: str, tool_update: ToolUpdate):
    """Update tool status and configuration"""
    update_data = {k: v for k, v in tool_update.dict().items() if v is not None}
    if update_data:
        update_data["last_updated"] = datetime.utcnow()
        await db.recon_tools.update_one({"id": tool_id}, {"$set": update_data})
    
    updated_tool = await db.recon_tools.find_one({"id": tool_id})
    if updated_tool:
        return ReconTool(**updated_tool)
    else:
        raise HTTPException(status_code=404, detail="Tool not found")

@api_router.post("/tools/{tool_id}/install")
async def install_tool(tool_id: str):
    """Initiate tool installation"""
    # Update tool status to installing
    await db.recon_tools.update_one(
        {"id": tool_id}, 
        {"$set": {"installation_status": InstallationStatus.UPDATING, "last_updated": datetime.utcnow()}}
    )
    return {"message": "Tool installation initiated", "tool_id": tool_id}

@api_router.get("/tools/stats")
async def get_tool_stats():
    """Get tool installation and status statistics"""
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

# Scan Results Routes
@api_router.get("/scan-results", response_model=List[ScanResult])
async def get_scan_results(target: Optional[str] = None, tool_name: Optional[str] = None):
    """Get scan results with optional filtering"""
    filter_query = {}
    if target:
        filter_query["target"] = {"$regex": target, "$options": "i"}
    if tool_name:
        filter_query["tool_name"] = tool_name
    
    results = await db.scan_results.find(filter_query).sort("start_time", -1).to_list(100)
    return [ScanResult(**result) for result in results]

@api_router.post("/scan-results", response_model=ScanResult)
async def create_scan_result(scan_result: ScanResult):
    """Create a new scan result"""
    await db.scan_results.insert_one(scan_result.dict())
    return scan_result

# Target Management Models
class TargetType(str, Enum):
    DOMAIN = "domain"
    IP = "ip" 
    CIDR = "cidr"

class TargetStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SCANNING = "scanning"
    COMPLETED = "completed"
    FAILED = "failed"

class ScanSeverity(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Target(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain: str
    type: TargetType
    status: TargetStatus = TargetStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_scan: Optional[datetime] = None
    subdomains: int = 0
    vulnerabilities: int = 0
    severity: ScanSeverity = ScanSeverity.NONE
    workflow: Optional[str] = "full-recon"
    notes: Optional[str] = None

class CreateTargetRequest(BaseModel):
    domain: str
    type: TargetType
    workflow: Optional[str] = "full-recon"
    notes: Optional[str] = None

class UpdateTargetRequest(BaseModel):
    domain: Optional[str] = None
    type: Optional[TargetType] = None
    status: Optional[TargetStatus] = None
    workflow: Optional[str] = None
    notes: Optional[str] = None

class TargetStats(BaseModel):
    total_targets: int
    active_scans: int
    total_subdomains: int
    total_vulnerabilities: int
    by_status: dict
    by_type: dict
    by_severity: dict

# Target Management Routes
@api_router.get("/targets/stats", response_model=TargetStats)
async def get_target_stats():
    """Get target statistics"""
    # Get all targets
    targets = await db.targets.find().to_list(1000)
    
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

@api_router.get("/targets", response_model=List[Target])
async def get_targets(
    status: Optional[TargetStatus] = None,
    type: Optional[TargetType] = None
):
    """Get all targets with optional filtering"""
    filter_query = {}
    
    if status:
        filter_query["status"] = status
    if type:
        filter_query["type"] = type
        
    targets = await db.targets.find(filter_query).to_list(1000)
    
    # Convert MongoDB documents to Target models
    result = []
    for target in targets:
        # Remove MongoDB _id from the response
        target.pop("_id", None)
        result.append(Target(**target))
        
    return result

@api_router.post("/targets", response_model=Target)
async def create_target(target_request: CreateTargetRequest):
    """Create a new target"""
    # Check if target already exists
    existing = await db.targets.find_one({"domain": target_request.domain})
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
    await db.targets.insert_one(target_dict)
    
    return target

@api_router.get("/targets/{target_id}", response_model=Target)
async def get_target(target_id: str):
    """Get a specific target by ID"""
    target = await db.targets.find_one({"id": target_id})
    
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
        
    # Remove MongoDB _id from the response
    target.pop("_id", None)
    return Target(**target)

@api_router.put("/targets/{target_id}", response_model=Target)
async def update_target(target_id: str, update_request: UpdateTargetRequest):
    """Update a target"""
    # Find existing target
    existing = await db.targets.find_one({"id": target_id})
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
    await db.targets.update_one({"id": target_id}, {"$set": update_data})
    
    # Fetch and return updated target
    updated_target = await db.targets.find_one({"id": target_id})
    updated_target.pop("_id", None)
    return Target(**updated_target)

@api_router.delete("/targets/{target_id}")
async def delete_target(target_id: str):
    """Delete a target"""
    # Check if target exists
    existing = await db.targets.find_one({"id": target_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # Delete the target
    result = await db.targets.delete_one({"id": target_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Target not found")
        
    # Also delete related scan results
    await db.scan_results.delete_many({"target": existing["domain"]})
    
    return {"message": "Target deleted successfully"}

@api_router.post("/targets/{target_id}/scan")
async def start_scan(target_id: str):
    """Start a scan for the target"""
    # Find the target
    target = await db.targets.find_one({"id": target_id})
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # Update target status to scanning
    await db.targets.update_one(
        {"id": target_id}, 
        {
            "$set": {
                "status": TargetStatus.SCANNING,
                "last_scan": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Fetch and return updated target
    updated_target = await db.targets.find_one({"id": target_id})
    updated_target.pop("_id", None)
    return Target(**updated_target)

# Include subdomain routes
api_router.include_router(subdomain_router)

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
