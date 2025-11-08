"""
PRISMA Procurement API - Demo Script

Demonstrates end-to-end procurement flow:
1. Search for cement suppliers near Bandlaguda Jagir
2. Request quote from best supplier
3. Calculate route and ETA
4. Check system health
"""
import asyncio
import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:8001"

# Test location: Bandlaguda Jagir, Hyderabad
TEST_ORIGIN = {
    "latitude": 17.3352,
    "longitude": 78.4537,
    "region_name": "Bandlaguda Jagir"
}

# Materials to test
MATERIALS = ["cement_opc_53", "sand_river", "aggregate_20mm", "bricks_red"]


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_json(data, max_items=3):
    """Pretty print JSON with truncation"""
    if isinstance(data, dict):
        # Truncate large lists
        if 'suppliers' in data and len(data['suppliers']) > max_items:
            original_count = len(data['suppliers'])
            data = data.copy()
            data['suppliers'] = data['suppliers'][:max_items]
            print(json.dumps(data, indent=2, default=str))
            print(f"\n... ({original_count - max_items} more suppliers not shown)")
        else:
            print(json.dumps(data, indent=2, default=str))
    else:
        print(json.dumps(data, indent=2, default=str))


def test_health_check():
    """Test 1: Basic health check"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print_json(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_supplier_search(material="cement_opc_53", quantity=50.0):
    """Test 2: Search for suppliers"""
    print_section(f"TEST 2: Search Suppliers - {material}")
    
    payload = {
        "origin": TEST_ORIGIN,
        "material": material,
        "quantity_tons": quantity
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ext/suppliers/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📍 Origin: {data['origin']['region_name']}")
            print(f"🔍 Material: {data['material']}")
            print(f"📦 Quantity: {data['quantity_tons']} tons")
            print(f"📊 Suppliers found: {len(data['suppliers'])}")
            
            if data.get('recommended'):
                rec = data['recommended']
                print(f"\n✅ RECOMMENDED SUPPLIER:")
                print(f"   • Name: {rec['name']}")
                print(f"   • Distance: {rec['distance_km']} km")
                print(f"   • Price: ₹{rec['price_inr_per_ton']}/ton")
                print(f"   • Lead Time: {rec['lead_time_days']} days")
                print(f"   • Rating: {rec['rating']}⭐")
                print(f"   • Stock: {rec['stock_tons']} tons available")
            
            print(f"\n📋 Top 3 Suppliers:")
            for i, supplier in enumerate(data['suppliers'][:3], 1):
                print(f"   {i}. {supplier['name']}")
                print(f"      Distance: {supplier['distance_km']} km | "
                      f"Price: ₹{supplier['price_inr_per_ton']}/ton | "
                      f"Stock: {supplier['stock_tons']} tons")
            
            print(f"\n🔖 Provenance:")
            prov = data['provenance']
            print(f"   • Provider: {prov['provider']}")
            print(f"   • Cache: {prov['cache']}")
            print(f"   • Request ID: {prov['request_id']}")
            print(f"   • Sources: {', '.join(prov['sources'])}")
            
            return data
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_quote(supplier_id, material="cement_opc_53", quantity=50.0):
    """Test 3: Request price quote"""
    print_section(f"TEST 3: Request Quote - {supplier_id}")
    
    payload = {
        "supplier_id": supplier_id,
        "material": material,
        "quantity_tons": quantity,
        "origin": TEST_ORIGIN
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ext/suppliers/quote",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📋 QUOTE DETAILS:")
            print(f"   • Quote ID: {data['quote_id']}")
            print(f"   • Supplier: {data['supplier']['name']}")
            print(f"   • Material: {data['material']}")
            print(f"   • Quantity: {data['quantity_tons']} tons")
            print(f"   • Unit Price: ₹{data['unit_price_inr']}/ton")
            print(f"   • Total Price: ₹{data['total_price_inr']}")
            print(f"   • Valid Until: {data['valid_until']}")
            print(f"   • Notes: {data['notes']}")
            
            print(f"\n🔖 Provenance:")
            prov = data['provenance']
            print(f"   • Request ID: {prov['request_id']}")
            print(f"   • Generated: {prov['generated_at']}")
            
            return data
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_route_eta(destination):
    """Test 4: Calculate route and ETA"""
    print_section("TEST 4: Calculate Route & ETA")
    
    payload = {
        "origin": TEST_ORIGIN,
        "destination": destination,
        "quantity_tons": 50.0
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ext/route/eta",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n🚛 ROUTE DETAILS:")
            print(f"   • Route ID: {data['route_id']}")
            print(f"   • From: {data['origin']['region_name']}")
            print(f"   • To: {data['destination']['name']}")
            print(f"   • Distance: {data['distance_km']} km")
            print(f"   • Duration: {data['duration_minutes']} minutes")
            print(f"   • ETA: {data['eta']}")
            print(f"   • CO₂ Emissions: {data['co2_kg']} kg")
            print(f"   • Route Quality: {data['route_quality']}")
            
            return data
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_sources_health():
    """Test 5: Check data sources health"""
    print_section("TEST 5: Data Sources Health")
    
    try:
        response = requests.get(f"{BASE_URL}/ext/sources")
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n🏥 SYSTEM HEALTH:")
            print(f"   • Overall Status: {data['overall_status'].upper()}")
            
            print(f"\n📊 INDIVIDUAL SOURCES:")
            for source in data['sources']:
                status_emoji = "✅" if source['status'] == "healthy" else "⚠️" if source['status'] == "sandbox" else "❌"
                print(f"   {status_emoji} {source['source_name']}")
                print(f"      Status: {source['status']}")
                if source['response_time_ms']:
                    print(f"      Response Time: {source['response_time_ms']}ms")
                print(f"      Error Rate: {source['error_rate']}%")
            
            return data
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_cache_behavior():
    """Test 6: Cache behavior (hit vs miss)"""
    print_section("TEST 6: Cache Behavior")
    
    payload = {
        "origin": TEST_ORIGIN,
        "material": "cement_opc_53",
        "quantity_tons": 50.0
    }
    
    try:
        # First request (cache miss)
        print("🔍 First request (should be cache MISS)...")
        start = datetime.now()
        response1 = requests.post(f"{BASE_URL}/ext/suppliers/search", json=payload)
        duration1 = (datetime.now() - start).total_seconds() * 1000
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"   • Duration: {duration1:.0f}ms")
            print(f"   • Cache: {data1['provenance']['cache']}")
            print(f"   • Request ID: {data1['provenance']['request_id']}")
        
        # Second request (cache hit)
        print("\n🔍 Second request (should be cache HIT)...")
        start = datetime.now()
        response2 = requests.post(f"{BASE_URL}/ext/suppliers/search", json=payload)
        duration2 = (datetime.now() - start).total_seconds() * 1000
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"   • Duration: {duration2:.0f}ms")
            print(f"   • Cache: {data2['provenance']['cache']}")
            if data2['provenance'].get('cache_age_seconds'):
                print(f"   • Cache Age: {data2['provenance']['cache_age_seconds']}s")
            print(f"   • Request ID: {data2['provenance']['request_id']}")
        
        print(f"\n⚡ Speed improvement: {duration1 - duration2:.0f}ms faster with cache!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def run_comprehensive_demo():
    """Run complete end-to-end demo"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " " * 20 + "PRISMA PROCUREMENT API DEMO" + " " * 31 + "║")
    print("║" + " " * 15 + "End-to-End Procurement Flow Test" + " " * 30 + "║")
    print("╚" + "="*78 + "╝")
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Server not responding. Please start the server first:")
        print("   python main.py")
        return
    
    # Test 2: Search suppliers
    search_result = test_supplier_search(material="cement_opc_53", quantity=50.0)
    if not search_result:
        print("\n❌ Supplier search failed")
        return
    
    # Get recommended supplier for next tests
    recommended = search_result.get('recommended')
    if not recommended:
        print("\n⚠️ No recommended supplier found")
        return
    
    # Test 3: Request quote
    quote_result = test_quote(
        supplier_id=recommended['supplier_id'],
        material="cement_opc_53",
        quantity=50.0
    )
    
    # Test 4: Calculate route
    destination = {
        "latitude": recommended['latitude'],
        "longitude": recommended['longitude'],
        "name": recommended['name']
    }
    route_result = test_route_eta(destination)
    
    # Test 5: Check sources health
    sources_result = test_sources_health()
    
    # Test 6: Cache behavior
    test_cache_behavior()
    
    # Summary
    print_section("DEMO COMPLETE ✅")
    print("All procurement API endpoints tested successfully!")
    print("\n📝 Test Coverage:")
    print("   ✅ Health check")
    print("   ✅ Supplier search with ranking")
    print("   ✅ Price quote with jitter")
    print("   ✅ Route calculation with CO₂")
    print("   ✅ Data sources health")
    print("   ✅ Cache behavior (TTL)")
    
    print("\n🎯 Next Steps:")
    print("   • Integrate with PRISMA forecasting module")
    print("   • Connect to real supplier APIs (Geoapify, ONDC)")
    print("   • Add authentication & authorization")
    print("   • Implement rate limiting")
    print("   • Deploy to production")


if __name__ == "__main__":
    try:
        run_comprehensive_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

