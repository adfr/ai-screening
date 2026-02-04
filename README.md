# SDN Watchlist API

A production-ready sanctions screening API for the OFAC SDN (Specially Designated Nationals) list. Built for compliance teams that need intelligent name matching with context-aware ranking.

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Development](#development)
- [Architecture](#architecture)

## Quick Start

```bash
# Clone and setup
git clone https://github.com/adfr/ai-screening.git
cd ai-screening
uv venv && source .venv/bin/activate
uv pip install -e .

# Download SDN data
curl -o sdn.csv https://www.treasury.gov/ofac/downloads/sdn.csv

# Configure environment
echo "OPENAI_API_KEY=your-key" > .env

# Run
uvicorn sdn_api.api.main:app --reload
```

API available at `http://localhost:8000` | Docs at `http://localhost:8000/docs`

## Features

| Category | Capabilities |
|----------|-------------|
| **Name Matching** | Exact, fuzzy, phonetic matching · Name variation handling · Multi-language support |
| **Context Ranking** | DOB matching with fuzzy dates · Nationality verification · Address matching · Weighted scoring |
| **Production Ready** | FastAPI with async support · Health checks · Comprehensive error handling · Modular architecture |

## How It Works

The API uses a three-phase approach:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Name Matching  │ ──▶ │ Context Ranking │ ──▶ │   Explanation   │
│                 │     │                 │     │   Generation    │
│ • Exact match   │     │ • DOB scoring   │     │                 │
│ • Fuzzy match   │     │ • Nationality   │     │ • AI-powered    │
│ • Phonetic      │     │ • Location      │     │ • Confidence    │
│ • Variations    │     │ • Weighted rank │     │ • Verification  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Example**: Query `"ABBES, Moustaf"`

1. **Phase 1** - Generates variations and finds candidates:
   - `"ABBES, Moustafa"` (exact: 1.0)
   - `"MOUSTFA, Djamel"` with alias (0.89)

2. **Phase 2** - Ranks with context:
   - Scores based on DOB, nationality, location matches

3. **Phase 3** - Generates explanations:
   - Highlights spelling variations
   - Recommends verification steps

## Installation

### Requirements

- Python 3.8+
- UV package manager (recommended) or pip
- OpenAI API key

### Setup

```bash
# Clone repository
git clone https://github.com/adfr/ai-screening.git
cd ai-screening

# Create virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Download SDN data (updated regularly by OFAC)
curl -o sdn.csv https://www.treasury.gov/ofac/downloads/sdn.csv
```

## Configuration

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# API Settings (optional)
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Matching Settings (optional)
FUZZY_THRESHOLD=0.8
MAX_RESULTS=50
ENABLE_PHONETIC_MATCHING=true

# Logging (optional)
LOG_LEVEL=INFO
```

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/search` | Search the SDN list |
| `GET` | `/health` | Health check |

### Search Request

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "john smith, 1955-06-21, american", "max_results": 10}'
```

### Response Format

```json
{
  "results": [
    {
      "sdn_entry": {
        "uid": "12345",
        "first_name": "JOHN",
        "last_name": "SMITH",
        "sdn_type": "Individual",
        "program_list": ["SDGT"]
      },
      "match_score": 0.95,
      "match_reasons": ["Exact name match", "DOB matches", "Nationality matches"],
      "context_score": 0.92,
      "explanation": "High-likelihood match based on name, DOB, and nationality alignment."
    }
  ],
  "total_matches": 1,
  "search_metadata": {
    "query": "john smith, 1955-06-21, american",
    "processing_time": 0.145,
    "strategies_used": ["exact", "fuzzy", "phonetic"]
  }
}
```

### Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Invalid request |
| `422` | Validation error |
| `500` | Server error |

## Development

```bash
# Run tests
pytest
pytest --cov=sdn_api

# Code quality
black sdn_api tests
flake8 sdn_api tests
mypy sdn_api
```

## Architecture

```
sdn_api/
├── api/          # FastAPI routes
├── core/         # Business logic
│   ├── step1/    # Name matching
│   └── step2/    # Context ranking
├── models/       # Data schemas
└── utils/        # Utilities
```

## License

MIT License - see LICENSE file for details.
