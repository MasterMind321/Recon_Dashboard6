from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


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