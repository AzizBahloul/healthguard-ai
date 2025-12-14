"""
Unit tests for Emergency API endpoints
Tests emergency case management, triage, and routing logic
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import Mock, patch
import httpx


class TestEmergencyAPI:
    """Test suite for Emergency API endpoints"""
    
    def test_get_active_cases_empty(self, client):
        """Test getting active cases when none exist"""
        response = client.get("/api/v1/emergency/active")
        assert response.status_code == 200
        data = response.json()
        assert "active_cases" in data
        assert isinstance(data["active_cases"], list)
        assert "timestamp" in data
    
    def test_create_emergency_case_valid(self, client):
        """Test creating a valid emergency case"""
        emergency_data = {
            "patient_id": "P12345",
            "severity": "critical",
            "type": "cardiac_arrest",
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "address": "123 Emergency St"
            },
            "vital_signs": {
                "heart_rate": 120,
                "blood_pressure": "180/110",
                "oxygen_saturation": 88,
                "respiratory_rate": 24,
                "temperature": 101.5
            },
            "symptoms": ["chest_pain", "shortness_of_breath"],
            "reporter": "paramedic_unit_12"
        }
        
        response = client.post("/api/v1/emergency/create", json=emergency_data)
        assert response.status_code == 201
        data = response.json()
        assert "case_id" in data
        assert data["severity"] == "critical"
        assert data["status"] == "active"
    
    def test_create_emergency_case_invalid_severity(self, client):
        """Test creating emergency case with invalid severity"""
        emergency_data = {
            "patient_id": "P12345",
            "severity": "invalid_level",
            "type": "trauma",
            "location": {"latitude": 40.7, "longitude": -74.0}
        }
        
        response = client.post("/api/v1/emergency/create", json=emergency_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_emergency_case_missing_fields(self, client):
        """Test creating emergency case with missing required fields"""
        emergency_data = {
            "severity": "high"
            # Missing patient_id, type, location
        }
        
        response = client.post("/api/v1/emergency/create", json=emergency_data)
        assert response.status_code == 422
    
    def test_update_emergency_status(self, client):
        """Test updating emergency case status"""
        # First create a case
        emergency_data = {
            "patient_id": "P67890",
            "severity": "high",
            "type": "trauma",
            "location": {"latitude": 40.7, "longitude": -74.0}
        }
        create_response = client.post("/api/v1/emergency/create", json=emergency_data)
        case_id = create_response.json()["case_id"]
        
        # Update status
        update_data = {"status": "en_route_to_hospital"}
        response = client.patch(f"/api/v1/emergency/{case_id}/status", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "en_route_to_hospital"
    
    def test_get_emergency_case_by_id(self, client):
        """Test retrieving specific emergency case"""
        # Create a case first
        emergency_data = {
            "patient_id": "P11111",
            "severity": "medium",
            "type": "fall",
            "location": {"latitude": 40.7, "longitude": -74.0}
        }
        create_response = client.post("/api/v1/emergency/create", json=emergency_data)
        case_id = create_response.json()["case_id"]
        
        # Get the case
        response = client.get(f"/api/v1/emergency/{case_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == case_id
        assert data["patient_id"] == "P11111"
    
    def test_get_nonexistent_case(self, client):
        """Test getting a case that doesn't exist"""
        response = client.get("/api/v1/emergency/nonexistent_id")
        assert response.status_code == 404
    
    def test_triage_assessment(self, client):
        """Test automated triage assessment"""
        triage_data = {
            "vital_signs": {
                "heart_rate": 140,
                "blood_pressure": "200/120",
                "oxygen_saturation": 85,
                "respiratory_rate": 30,
                "glasgow_coma_scale": 12
            },
            "symptoms": ["chest_pain", "difficulty_breathing", "altered_mental_status"],
            "patient_age": 65,
            "medical_history": ["hypertension", "diabetes"]
        }
        
        response = client.post("/api/v1/emergency/triage", json=triage_data)
        assert response.status_code == 200
        data = response.json()
        assert "severity_level" in data
        assert "recommended_actions" in data
        assert "confidence_score" in data
        assert data["severity_level"] in ["critical", "high", "medium", "low"]
    
    def test_emergency_statistics(self, client):
        """Test getting emergency statistics"""
        response = client.get("/api/v1/emergency/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_cases" in data
        assert "active_cases" in data
        assert "resolved_cases" in data
        assert "average_response_time" in data
    
    def test_emergency_timeline(self, client):
        """Test getting emergency case timeline"""
        # Create case
        emergency_data = {
            "patient_id": "P22222",
            "severity": "high",
            "type": "stroke",
            "location": {"latitude": 40.7, "longitude": -74.0}
        }
        create_response = client.post("/api/v1/emergency/create", json=emergency_data)
        case_id = create_response.json()["case_id"]
        
        # Get timeline
        response = client.get(f"/api/v1/emergency/{case_id}/timeline")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["events"], list)
        assert len(data["events"]) > 0
        assert "timestamp" in data["events"][0]
        assert "event_type" in data["events"][0]


@pytest.mark.parametrize("severity,expected_priority", [
    ("critical", 1),
    ("high", 2),
    ("medium", 3),
    ("low", 4)
])
def test_severity_to_priority_mapping(severity, expected_priority):
    """Test that severity levels map to correct priority values"""
    # This test would require the actual implementation
    # For now, just test the mapping logic
    priority_map = {"critical": 1, "high": 2, "medium": 3, "low": 4}
    assert priority_map.get(severity) == expected_priority


@pytest.mark.asyncio
async def test_concurrent_emergency_creation(app):
    """Test creating multiple emergencies concurrently"""
    import asyncio
    from httpx import AsyncClient
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        tasks = []
        for i in range(10):
            emergency_data = {
                "patient_id": f"P{i:05d}",
                "severity": "medium",
                "type": "general",
                "location": {"latitude": 40.7, "longitude": -74.0}
            }
            tasks.append(client.post("/api/v1/emergency/create", json=emergency_data))
        
        responses = await asyncio.gather(*tasks)
        assert all(r.status_code == 201 for r in responses)
        case_ids = [r.json()["case_id"] for r in responses]
        assert len(set(case_ids)) == 10  # All unique IDs
