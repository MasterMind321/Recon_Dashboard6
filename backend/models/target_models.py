from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

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