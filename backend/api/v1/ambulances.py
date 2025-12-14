from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class AmbulanceLocation(BaseModel):
    ambulance_id: str
    unit_number: str
    status: str  # available, dispatched, enroute, on_scene, transporting
    location: dict
    crew: List[str]
    last_updated: datetime

class RouteRequest(BaseModel):
    ambulance_id: str
    pickup_location: dict
    destination_hospital_id: str
    patient_acuity: str
    traffic_consideration: bool = True

class RouteRecommendation(BaseModel):
    route_id: str
    estimated_time_minutes: int
    distance_miles: float
    route_coordinates: List[dict]
    traffic_conditions: str
    alternative_routes: List[dict] = []

@router.get("/active", response_model=List[AmbulanceLocation])
async def get_active_ambulances():
    """Get all active ambulances with their current locations"""
    return [
        AmbulanceLocation(
            ambulance_id="AMB-001",
            unit_number="Medic 15",
            status="available",
            location={"lat": 40.7589, "lon": -73.9851},
            crew=["Paramedic Johnson", "EMT Smith"],
            last_updated=datetime.utcnow()
        ),
        AmbulanceLocation(
            ambulance_id="AMB-002",
            unit_number="Medic 23",
            status="transporting",
            location={"lat": 40.7128, "lon": -74.0060},
            crew=["Paramedic Davis", "EMT Wilson"],
            last_updated=datetime.utcnow()
        )
    ]

@router.post("/route", response_model=RouteRecommendation)
async def calculate_route(request: RouteRequest):
    """
    Calculate optimal route for ambulance
    
    Considers:
    - Real-time traffic
    - Patient acuity (affects speed/routing)
    - Road closures
    - Weather conditions
    """
    # TODO: Integrate with MCP ambulance_router agent
    return RouteRecommendation(
        route_id="ROUTE-12345",
        estimated_time_minutes=12,
        distance_miles=5.3,
        route_coordinates=[
            {"lat": 40.7589, "lon": -73.9851},
            {"lat": 40.7484, "lon": -73.9857},
            {"lat": 40.7128, "lon": -74.0060}
        ],
        traffic_conditions="moderate",
        alternative_routes=[
            {
                "route_id": "ALT-1",
                "eta_minutes": 15,
                "distance_miles": 6.1,
                "description": "Via highway - longer but faster"
            }
        ]
    )

@router.get("/{ambulance_id}")
async def get_ambulance_details(ambulance_id: str):
    """Get detailed information about specific ambulance"""
    return {
        "ambulance_id": ambulance_id,
        "unit_number": "Medic 15",
        "status": "available",
        "equipment": [
            "AED",
            "Advanced_Airway",
            "Cardiac_Monitor",
            "IV_Supplies"
        ]
    }
