# Flask UI for SDN Screening API

A modern web interface for the SDN (Specially Designated Nationals) screening API, providing an intuitive way to search and view OFAC compliance results.

## Features

- Clean, responsive web interface
- Real-time search against SDN watchlist
- Visual confidence level indicators
- Detailed match explanations
- Live API health monitoring
- Statistics dashboard

## Prerequisites

- Python 3.10+
- uv package manager
- Running SDN API on port 8000

## Installation

1. Navigate to the flask_ui directory:
```bash
cd flask_ui
```

2. Create and activate virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -e .
```

4. Configure environment (optional):
```bash
cp .env.example .env
# Edit .env to change API URL if needed
```

## Running the Application

### Option 1: Using the run script
```bash
python run.py
```

### Option 2: Direct Python
```bash
source .venv/bin/activate
python app/app.py
```

### Option 3: Production server with Gunicorn
```bash
source .venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5000 app.app:app
```

## Usage

1. Ensure the SDN API is running on http://localhost:8000
2. Start the Flask UI (default: http://localhost:5000)
3. Enter search query (name, DOB, nationality, etc.)
4. View results with confidence scores and explanations

## Configuration

Environment variables in `.env`:

- `API_BASE_URL`: Backend API URL (default: http://localhost:8000)
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Enable debug mode (default: True)
- `FLASK_PORT`: Flask server port (default: 5000)

## Architecture

The Flask UI is completely independent from the API:
- Separate virtual environment
- No shared code or dependencies
- Communicates via HTTP REST API
- Can be deployed separately

## API Endpoints

The UI provides these routes:
- `/` - Main search interface
- `/search` - POST endpoint for search queries
- `/health` - Health check for UI and API
- `/stats` - SDN database statistics

## Development

The project structure:
```
flask_ui/
├── app/
│   ├── __init__.py
│   └── app.py          # Flask application
├── templates/
│   ├── base.html       # Base template
│   └── index.html      # Search interface
├── static/
│   ├── css/
│   │   └── style.css   # Styles
│   └── js/
│       └── main.js     # JavaScript
├── .env                # Environment config
├── pyproject.toml      # Project config
└── run.sh             # Startup script
```