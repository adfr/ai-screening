from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import traceback
from functools import wraps

from ..models.sdn import SearchQuery, SearchResponse, MatchResult
from ..core.search_service import SDNSearchService
from ..config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS

# API Key
API_KEY = "7d56a165ab7bc4cb4360e2bd8499cd55fbf5666c3c58cb8f258ac70019a6d224.49090a5fa7204c2ab64cf5a4a6801c8a85b0fd3bdb73ae61239b35d4bffd0645"

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if api_key != API_KEY:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Initialize search service
SDN_FILE_PATH = Path(__file__).parent.parent.parent / settings.sdn_file_path
try:
    search_service = SDNSearchService(str(SDN_FILE_PATH), use_llm=settings.use_llm)
    logger.info(f"Initialized SDN Search Service with LLM: {settings.use_llm}")
except FileNotFoundError:
    logger.error(f"SDN file not found at {SDN_FILE_PATH}")
    search_service = None


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "sdn_loaded": search_service is not None,
        "entries_count": len(search_service.entries) if search_service else 0
    })


@app.route("/search", methods=["POST"])
def search_sdn():
    """
    Search the SDN list with two-step matching.
    
    Step 1: Flexible name matching
    Step 2: Context-based ranking (DOB, nationality, etc.)
    """
    if not search_service:
        return jsonify({"error": "SDN data not loaded"}), 503
    
    try:
        data = request.get_json()
        query_text = data.get("query", "")
        max_results = data.get("max_results", 10)
        
        results = search_service.search(query_text, max_results)
        
        return jsonify({
            "query": query_text,
            "total_matches": len(results),
            "results": [result.dict() for result in results]
        })
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/stats", methods=["GET"])
def get_stats():
    """Get statistics about the loaded SDN data."""
    if not search_service:
        return jsonify({"error": "SDN data not loaded"}), 503
    
    individuals = sum(1 for e in search_service.entries if 'individual' in e.type.lower())
    entities = len(search_service.entries) - individuals
    
    return jsonify({
        "total_entries": len(search_service.entries),
        "individuals": individuals,
        "entities": entities,
        "programs": len(set(e.program for e in search_service.entries if e.program))
    })