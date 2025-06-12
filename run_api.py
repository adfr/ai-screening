#!/usr/bin/env python3
"""
Run the SDN API server
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "sdn_api.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )