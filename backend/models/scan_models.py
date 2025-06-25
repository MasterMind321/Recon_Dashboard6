from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from .tool_models import ToolCategory
import uuid


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


class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatusCheckCreate(BaseModel):
    client_name: str