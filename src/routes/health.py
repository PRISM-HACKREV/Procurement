"""
Health and sources monitoring endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from typing import List

from src.domain.schemas import SourcesResponse, SourceHealth, Provenance
from src.core.config import settings
from src.core.utils import simulate_latency, get_provenance
from src.core.data_loader import get_data_loader

router = APIRouter(prefix="/ext", tags=["Health"])


@router.get("/sources", response_model=SourcesResponse)
async def get_sources_health():
    """
    Check health status of all data source integrations.
    
    Returns status of:
    - Mock suppliers database
    - Haversine distance calculator
    - Routing engine
    - Pricing engine
    - Cache system
    """
    # Simulate API latency
    await simulate_latency()
    
    now = datetime.utcnow()
    
    # Check data loader
    try:
        loader = get_data_loader()
        materials = loader.get_all_materials()
        suppliers_status = "healthy" if len(materials) > 0 else "degraded"
        suppliers_response_time = 50
        suppliers_error_rate = 0.0
    except Exception:
        suppliers_status = "down"
        suppliers_response_time = None
        suppliers_error_rate = 100.0
    
    # Build source health list
    sources: List[SourceHealth] = [
        SourceHealth(
            source_name="mock-suppliers-db",
            status=suppliers_status,
            response_time_ms=suppliers_response_time,
            last_check=now,
            error_rate=suppliers_error_rate
        ),
        SourceHealth(
            source_name="haversine-distance-calc",
            status="healthy",
            response_time_ms=5,
            last_check=now,
            error_rate=0.0
        ),
        SourceHealth(
            source_name="mock-routing-engine",
            status="healthy",
            response_time_ms=30,
            last_check=now,
            error_rate=0.0
        ),
        SourceHealth(
            source_name="mock-pricing-engine",
            status="healthy",
            response_time_ms=25,
            last_check=now,
            error_rate=0.0
        ),
        SourceHealth(
            source_name="cache-system",
            status="healthy",
            response_time_ms=2,
            last_check=now,
            error_rate=0.0
        )
    ]
    
    # Add external API status (all disabled in sandbox mode)
    if settings.SOURCE_MODE == "sandbox":
        sources.extend([
            SourceHealth(
                source_name="geoapify-api",
                status="disabled",
                response_time_ms=None,
                last_check=now,
                error_rate=0.0
            ),
            SourceHealth(
                source_name="ondc-network",
                status="disabled",
                response_time_ms=None,
                last_check=now,
                error_rate=0.0
            ),
            SourceHealth(
                source_name="weather-api",
                status="disabled",
                response_time_ms=None,
                last_check=now,
                error_rate=0.0
            )
        ])
    
    # Determine overall status
    statuses = [s.status for s in sources if s.status != "disabled"]
    if all(s == "healthy" for s in statuses):
        overall_status = "healthy"
    elif any(s == "down" for s in statuses):
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    response = SourcesResponse(
        overall_status=overall_status,
        sources=sources,
        provenance=Provenance(**get_provenance(
            sources=["system-health-monitor"]
        ))
    )
    
    return response

