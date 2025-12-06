from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class RiskLevel(Enum):
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"  
    HIGH_RISK = "high_risk"
    BLOCKED = "blocked"

@dataclass
class ModerationResult:
    is_safe: bool
    risk_level: RiskLevel
    flagged_words: List[str]
    flagged_patterns: List[str]
    reason: str
    sanitized_content: Optional[str] = None