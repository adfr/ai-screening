# SDN Watchlist API

A two-step matching system for the OFAC SDN (Specially Designated Nationals) list.

## Features

- **Step 1**: Flexible name matching with variations and fuzzy matching
- **Step 2**: Context-based ranking using DOB, nationality, and other factors
- REST API for easy integration
- Modular architecture for maintainability

## Installation

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## Usage

### Start the API server

```bash
uvicorn sdn_api.api.main:app --reload
```

### API Endpoints

- `POST /search` - Search the SDN list
- `GET /health` - Health check endpoint

### Example Request

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "john mccain, 21/06/1955, american",
    "max_results": 10
  }'
```