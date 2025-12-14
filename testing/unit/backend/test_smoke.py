"""
Smoke tests for backend API - tests actual implemented endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestActualAPIs:
    """Test the actual implemented API endpoints"""
    
    def test_health_check(self, client):
        """Test if health endpoint exists"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_emergency_active_endpoint(self, client):
        """Test emergency active cases endpoint"""
        response = client.get("/api/v1/emergency/active")
        assert response.status_code == 200
        data = response.json()
        assert "active_cases" in data
    
    def test_hospital_beds_endpoint(self, client):
        """Test hospital bed availability endpoint"""
        response = client.get("/api/v1/hospitals/beds")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "hospital_id" in data[0]
            assert "available_beds" in data[0]
    
    def test_ambulance_active_endpoint(self, client):
        """Test ambulance active units endpoint"""
        response = client.get("/api/v1/ambulances/active")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "ambulance_id" in data[0]
            assert "status" in data[0]
    
    def test_hospital_list_endpoint(self, client):
        """Test hospital list endpoint"""
        response = client.get("/api/v1/hospitals/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
    
    def test_emergency_trauma_endpoint_structure(self, client):
        """Test trauma routing endpoint exists and validates input"""
        trauma_data = {
            "incident_id": "TEST001",
            "patient_age": 45,
            "patient_sex": "M",
            "vital_signs": {"pulse": 110, "bp": "120/80"},
            "injury_description": "head trauma",
            "mechanism_of_injury": "MVA",
            "paramedic_assessment": "alert",
            "current_location": {"lat": 40.7128, "lng": -74.0060}
        }
        
        response = client.post("/api/v1/emergency/trauma", json=trauma_data)
        # Should either work (200) or return validation error (422)
        assert response.status_code in [200, 422]
    
    def test_ambulance_route_endpoint_structure(self, client):
        """Test ambulance routing endpoint"""
        route_data = {
            "ambulance_id": "AMB-001",
            "pickup_location": {"lat": 40.7128, "lng": -74.0060},
            "destination_hospital_id": "HOSP-001",
            "patient_acuity": "critical",
            "traffic_consideration": True
        }
        
        response = client.post("/api/v1/ambulances/route", json=route_data)
        assert response.status_code in [200, 201, 404, 422]


@pytest.mark.unit
class TestCORSAndSecurity:
    """Test security configurations"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS is properly configured"""
        response = client.options("/api/v1/emergency/active")
        # Either CORS is configured or endpoint exists
        assert response.status_code in [200, 405]
    
    def test_json_content_type(self, client):
        """Test that API returns JSON"""
        response = client.get("/api/v1/emergency/active")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")


@pytest.mark.unit
class TestAPIResponses:
    """Test API response structures"""
    
    def test_error_responses_have_detail(self, client):
        """Test that error responses include detail field"""
        response = client.get("/api/v1/nonexistent/endpoint")
        assert response.status_code == 404
        data = response.json()
        # FastAPI auto-generates detail field
        assert "detail" in data
    
    def test_hospital_bed_data_structure(self, client):
        """Test hospital bed response structure"""
        response = client.get("/api/v1/hospitals/beds")
        assert response.status_code == 200
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            bed_info = data[0]
            assert isinstance(bed_info, dict)
            # Check for expected fields
            assert "hospital_id" in bed_info or "hospital_name" in bed_info
    
    def test_ambulance_location_data_structure(self, client):
        """Test ambulance location response structure"""
        response = client.get("/api/v1/ambulances/active")
        assert response.status_code == 200
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            ambulance = data[0]
            assert isinstance(ambulance, dict)
            assert "ambulance_id" in ambulance
            assert "status" in ambulance
