from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from ..models.sdn import SearchQuery, SearchResponse, MatchResult
from ..core.search_service import SDNSearchService
from ..config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


app = FastAPI(
    title="SDN Watchlist API",
    description="Two-step matching system for OFAC SDN list",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search service
SDN_FILE_PATH = Path(__file__).parent.parent.parent / settings.sdn_file_path
try:
    search_service = SDNSearchService(str(SDN_FILE_PATH), use_llm=settings.use_llm)
    logger.info(f"Initialized SDN Search Service with LLM: {settings.use_llm}")
except FileNotFoundError:
    logger.error(f"SDN file not found at {SDN_FILE_PATH}")
    search_service = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "sdn_loaded": search_service is not None,
        "entries_count": len(search_service.entries) if search_service else 0
    }


@app.post("/search", response_model=SearchResponse)
async def search_sdn(query: SearchQuery):
    """
    Search the SDN list with two-step matching.
    
    Step 1: Flexible name matching
    Step 2: Context-based ranking (DOB, nationality, etc.)
    """
    if not search_service:
        raise HTTPException(status_code=503, detail="SDN data not loaded")
    
    try:
        results = search_service.search(query.query, query.max_results)
        
        return SearchResponse(
            query=query.query,
            total_matches=len(results),
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get statistics about the loaded SDN data."""
    if not search_service:
        raise HTTPException(status_code=503, detail="SDN data not loaded")
    
    individuals = sum(1 for e in search_service.entries if 'individual' in e.type.lower())
    entities = len(search_service.entries) - individuals
    
    return {
        "total_entries": len(search_service.entries),
        "individuals": individuals,
        "entities": entities,
        "programs": len(set(e.program for e in search_service.entries if e.program))
    }