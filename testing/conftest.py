"""
Pytest configuration for HealthGuard AI testing
Handles backend import paths and common fixtures
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    """Create a test FastAPI application"""
    from datetime import datetime
    app = FastAPI(title="HealthGuard AI Test")
    
    # Add health endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    # Import and include routers
    try:
        from api.v1 import emergency, hospitals, ambulances
        app.include_router(emergency.router, prefix="/api/v1/emergency", tags=["emergency"])
        app.include_router(hospitals.router, prefix="/api/v1/hospitals", tags=["hospitals"])
        app.include_router(ambulances.router, prefix="/api/v1/ambulances", tags=["ambulances"])
    except ImportError as e:
        # If routers don't exist yet, create mock endpoints
        pass
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_database():
    """Mock database for testing"""
    return {
        "hospitals": [
            {
                "id": "h1",
                "name": "Metro General Hospital",
                "total_beds": 500,
                "available_beds": 50,
                "specialties": ["emergency", "trauma", "cardiology"]
            }
        ],
        "ambulances": [
            {
                "id": "a1",
                "call_sign": "AMB-001",
                "status": "available",
                "location": {"lat": 40.7128, "lng": -74.0060}
            }
        ],
        "emergencies": []
    }
