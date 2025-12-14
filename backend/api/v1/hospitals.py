from fastapi import APIRouter, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class BedAvailability(BaseModel):
    hospital_id: str
    hospital_name: str
    total_beds: int
    available_beds: int
    bed_type_breakdown: dict
    utilization_percentage: float
    last_updated: datetime

class Hospital(BaseModel):
    id: str
    name: str
    level: str
    capabilities: List[str]
    location: dict
    contact: dict

@router.get("/beds", response_model=List[BedAvailability])
async def get_bed_availability(
    hospital_id: Optional[str] = None,
    bed_type: Optional[str] = None,
    region: Optional[str] = None
):
    """
    Get real-time bed availability across hospitals
    
    Query parameters:
    - hospital_id: Filter by specific hospital
    - bed_type: Filter by bed type (icu, medical_surgical, etc.)
    - region: Filter by geographic region
    """
    # TODO: Query database for real bed availability
    # For now, return mock data
    return [
        BedAvailability(
            hospital_id="HOSP-001",
            hospital_name="Metro General Hospital",
            total_beds=450,
            available_beds=32,
            bed_type_breakdown={
                "icu": 5,
                "step_down": 8,
                "medical_surgical": 15,
                "telemetry": 4
            },
            utilization_percentage=92.9,
            last_updated=datetime.utcnow()
        ),
        BedAvailability(
            hospital_id="HOSP-002",
            hospital_name="City Medical Center",
            total_beds=380,
            available_beds=48,
            bed_type_breakdown={
                "icu": 8,
                "step_down": 12,
                "medical_surgical": 22,
                "telemetry": 6
            },
            utilization_percentage=87.4,
            last_updated=datetime.utcnow()
        )
    ]

@router.get("/{hospital_id}", response_model=Hospital)
async def get_hospital_details(hospital_id: str):
    """Get detailed information about a specific hospital"""
    # TODO: Query database
    return Hospital(
        id=hospital_id,
        name="Metro General Hospital",
        level="Level 1 Trauma Center",
        capabilities=[
            "trauma_surgery",
            "neurosurgery",
            "cardiac_cath_lab",
            "stroke_center",
            "burn_unit",
            "nicu",
            "picu"
        ],
        location={
            "address": "123 Medical Plaza",
            "city": "Metro City",
            "state": "MC",
            "zip": "12345",
            "coordinates": {"lat": 40.7128, "lon": -74.0060}
        },
        contact={
            "phone": "555-0100",
            "emergency": "555-0911"
        }
    )

@router.get("/")
async def list_hospitals(
    region: Optional[str] = None,
    level: Optional[str] = None
):
    """List all hospitals with optional filtering"""
    return {
        "hospitals": [
            {"id": "HOSP-001", "name": "Metro General Hospital"},
            {"id": "HOSP-002", "name": "City Medical Center"}
        ],
        "total": 2
    }
