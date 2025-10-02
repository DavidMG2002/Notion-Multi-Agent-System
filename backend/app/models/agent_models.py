from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class AgentTask:
    task: str
    priority: str
    estimated_time: str

@dataclass 
class AgentResponse:
    agent: str
    success: bool = True
    content: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ContentBlock:
    block_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None