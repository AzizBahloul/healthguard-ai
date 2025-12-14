"""
Unit tests for Ambulance API endpoints
Tests ambulance dispatch, tracking, and routing
"""
import pytest
from fastapi.testclient import TestClient
import httpx


class TestAmbulanceAPI:
    """Test suite for Ambulance API endpoints"""
    
    def test_list_ambulances(self, client):
        """Test listing all ambulances"""
        response = client.get("/api/v1/ambulances/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            ambulance = data[0]
            assert "id" in ambulance
            assert "unit_number" in ambulance
            assert "status" in ambulance
            assert "location" in ambulance
    
    def test_get_ambulance_by_id(self, client):
        """Test getting specific ambulance"""
        response = client.get("/api/v1/ambulances/AMB001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "AMB001"
    
    def test_get_available_ambulances(self, client):
        """Test getting only available ambulances"""
        response = client.get("/api/v1/ambulances/available")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        for ambulance in data:
            assert ambulance["status"] == "available"
    
    def test_dispatch_ambulance(self, client):
        """Test dispatching ambulance to emergency"""
        dispatch_data = {
            "ambulance_id": "AMB001",
            "emergency_case_id": "EMG12345",
            "destination": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "address": "123 Emergency St"
            },
            "priority": "critical"
        }
        
        response = client.post("/api/v1/ambulances/dispatch", json=dispatch_data)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "dispatch_time" in data
        assert "estimated_arrival_time" in data
    
    def test_update_ambulance_location(self, client):
        """Test updating ambulance GPS location"""
        location_data = {
            "latitude": 40.7589,
            "longitude": -73.9851,
            "heading": 180,
            "speed_mph": 45
        }
        
        response = client.post(
            "/api/v1/ambulances/AMB001/location",
            json=location_data
        )
        assert response.status_code == 200
    
    def test_update_ambulance_status(self, client):
        """Test updating ambulance status"""
        status_data = {
            "status": "en_route",
            "destination_hospital_id": "metro_general"
        }
        
        response = client.patch(
            "/api/v1/ambulances/AMB001/status",
            json=status_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "en_route"
    
    def test_get_ambulance_eta(self, client):
        """Test calculating ambulance ETA"""
        params = {
            "destination_lat": 40.7128,
            "destination_lng": -74.0060
        }
        
        response = client.get("/api/v1/ambulances/AMB001/eta", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "estimated_minutes" in data
        assert "distance_km" in data
        assert "route" in data
    
    def test_get_nearest_ambulance(self, client):
        """Test finding nearest available ambulance"""
        params = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "status": "available"
        }
        
        response = client.get("/api/v1/ambulances/nearest", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "ambulance_id" in data
        assert "distance_km" in data
        assert "eta_minutes" in data
    
    def test_ambulance_history(self, client):
        """Test getting ambulance dispatch history"""
        response = client.get("/api/v1/ambulances/AMB001/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            record = data[0]
            assert "timestamp" in record
            assert "event_type" in record
    
    def test_ambulance_equipment(self, client):
        """Test getting ambulance equipment inventory"""
        response = client.get("/api/v1/ambulances/AMB001/equipment")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            item = data[0]
            assert "name" in item
            assert "quantity" in item
            assert "status" in item
    
    def test_ambulance_crew(self, client):
        """Test getting ambulance crew information"""
        response = client.get("/api/v1/ambulances/AMB001/crew")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            member = data[0]
            assert "name" in member
            assert "role" in member
            assert "certification_level" in member
    
    def test_optimize_ambulance_routing(self, client):
        """Test ambulance route optimization"""
        route_data = {
            "ambulances": ["AMB001", "AMB002", "AMB003"],
            "emergencies": ["EMG001", "EMG002"],
            "constraints": {
                "max_response_time_minutes": 15,
                "prefer_als_for_critical": True
            }
        }
        
        response = client.post("/api/v1/ambulances/optimize-routing", json=route_data)
        assert response.status_code == 200
        data = response.json()
        assert "assignments" in data
        assert "optimization_score" in data


class TestAmbulanceDispatchLogic:
    """Test ambulance dispatch algorithms"""
    
    def test_dispatch_closest_available(self, client):
        """Test dispatching closest available ambulance"""
        emergency_location = {
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        
        response = client.post(
            "/api/v1/ambulances/dispatch/auto",
            json=emergency_location
        )
        assert response.status_code in [200, 201]
    
    def test_dispatch_with_capability_match(self, client):
        """Test dispatching ambulance with required capabilities"""
        dispatch_data = {
            "location": {"latitude": 40.7, "longitude": -74.0},
            "required_capability": "als",  # Advanced Life Support
            "severity": "critical"
        }
        
        response = client.post(
            "/api/v1/ambulances/dispatch/match",
            json=dispatch_data
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["ambulance_capability_level"] in ["als", "critical_care"]
    
    def test_no_ambulances_available(self, client):
        """Test response when no ambulances available"""
        # This should trigger mutual aid or overflow protocols
        response = client.get("/api/v1/ambulances/available")
        
        # Even if none available, should return valid response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
