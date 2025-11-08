"""
Supplier search and procurement routes for PRISMA Procurement API
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import random

from src.domain.schemas import (
    Origin, Supplier, SupplierBundle, Quote, RouteETA, 
    Provenance, SourceHealth, SourcesResponse
)
from src.core.config import settings
from src.core.utils import (
    haversine_distance, simulate_latency, generate_request_id,
    apply_price_jitter, calculate_co2_emissions, estimate_delivery_eta,
    load_supplier_data, rank_suppliers, filter_eligible_suppliers,
    create_split_plan
)
from src.core.cache import cache_manager

router = APIRouter(prefix="/ext", tags=["Procurement"])


class SupplierSearchRequest(BaseModel):
    """Request model for supplier search"""
    origin: Origin
    material: str = Field(..., description="Material ID (cement, sand, aggregate, bricks)")
    quantity_tons: float = Field(..., gt=0, description="Required quantity in tons")


class QuoteRequest(BaseModel):
    """Request model for price quote"""
    supplier_id: str
    material: str
    quantity_tons: float = Field(..., gt=0)
    origin: Origin


class RouteRequest(BaseModel):
    """Request model for route calculation"""
    origin: Origin
    destination: dict = Field(..., description="Destination coordinates and name")
    quantity_tons: Optional[float] = Field(None, description="Material quantity for CO2 calculation")


@router.post("/suppliers/search", response_model=SupplierBundle)
async def search_suppliers(request: SupplierSearchRequest):
    """
    Search and rank suppliers for a material based on location and quantity.
    
    Returns ranked suppliers with distance, price, and lead time calculations.
    Includes best recommendation or split plan if needed.
    """
    # Simulate latency
    await simulate_latency(settings.MIN_LATENCY_MS, settings.MAX_LATENCY_MS)
    
    request_id = generate_request_id()
    
    # Check cache
    cache_key_params = {
        "endpoint": "suppliers_search",
        "material": request.material,
        "lat": round(request.origin.latitude, 4),
        "lon": round(request.origin.longitude, 4),
        "qty": request.quantity_tons
    }
    
    cached = await cache_manager.get(**cache_key_params)
    if cached and settings.USE_MOCK:
        data = cached["data"]
        data["provenance"]["cache"] = True
        data["provenance"]["cache_age_seconds"] = cached["age_seconds"]
        data["provenance"]["request_id"] = request_id
        return data
    
    try:
        # Load supplier data (cached)
        supplier_data = load_supplier_data(request.material)
        suppliers_list = supplier_data.get("suppliers", [])
        
        # Calculate distances and enrich supplier data (vectorized approach)
        origin_lat, origin_lon = request.origin.latitude, request.origin.longitude
        
        enriched_suppliers = [
            {
                **supplier,
                "distance_km": haversine_distance(
                    origin_lat, origin_lon,
                    supplier["latitude"], supplier["longitude"]
                )
            }
            for supplier in suppliers_list
        ]
        
        # Rank suppliers (single pass)
        ranked = rank_suppliers(enriched_suppliers)
        
        # Filter eligible suppliers (sufficient stock)
        eligible = filter_eligible_suppliers(ranked, request.quantity_tons)
        
        # Determine recommended supplier or split plan
        recommended = None
        
        if eligible:
            # Best single supplier
            recommended = Supplier(**eligible[0])
        elif ranked:
            # Need split plan
            split_plan = create_split_plan(ranked, request.quantity_tons)
            if split_plan:
                recommended = Supplier(**split_plan[0])
        
        # Convert to Supplier objects (lazy evaluation)
        all_suppliers = [Supplier(**s) for s in ranked]
        
        # Build provenance
        provenance = Provenance(
            provider="mock-sandbox" if settings.SOURCE_MODE == "sandbox" else "live-api",
            cache=False,
            cache_age_seconds=None,
            request_id=request_id,
            generated_at=datetime.utcnow(),
            sources=["mock-suppliers-db", "haversine-distance-calc"]
        )
        
        # Create response
        response = SupplierBundle(
            origin=request.origin,
            material=request.material,
            quantity_tons=request.quantity_tons,
            suppliers=all_suppliers,
            recommended=recommended,
            ranking_criteria=["distance", "price", "lead_time"],
            provenance=provenance
        )
        
        # Cache the response
        await cache_manager.set(
            data=response.model_dump(),
            ttl_hours=settings.CACHE_TTL_HOURS,
            **cache_key_params
        )
        
        return response
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/suppliers/quote", response_model=Quote)
async def get_supplier_quote(request: QuoteRequest):
    """
    Request a price quote from a specific supplier with realistic price jitter.
    
    Applies ±1-2% price variation to simulate market conditions.
    """
    # Simulate latency
    await simulate_latency(settings.MIN_LATENCY_MS, settings.MAX_LATENCY_MS)
    
    request_id = generate_request_id()
    
    try:
        # Load supplier data
        supplier_data = load_supplier_data(request.material)
        suppliers_list = supplier_data.get("suppliers", [])
        
        # Find the requested supplier
        supplier_info = None
        for s in suppliers_list:
            if s["supplier_id"] == request.supplier_id:
                supplier_info = s
                break
        
        if not supplier_info:
            raise HTTPException(
                status_code=404,
                detail=f"Supplier {request.supplier_id} not found"
            )
        
        # Calculate distance
        distance = haversine_distance(
            request.origin.latitude,
            request.origin.longitude,
            supplier_info["latitude"],
            supplier_info["longitude"]
        )
        
        # Create supplier object
        supplier = Supplier(
            **supplier_info,
            distance_km=distance
        )
        
        # Apply price jitter (±1-2%)
        base_price = supplier_info["price_inr_per_ton"]
        quoted_price = apply_price_jitter(
            base_price,
            settings.PRICE_JITTER_MIN,
            settings.PRICE_JITTER_MAX
        )
        
        total_price = round(quoted_price * request.quantity_tons, 2)
        
        # Calculate ETA with jitter
        eta_days = estimate_delivery_eta(distance, supplier_info["lead_time_days"])
        eta_days_jittered = max(1, eta_days + random.choice([-2, -1, 0, 1, 2]))
        
        # Quote validity (48 hours)
        valid_until = datetime.utcnow() + timedelta(hours=48)
        
        # Generate quote ID
        quote_id = f"QUO-{datetime.utcnow().strftime('%Y%m%d')}-{request_id[-6:]}"
        
        # Build provenance
        provenance = Provenance(
            provider="mock-sandbox" if settings.SOURCE_MODE == "sandbox" else "live-api",
            cache=False,
            cache_age_seconds=None,
            request_id=request_id,
            generated_at=datetime.utcnow(),
            sources=["mock-pricing-engine", "market-data-feed"]
        )
        
        # Create quote
        quote = Quote(
            quote_id=quote_id,
            supplier=supplier,
            material=request.material,
            quantity_tons=request.quantity_tons,
            unit_price_inr=quoted_price,
            total_price_inr=total_price,
            valid_until=valid_until,
            notes=f"Price includes GST. Delivery in {eta_days_jittered} days. Subject to availability.",
            provenance=provenance
        )
        
        return quote
        
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/route/eta", response_model=RouteETA)
async def calculate_route_eta(request: RouteRequest):
    """
    Calculate route distance, ETA, and CO2 emissions for delivery.
    
    Uses Haversine distance, assumes 300 km/day travel speed,
    and calculates CO2 based on 0.06 kg per ton-km.
    """
    # Simulate latency
    await simulate_latency(settings.MIN_LATENCY_MS, settings.MAX_LATENCY_MS)
    
    request_id = generate_request_id()
    
    try:
        # Extract destination coordinates
        dest_lat = request.destination.get("latitude")
        dest_lon = request.destination.get("longitude")
        dest_name = request.destination.get("name", "Supplier Location")
        
        if dest_lat is None or dest_lon is None:
            raise HTTPException(
                status_code=400,
                detail="Destination must include 'latitude' and 'longitude'"
            )
        
        # Calculate distance
        distance = haversine_distance(
            request.origin.latitude,
            request.origin.longitude,
            dest_lat,
            dest_lon
        )
        
        # Calculate duration (assuming average speed of 300 km/day, 8 hours driving)
        hours_per_day = 8
        avg_speed_kmh = 40  # km/h in urban/semi-urban areas
        duration_hours = distance / avg_speed_kmh
        duration_minutes = int(duration_hours * 60)
        
        # Calculate ETA
        eta = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        # Calculate CO2 emissions if quantity provided
        co2_kg = 0.0
        if request.quantity_tons:
            co2_kg = calculate_co2_emissions(request.quantity_tons, distance)
        else:
            # Assume 10 tons for estimation
            co2_kg = calculate_co2_emissions(10.0, distance)
        
        # Determine route quality
        if distance < 10:
            route_quality = "optimal"
        elif distance < 30:
            route_quality = "good"
        else:
            route_quality = "fair"
        
        # Generate route ID
        route_id = f"ROUTE-{datetime.utcnow().strftime('%Y%m%d')}-{request_id[-6:]}"
        
        # Build provenance
        provenance = Provenance(
            provider="mock-sandbox" if settings.SOURCE_MODE == "sandbox" else "live-api",
            cache=False,
            cache_age_seconds=None,
            request_id=request_id,
            generated_at=datetime.utcnow(),
            sources=["mock-routing-engine", "haversine-distance", "co2-calculator"]
        )
        
        # Create response
        route_eta = RouteETA(
            route_id=route_id,
            origin=request.origin,
            destination={
                "latitude": dest_lat,
                "longitude": dest_lon,
                "name": dest_name
            },
            distance_km=distance,
            duration_minutes=duration_minutes,
            eta=eta,
            co2_kg=co2_kg,
            route_quality=route_quality,
            provenance=provenance
        )
        
        return route_eta
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/sources", response_model=SourcesResponse)
async def get_sources_health():
    """
    Check health status of all data source integrations.
    
    Returns overall system health and individual source statuses.
    """
    # Simulate latency
    await simulate_latency(100, 300)
    
    request_id = generate_request_id()
    now = datetime.utcnow()
    
    # Define mock sources and their health
    sources = [
        SourceHealth(
            source_name="mock-suppliers-db",
            status="healthy",
            response_time_ms=50,
            last_check=now,
            error_rate=0.0
        ),
        SourceHealth(
            source_name="haversine-distance-calc",
            status="healthy",
            response_time_ms=5,
            last_check=now,
            error_rate=0.0
        ),
        SourceHealth(
            source_name="mock-pricing-engine",
            status="healthy",
            response_time_ms=30,
            last_check=now,
            error_rate=0.0
        ),
        SourceHealth(
            source_name="mock-routing-engine",
            status="healthy",
            response_time_ms=45,
            last_check=now,
            error_rate=0.0
        ),
        SourceHealth(
            source_name="geoapify-api",
            status="sandbox",
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
        )
    ]
    
    # Determine overall status
    unhealthy_count = sum(1 for s in sources if s.status == "down")
    overall_status = "degraded" if unhealthy_count > 0 else "healthy"
    
    # Build provenance
    provenance = Provenance(
        provider="system-health-monitor",
        cache=False,
        cache_age_seconds=None,
        request_id=request_id,
        generated_at=now,
        sources=["internal-health-check"]
    )
    
    # Get cache stats
    cache_stats = cache_manager.get_stats()
    
    response = SourcesResponse(
        overall_status=overall_status,
        sources=sources,
        provenance=provenance
    )
    
    return response
