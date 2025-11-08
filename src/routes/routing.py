"""
Route and ETA calculation endpoints
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta

from src.domain.schemas import RouteETA, Provenance
from src.domain.requests import RouteETARequest
from src.core.utils import (
    haversine_distance, calculate_eta_days, calculate_co2_emissions,
    simulate_latency, should_simulate_rate_limit, generate_route_id,
    get_provenance
)

router = APIRouter(prefix="/ext/route", tags=["Routing"])


@router.post("/eta", response_model=RouteETA)
async def calculate_route_eta(request: RouteETARequest):
    """
    Calculate route distance, ETA, and CO2 emissions.
    
    Uses Haversine distance formula and standard transport calculations:
    - ETA: distance / 300 km/day (minimum 0.5 days)
    - CO2: 0.06 kg per ton-km
    """
    # Simulate rate limiting
    if should_simulate_rate_limit():
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": "2"}
        )
    
    # Simulate API latency
    await simulate_latency()
    
    # Extract coordinates
    origin_lat = request.origin.latitude
    origin_lon = request.origin.longitude
    dest_lat = request.destination.get('latitude')
    dest_lon = request.destination.get('longitude')
    
    if dest_lat is None or dest_lon is None:
        raise HTTPException(
            status_code=400,
            detail="Destination must include 'latitude' and 'longitude'"
        )
    
    # Calculate distance
    distance_km = haversine_distance(origin_lat, origin_lon, dest_lat, dest_lon)
    
    # Calculate ETA
    eta_days = calculate_eta_days(distance_km)
    eta_datetime = datetime.utcnow() + timedelta(days=eta_days)
    
    # Calculate duration in minutes (assuming 40 km/h average speed)
    duration_minutes = int((distance_km / 40.0) * 60)
    
    # Calculate CO2 emissions (default to 1 ton if not specified)
    quantity = request.quantity_tons if request.quantity_tons else 1.0
    co2_kg = calculate_co2_emissions(quantity, distance_km)
    
    # Determine route quality
    if distance_km < 10:
        route_quality = "optimal"
    elif distance_km < 30:
        route_quality = "good"
    else:
        route_quality = "fair"
    
    # Build response
    route = RouteETA(
        route_id=generate_route_id(),
        origin=request.origin,
        destination=request.destination,
        distance_km=distance_km,
        duration_minutes=duration_minutes,
        eta=eta_datetime,
        co2_kg=co2_kg,
        route_quality=route_quality,
        provenance=Provenance(**get_provenance(
            sources=["haversine-distance-calc", "mock-routing-engine", "co2-calculator"]
        ))
    )
    
    return route

