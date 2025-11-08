"""
Request schemas for API endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional
from src.domain.schemas import Origin


class SupplierSearchRequest(BaseModel):
    """Request for supplier search"""
    origin: Origin = Field(..., description="Request origin location")
    material: str = Field(..., description="Material type (cement, sand, gravel, bricks)")
    quantity_tons: float = Field(..., description="Required quantity in tons", gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin": {
                    "latitude": 17.3352,
                    "longitude": 78.4537,
                    "region_name": "Bandlaguda Jagir"
                },
                "material": "cement",
                "quantity_tons": 50.0
            }
        }


class QuoteRequest(BaseModel):
    """Request for price quote"""
    supplier_id: str = Field(..., description="Supplier identifier")
    material: str = Field(..., description="Material type")
    quantity_tons: float = Field(..., description="Required quantity in tons", gt=0)
    origin: Origin = Field(..., description="Delivery location")
    
    class Config:
        json_schema_extra = {
            "example": {
                "supplier_id": "SUP-CEM-BDJ-001",
                "material": "cement",
                "quantity_tons": 50.0,
                "origin": {
                    "latitude": 17.3352,
                    "longitude": 78.4537,
                    "region_name": "Bandlaguda Jagir"
                }
            }
        }


class RouteETARequest(BaseModel):
    """Request for route and ETA calculation"""
    origin: Origin = Field(..., description="Starting location")
    destination: dict = Field(..., description="Destination coordinates and name")
    quantity_tons: Optional[float] = Field(None, description="Material quantity for CO2 calculation", gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin": {
                    "latitude": 17.3352,
                    "longitude": 78.4537,
                    "region_name": "Bandlaguda Jagir"
                },
                "destination": {
                    "latitude": 17.3345,
                    "longitude": 78.4512,
                    "name": "Bandlaguda Cement Depot"
                },
                "quantity_tons": 50.0
            }
        }

