# SDN Watchlist API

A sophisticated two-step matching system for searching the OFAC SDN (Specially Designated Nationals) list. This API helps organizations comply with sanctions screening requirements by providing intelligent name matching and context-based ranking of potential matches.

## Overview

The SDN Watchlist API uses a two-phase approach to identify potential matches:

1. **Name Matching Phase**: Employs multiple strategies including exact matching, fuzzy matching, phonetic matching, and name variation handling to cast a wide net for potential matches
2. **Context Ranking Phase**: Scores and ranks matches based on additional context like date of birth, nationality, and other identifying information

## Features

- **Intelligent Name Matching**:
  - Exact and fuzzy name matching
  - Phonetic similarity detection
  - Common name variation handling
  - Multi-language name support
  
- **Context-Aware Ranking**:
  - Date of birth matching with fuzzy date support
  - Nationality and citizenship verification
  - Address and location matching
  - Weighted scoring system
  
- **Production-Ready**:
  - RESTful API with FastAPI
  - Async support for high performance
  - Comprehensive error handling
  - Health check endpoints
  - Modular, maintainable architecture

## Requirements

- Python 3.8+
- UV package manager
- Access to OFAC SDN data

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/adfr/ai-screening.git
cd ai-screening
```

### 2. Create and activate virtual environment

```bash
# Using UV (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using standard Python
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
# Install the package in development mode
uv pip install -e .

# Or with standard pip
pip install -e .
```

### 4. Environment Configuration

Create a `.env` file in the project root with the following variables:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# OpenAI Configuration (required for context ranking)
OPENAI_API_KEY=your-api-key-here

# Matching Configuration (optional)
FUZZY_THRESHOLD=0.8
MAX_RESULTS=50
ENABLE_PHONETIC_MATCHING=true

# Logging
LOG_LEVEL=INFO
```

**Important**: The `.env` file is required for the API to function properly, especially the `OPENAI_API_KEY` which is used for intelligent context-based ranking.

## Usage

### Start the API server

```bash
# Using uvicorn directly
uvicorn sdn_api.api.main:app --reload

# Or with custom host/port from .env
uvicorn sdn_api.api.main:app --host $API_HOST --port $API_PORT --reload
```

The API will be available at `http://localhost:8000` by default.

### API Documentation

Once the server is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

### API Endpoints

#### 1. Search Endpoint
- **URL**: `POST /search`
- **Description**: Search for individuals or entities in the SDN list
- **Request Body**:
  ```json
  {
    "query": "string containing name and optional context",
    "max_results": 10
  }
  ```

#### 2. Health Check
- **URL**: `GET /health`
- **Description**: Check API status and connectivity
- **Response**: `{"status": "healthy"}`

### Example Requests

#### Basic Name Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vladimir putin",
    "max_results": 5
  }'
```

#### Search with Context
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "john mccain, 21/06/1955, american",
    "max_results": 10
  }'
```

### Example Response

```json
{
  "results": [
    {
      "sdn_entry": {
        "uid": "12345",
        "first_name": "JOHN",
        "last_name": "MCCAIN",
        "title": "",
        "sdn_type": "Individual",
        "remarks": "DOB 21 Jun 1955; nationality United States",
        "program_list": ["UKRAINE-EO13662"]
      },
      "match_score": 0.95,
      "match_reasons": [
        "Exact name match",
        "Date of birth matches",
        "Nationality matches"
      ],
      "context_score": 0.92
    }
  ],
  "total_matches": 1,
  "search_metadata": {
    "query": "john mccain, 21/06/1955, american",
    "processing_time": 0.145,
    "strategies_used": ["exact", "fuzzy", "phonetic"]
  }
}
```

### Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful search
- `400 Bad Request`: Invalid request format
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

Error responses include details:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sdn_api

# Run specific test file
pytest tests/test_api.py
```

### Code Quality

```bash
# Format code
black sdn_api tests

# Lint code
flake8 sdn_api tests

# Type checking
mypy sdn_api
```

## Architecture

The project follows a modular architecture:

```
sdn_api/
├── api/          # FastAPI application and routes
├── core/         # Core business logic
│   ├── step1/    # Name matching algorithms
│   └── step2/    # Context ranking system
├── models/       # Data models and schemas
└── utils/        # Utility functions
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.