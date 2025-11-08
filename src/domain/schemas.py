"""
Pydantic schemas for PRISMA Procurement API

Defines all data contracts: Origin, Supplier, SupplierBundle, Quote, RouteETA, Provenance
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MaterialType(str, Enum):
    """Supported construction materials"""
    CEMENT = "cement"
    SAND = "sand"
    GRAVEL = "gravel"
    BRICKS = "bricks"


class Origin(BaseModel):
    """Request origin location (where materials are needed)"""
    latitude: float = Field(..., description="Latitude of request origin", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude of request origin", ge=-180, le=180)
    region_name: Optional[str] = Field(None, description="Human-readable region name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 17.3352,
                "longitude": 78.4537,
                "region_name": "Bandlaguda Jagir"
            }
        }


class Supplier(BaseModel):
    """Individual supplier information"""
    supplier_id: str = Field(..., description="Unique supplier identifier")
    name: str = Field(..., description="Supplier business name")
    material_id: str = Field(..., description="Material type ID")
    material_name: str = Field(..., description="Material name")
    stock_tons: float = Field(..., description="Available stock in metric tons", ge=0)
    price_inr_per_ton: float = Field(..., description="Price per ton in INR", ge=0)
    lead_time_days: int = Field(..., description="Delivery lead time in days", ge=0)
    latitude: float = Field(..., description="Supplier location latitude", ge=-90, le=90)
    longitude: float = Field(..., description="Supplier location longitude", ge=-180, le=180)
    address: str = Field(..., description="Full supplier address")
    rating: float = Field(..., description="Supplier rating (0-5)", ge=0, le=5)
    distance_km: Optional[float] = Field(None, description="Distance from origin in kilometers", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "supplier_id": "SUP-CEM-001",
                "name": "Bandlaguda Cement Depot",
                "material_id": "cement",
                "material_name": "Portland Cement",
                "stock_tons": 500.0,
                "price_inr_per_ton": 6800.0,
                "lead_time_days": 2,
                "latitude": 17.3345,
                "longitude": 78.4512,
                "address": "Plot 42, Industrial Area, Bandlaguda Jagir, Hyderabad - 500086",
                "rating": 4.5,
                "distance_km": 2.3
            }
        }


class Provenance(BaseModel):
    """Metadata about data source and freshness"""
    provider: str = Field(..., description="API provider name (e.g., 'geoapify', 'ondc', 'mock')")
    cache: bool = Field(..., description="Whether response was served from cache")
    cache_age_seconds: Optional[int] = Field(None, description="Age of cached data in seconds")
    request_id: str = Field(..., description="Unique request identifier for tracing")
    generated_at: datetime = Field(..., description="Timestamp when response was generated")
    sources: List[str] = Field(..., description="List of data sources used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider": "mock-sandbox",
                "cache": False,
                "cache_age_seconds": None,
                "request_id": "req-abc123def456",
                "generated_at": "2025-11-08T10:30:00Z",
                "sources": ["mock-suppliers-db", "haversine-distance-calc"]
            }
        }


class SupplierBundle(BaseModel):
    """Complete supplier search response with ranking"""
    origin: Origin = Field(..., description="Request origin location")
    material: str = Field(..., description="Requested material type")
    quantity_tons: float = Field(..., description="Requested quantity in tons", ge=0)
    suppliers: List[Supplier] = Field(..., description="All matching suppliers")
    recommended: Optional[Supplier] = Field(None, description="Top-ranked supplier recommendation")
    ranking_criteria: List[str] = Field(
        default=["distance", "price", "lead_time"],
        description="Criteria used for ranking"
    )
    provenance: Provenance = Field(..., description="Data provenance metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin": {
                    "latitude": 17.3352,
                    "longitude": 78.4537,
                    "region_name": "Bandlaguda Jagir"
                },
                "material": "cement",
                "quantity_tons": 50.0,
                "suppliers": [],
                "recommended": None,
                "ranking_criteria": ["distance", "price", "lead_time"],
                "provenance": {
                    "provider": "mock-sandbox",
                    "cache": False,
                    "request_id": "req-xyz789",
                    "generated_at": "2025-11-08T10:30:00Z",
                    "sources": ["mock-suppliers-db"]
                }
            }
        }


class Quote(BaseModel):
    """Price quote from a specific supplier"""
    quote_id: str = Field(..., description="Unique quote identifier")
    supplier: Supplier = Field(..., description="Supplier providing the quote")
    material: str = Field(..., description="Material type")
    quantity_tons: float = Field(..., description="Quoted quantity in tons", ge=0)
    unit_price_inr: float = Field(..., description="Price per ton in INR", ge=0)
    total_price_inr: float = Field(..., description="Total quote price in INR", ge=0)
    valid_until: datetime = Field(..., description="Quote expiration timestamp")
    notes: Optional[str] = Field(None, description="Additional quote notes")
    provenance: Provenance = Field(..., description="Data provenance metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "quote_id": "QUO-20251108-001",
                "supplier": {},
                "material": "cement",
                "quantity_tons": 50.0,
                "unit_price_inr": 6850.0,
                "total_price_inr": 342500.0,
                "valid_until": "2025-11-10T10:30:00Z",
                "notes": "Price includes GST",
                "provenance": {
                    "provider": "mock-sandbox",
                    "cache": False,
                    "request_id": "req-quote-123",
                    "generated_at": "2025-11-08T10:30:00Z",
                    "sources": ["mock-pricing-engine"]
                }
            }
        }


class RouteETA(BaseModel):
    """Route information with ETA and environmental impact"""
    route_id: str = Field(..., description="Unique route identifier")
    origin: Origin = Field(..., description="Starting location")
    destination: dict = Field(..., description="Destination supplier coordinates")
    distance_km: float = Field(..., description="Total route distance in kilometers", ge=0)
    duration_minutes: int = Field(..., description="Estimated travel time in minutes", ge=0)
    eta: datetime = Field(..., description="Estimated time of arrival")
    co2_kg: float = Field(..., description="Estimated CO2 emissions in kg", ge=0)
    route_quality: str = Field(..., description="Route quality indicator (e.g., 'optimal', 'good', 'fair')")
    provenance: Provenance = Field(..., description="Data provenance metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "route_id": "ROUTE-20251108-001",
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
                "distance_km": 2.3,
                "duration_minutes": 15,
                "eta": "2025-11-08T10:45:00Z",
                "co2_kg": 1.84,
                "route_quality": "optimal",
                "provenance": {
                    "provider": "mock-sandbox",
                    "cache": False,
                    "request_id": "req-route-456",
                    "generated_at": "2025-11-08T10:30:00Z",
                    "sources": ["mock-routing-engine"]
                }
            }
        }


class HealthStatus(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    mode: str = Field(..., description="Operating mode (sandbox/live)")
    timestamp: datetime = Field(..., description="Health check timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "mode": "sandbox",
                "timestamp": "2025-11-08T10:30:00Z"
            }
        }


class SourceHealth(BaseModel):
    """Health status of external integrations"""
    source_name: str = Field(..., description="Name of the data source")
    status: str = Field(..., description="Health status (healthy/degraded/down)")
    response_time_ms: Optional[int] = Field(None, description="Average response time in milliseconds")
    last_check: datetime = Field(..., description="Last health check timestamp")
    error_rate: float = Field(..., description="Error rate percentage", ge=0, le=100)


class SourcesResponse(BaseModel):
    """Overall health of all integrations"""
    overall_status: str = Field(..., description="Overall system health status")
    sources: List[SourceHealth] = Field(..., description="Individual source health statuses")
    provenance: Provenance = Field(..., description="Data provenance metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_status": "healthy",
                "sources": [
                    {
                        "source_name": "mock-suppliers-db",
                        "status": "healthy",
                        "response_time_ms": 50,
                        "last_check": "2025-11-08T10:30:00Z",
                        "error_rate": 0.0
                    }
                ],
                "provenance": {
                    "provider": "mock-sandbox",
                    "cache": False,
                    "request_id": "req-health-789",
                    "generated_at": "2025-11-08T10:30:00Z",
                    "sources": ["system-health-monitor"]
                }
            }
        }

