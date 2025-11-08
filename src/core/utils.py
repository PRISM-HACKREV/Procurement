"""
Core utility functions for PRISMA Procurement API
"""
import math
import random
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from functools import lru_cache
import json
import os


# Constants
EARTH_RADIUS_KM = 6371.0
CO2_EMISSION_FACTOR = 0.06  # kg CO2 per ton-km
AVG_SPEED_KM_PER_DAY = 300.0


@lru_cache(maxsize=128)
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth
    using the Haversine formula.
    
    Args:
        lat1, lon1: Coordinates of first point (degrees)
        lat2, lon2: Coordinates of second point (degrees)
        
    Returns:
        Distance in kilometers
    """
    # Convert degrees to radians once
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    delta_lat, delta_lon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    
    # Haversine formula (optimized)
    sin_dlat_2 = math.sin(delta_lat / 2)
    sin_dlon_2 = math.sin(delta_lon / 2)
    
    a = sin_dlat_2 * sin_dlat_2 + math.cos(lat1_rad) * math.cos(lat2_rad) * sin_dlon_2 * sin_dlon_2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return round(EARTH_RADIUS_KM * c, 2)


async def simulate_latency(min_ms: int = 200, max_ms: int = 600):
    """
    Simulate API latency with random delay between min_ms and max_ms milliseconds.
    """
    delay_ms = random.randint(min_ms, max_ms)
    await asyncio.sleep(delay_ms / 1000.0)


def generate_request_id() -> str:
    """Generate a unique request ID for tracing."""
    return f"req-{uuid.uuid4().hex[:12]}"


def apply_price_jitter(base_price: float, min_factor: float = 0.99, max_factor: float = 1.02) -> float:
    """
    Apply random price jitter (±1-2%) to simulate market fluctuations.
    
    Args:
        base_price: Base price per unit
        min_factor: Minimum multiplier (0.99 = -1%)
        max_factor: Maximum multiplier (1.02 = +2%)
        
    Returns:
        Adjusted price with jitter
    """
    jitter = random.uniform(min_factor, max_factor)
    return round(base_price * jitter, 2)


def calculate_co2_emissions(quantity_tons: float, distance_km: float) -> float:
    """
    Calculate CO2 emissions for material transport.
    
    Formula: 0.06 kg CO2 per ton-km (typical for heavy truck transport)
    
    Args:
        quantity_tons: Material quantity in tons
        distance_km: Transport distance in kilometers
        
    Returns:
        CO2 emissions in kilograms
    """
    return round(quantity_tons * distance_km * CO2_EMISSION_FACTOR, 2)


def estimate_delivery_eta(distance_km: float, base_lead_time_days: int = 0) -> int:
    """
    Estimate delivery time based on distance.
    
    Formula: distance / 300 km/day (min 0.5 days) + base_lead_time
    
    Args:
        distance_km: Distance in kilometers
        base_lead_time_days: Supplier's base lead time
        
    Returns:
        Estimated delivery time in days
    """
    travel_days = max(0.5, distance_km / AVG_SPEED_KM_PER_DAY)
    return base_lead_time_days + int(math.ceil(travel_days))


# Material ID to filename mapping (constant)
MATERIAL_FILE_MAP = {
    "cement_opc_53": "cement_suppliers_mock.json",
    "cement": "cement_suppliers_mock.json",
    "sand_river": "sand_suppliers_mock.json",
    "sand": "sand_suppliers_mock.json",
    "aggregate_20mm": "aggregate_suppliers_mock.json",
    "aggregate": "aggregate_suppliers_mock.json",
    "gravel": "aggregate_suppliers_mock.json",
    "bricks_red": "bricks_suppliers_mock.json",
    "bricks": "bricks_suppliers_mock.json"
}

# Cache for loaded supplier data
_supplier_data_cache: Dict[str, Dict[str, Any]] = {}


def load_supplier_data(material_id: str) -> Dict[str, Any]:
    """
    Load supplier data from JSON file with caching.
    
    Args:
        material_id: Material identifier (e.g., 'cement_opc_53')
        
    Returns:
        Dictionary containing supplier data
    """
    material_key = material_id.lower()
    
    # Return from cache if available
    if material_key in _supplier_data_cache:
        return _supplier_data_cache[material_key]
    
    # Get filename from mapping
    filename = MATERIAL_FILE_MAP.get(material_key)
    if not filename:
        raise ValueError(f"Unknown material_id: {material_id}")
    
    # Get the data directory path
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(current_dir, "data", filename)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Cache the loaded data
            _supplier_data_cache[material_key] = data
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Supplier data file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in supplier data file: {e}")


def should_trigger_rate_limit() -> bool:
    """
    Randomly trigger rate limit (429) with 1/20 probability (5% chance).
    """
    return random.randint(1, 20) == 1


def get_retry_after_seconds() -> int:
    """
    Get random retry-after delay in seconds (1-3 seconds).
    """
    return random.randint(1, 3)


def rank_suppliers(suppliers: List[Dict[str, Any]], 
                   criteria: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Rank suppliers by multiple criteria (distance → price → lead_time).
    
    Args:
        suppliers: List of supplier dictionaries
        criteria: Ranking criteria in order of priority
        
    Returns:
        Sorted list of suppliers
    """
    if not suppliers:
        return []
    
    # Default criteria
    if criteria is None:
        criteria = ["distance_km", "price_inr_per_ton", "lead_time_days"]
    
    # Optimized multi-criteria sorting
    return sorted(
        suppliers,
        key=lambda s: tuple(s.get(c, float('inf')) for c in criteria)
    )


def filter_eligible_suppliers(suppliers: List[Dict[str, Any]], 
                               required_quantity: float) -> List[Dict[str, Any]]:
    """
    Filter suppliers that have sufficient stock.
    
    Args:
        suppliers: List of supplier dictionaries
        required_quantity: Required quantity in tons
        
    Returns:
        List of eligible suppliers
    """
    return [s for s in suppliers if s.get("stock_tons", 0) >= required_quantity]


def create_split_plan(suppliers: List[Dict[str, Any]], 
                      required_quantity: float) -> List[Dict[str, Any]]:
    """
    Create a split procurement plan if no single supplier can meet demand.
    
    Args:
        suppliers: List of ranked suppliers
        required_quantity: Required quantity in tons
        
    Returns:
        List of suppliers with allocated quantities
    """
    if not suppliers:
        return []
    
    split_plan = []
    remaining = required_quantity
    
    # Sort by best ranking (already sorted)
    for supplier in suppliers[:3]:  # Max 3 suppliers in split
        available = supplier.get("stock_tons", 0)
        if available <= 0:
            continue
            
        allocation = min(available, remaining)
        if allocation > 0:
            split_supplier = supplier.copy()
            split_supplier["allocated_tons"] = round(allocation, 2)
            split_supplier["estimated_cost_inr"] = round(
                allocation * supplier.get("price_inr_per_ton", 0), 2
            )
            split_plan.append(split_supplier)
            remaining -= allocation
            
        if remaining <= 0:
            break
    
    return split_plan
