#!/usr/bin/env python3
"""
Run the SDN API server
"""
from sdn_api.api.main import app

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )