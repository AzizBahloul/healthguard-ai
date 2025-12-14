"""
Unit tests for Hospital API endpoints
Tests hospital management, capacity tracking, and resource allocation
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import httpx


class TestHospitalAPI:
    """Test suite for Hospital API endpoints"""
    
    def test_list_hospitals(self, client):
        """Test listing all hospitals"""
        response = client.get("/api/v1/hospitals/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Validate hospital structure
        hospital = data[0]
        assert "id" in hospital
        assert "name" in hospital
        assert "level" in hospital
        assert "capabilities" in hospital
        assert "location" in hospital
        assert "capacity" in hospital
    
    def test_get_hospital_by_id(self, client):
        """Test getting specific hospital details"""
        response = client.get("/api/v1/hospitals/metro_general")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "metro_general"
        assert "name" in data
        assert "contact" in data
    
    def test_get_nonexistent_hospital(self, client):
        """Test getting hospital that doesn't exist"""
        response = client.get("/api/v1/hospitals/nonexistent_hospital")
        assert response.status_code == 404
    
    def test_get_hospital_capacity(self, client):
        """Test getting hospital capacity information"""
        response = client.get("/api/v1/hospitals/metro_general/capacity")
        assert response.status_code == 200
        data = response.json()
        assert "total_beds" in data
        assert "available_beds" in data
        assert "icu_beds" in data
        assert "er_beds" in data
        assert "occupancy_rate" in data
        assert 0 <= data["occupancy_rate"] <= 100
    
    def test_update_hospital_capacity(self, client):
        """Test updating hospital capacity"""
        capacity_data = {
            "total_beds": 500,
            "available_beds": 50,
            "icu_beds": {"total": 50, "available": 5},
            "er_beds": {"total": 30, "available": 10}
        }
        
        response = client.put(
            "/api/v1/hospitals/metro_general/capacity",
            json=capacity_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["available_beds"] == 50
    
    def test_search_hospitals_by_location(self, client):
        """Test searching hospitals by location"""
        params = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius_km": 10
        }
        
        response = client.get("/api/v1/hospitals/search", params=params)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Validate distance is included
        if len(data) > 0:
            assert "distance_km" in data[0]
    
    def test_search_hospitals_by_capability(self, client):
        """Test searching hospitals by capability"""
        params = {
            "capability": "trauma_surgery",
            "severity": "critical"
        }
        
        response = client.get("/api/v1/hospitals/search", params=params)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All returned hospitals should have the capability
        for hospital in data:
            assert "trauma_surgery" in hospital["capabilities"]
    
    def test_get_hospital_availability(self, client):
        """Test checking real-time hospital availability"""
        response = client.get("/api/v1/hospitals/metro_general/availability")
        assert response.status_code == 200
        data = response.json()
        assert "accepting_patients" in data
        assert "estimated_wait_time_minutes" in data
        assert "specialties_available" in data
        assert isinstance(data["specialties_available"], list)
    
    def test_get_hospital_staff(self, client):
        """Test getting hospital staff information"""
        response = client.get("/api/v1/hospitals/metro_general/staff")
        assert response.status_code == 200
        data = response.json()
        assert "total_staff" in data
        assert "on_duty" in data
        assert "by_specialty" in data
        assert isinstance(data["by_specialty"], dict)
    
    def test_get_hospital_equipment(self, client):
        """Test getting hospital equipment status"""
        response = client.get("/api/v1/hospitals/metro_general/equipment")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            equipment = data[0]
            assert "name" in equipment
            assert "type" in equipment
            assert "status" in equipment
            assert equipment["status"] in ["available", "in_use", "maintenance", "offline"]
    
    def test_hospital_statistics(self, client):
        """Test getting hospital statistics"""
        response = client.get("/api/v1/hospitals/metro_general/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "admissions_today" in data
        assert "discharges_today" in data
        assert "average_length_of_stay" in data
        assert "mortality_rate" in data
    
    def test_get_hospitals_with_filters(self, client):
        """Test getting hospitals with multiple filters"""
        params = {
            "level": "Level 1 Trauma Center",
            "min_available_beds": 5,
            "capability": "stroke_center"
        }
        
        response = client.get("/api/v1/hospitals/search", params=params)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        for hospital in data:
            assert hospital["level"] == "Level 1 Trauma Center"
            assert "stroke_center" in hospital["capabilities"]
    
    def test_hospital_diversion_status(self, client):
        """Test getting hospital diversion status"""
        response = client.get("/api/v1/hospitals/metro_general/diversion")
        assert response.status_code == 200
        data = response.json()
        assert "is_on_diversion" in data
        assert "diversion_type" in data
        assert "reason" in data
        assert "expected_end_time" in data
    
    def test_update_diversion_status(self, client):
        """Test updating hospital diversion status"""
        diversion_data = {
            "is_on_diversion": True,
            "diversion_type": "full",
            "reason": "ICU at capacity",
            "duration_hours": 4
        }
        
        response = client.post(
            "/api/v1/hospitals/metro_general/diversion",
            json=diversion_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_on_diversion"] == True
    
    def test_get_hospital_departments(self, client):
        """Test getting hospital department information"""
        response = client.get("/api/v1/hospitals/metro_general/departments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            dept = data[0]
            assert "name" in dept
            assert "capacity" in dept
            assert "current_patients" in dept
    
    @pytest.mark.parametrize("filter_type,filter_value", [
        ("capability", "cardiac_cath_lab"),
        ("level", "Level 2 Trauma Center"),
        ("min_beds", 10)
    ])
    def test_hospital_filtering(self, client, filter_type, filter_value):
        """Test various hospital filtering options"""
        params = {filter_type: filter_value}
        response = client.get("/api/v1/hospitals/search", params=params)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestHospitalCapacityManagement:
    """Test hospital capacity management logic"""
    
    def test_bed_allocation(self, client):
        """Test allocating bed to patient"""
        allocation_data = {
            "patient_id": "P12345",
            "bed_type": "icu",
            "priority": "critical"
        }
        
        response = client.post(
            "/api/v1/hospitals/metro_general/allocate-bed",
            json=allocation_data
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "bed_id" in data
        assert "allocation_time" in data
    
    def test_bed_release(self, client):
        """Test releasing allocated bed"""
        release_data = {
            "bed_id": "ICU-101",
            "patient_id": "P12345",
            "discharge_type": "home"
        }
        
        response = client.post(
            "/api/v1/hospitals/metro_general/release-bed",
            json=release_data
        )
        assert response.status_code == 200
    
    def test_capacity_exceeded(self, client):
        """Test handling when capacity is exceeded"""
        # This should trigger overflow protocols
        response = client.get("/api/v1/hospitals/metro_general/overflow-status")
        assert response.status_code == 200
        data = response.json()
        assert "is_overflow" in data
        assert "overflow_protocol_active" in data
