#!/usr/bin/env python3
"""
Minimal FastAPI Test Server for REST API Benchmarks

This is a lightweight test server that provides a single endpoint
for batch token creation, used exclusively for REST API benchmarking.

Usage:
    PYTHONPATH=python:$PYTHONPATH python tests/performance/test_api_server.py

Endpoints:
    POST /api/v1/tokens/batch - Create batch of tokens
    GET  /api/v1/health/live  - Health check
"""

import sys
import os

# Add python directory to path for neurograph module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

import neurograph
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uvicorn


# Pydantic models
class BatchCreateRequest(BaseModel):
    """Request model for batch token creation."""
    count: int = Field(..., gt=0, le=1_000_000, description="Number of tokens to create (max 1M per request)")


class TokenResponse(BaseModel):
    """Response model for a single token."""
    id: int
    coordinates: List[List[float]]


class BatchCreateResponse(BaseModel):
    """Response model for batch token creation."""
    success: bool = True
    message: str
    data: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


# Create FastAPI app
app = FastAPI(
    title="NeuroGraph Test API",
    description="Minimal test server for REST API benchmarks",
    version="0.67.4-test",
)


@app.post("/api/v1/tokens/batch", response_model=BatchCreateResponse)
async def create_tokens_batch(request: BatchCreateRequest):
    """
    Create a batch of tokens using real Rust Core implementation.

    This endpoint creates actual Token objects via PyO3 FFI to Rust Core,
    not simulated or mock objects.
    """
    try:
        # Create real tokens via Rust Core
        tokens = neurograph.Token.create_batch(request.count)

        # Convert to response format (lightweight - only ID and coordinates)
        token_data = [
            {
                "id": t.id,
                "coordinates": t.coordinates,
            }
            for t in tokens
        ]

        return BatchCreateResponse(
            success=True,
            message=f"Created {len(tokens)} tokens",
            data={
                "count": len(tokens),
                "tokens": token_data,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token creation failed: {str(e)}")


@app.get("/api/v1/health/live", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version=neurograph.__version__,
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "NeuroGraph Test API",
        "version": "0.67.4-test",
        "description": "Minimal test server for REST API benchmarks",
        "neurograph_version": neurograph.__version__,
        "endpoints": {
            "batch_create": "POST /api/v1/tokens/batch",
            "health": "GET /api/v1/health/live",
        }
    }


if __name__ == "__main__":
    print("=" * 80)
    print("NeuroGraph Test API Server")
    print("=" * 80)
    print(f"neurograph version: {neurograph.__version__}")
    print(f"Server: http://127.0.0.1:8000")
    print(f"Docs: http://127.0.0.1:8000/docs")
    print("=" * 80)
    print()

    # Test token creation
    print("Testing token creation...")
    test_tokens = neurograph.Token.create_batch(5)
    print(f"✓ Created {len(test_tokens)} test tokens")
    print(f"✓ Token[0] ID: {test_tokens[0].id}")
    print()

    print("Starting server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
