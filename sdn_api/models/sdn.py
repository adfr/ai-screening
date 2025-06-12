from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum


class EntityType(str, Enum):
    INDIVIDUAL = "individual"
    ENTITY = "entity"
    UNKNOWN = "unknown"


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM_HIGH = "MEDIUM-HIGH"
    MEDIUM = "MEDIUM"
    LOW_MEDIUM = "LOW-MEDIUM"
    LOW = "LOW"


class SDNEntry(BaseModel):
    """Represents a single SDN list entry."""
    id: str
    name: str
    type: str = ""
    program: str = ""
    title: str = ""
    nationality: Optional[str] = None
    dob: Optional[str] = None
    pob: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    remarks: str = ""
    

class SearchQuery(BaseModel):
    """Search request model."""
    query: str = Field(..., description="Search query (e.g., 'john mccain, 21/06/1955, american')")
    max_results: int = Field(default=10, ge=1, le=100)
    

class MatchResult(BaseModel):
    """Single match result."""
    name: str
    type: str
    name_match_score: float = Field(..., ge=0, le=1, description="Initial fuzzy name matching score")
    llm_score: float = Field(..., ge=0, le=1, description="AI-enhanced score considering context")
    score: float = Field(..., ge=0, le=1, description="Deprecated: Use llm_score instead")
    confidence: ConfidenceLevel
    match_reasons: List[str]
    details: Dict[str, Optional[str | List[str]]]


class SearchResponse(BaseModel):
    """API search response."""
    query: str
    total_matches: int
    results: List[MatchResult]