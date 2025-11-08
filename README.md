# PRISMA Procurement & Supplier Integration Layer

**AI-driven supplier search and procurement simulation for construction materials in Hyderabad**

This is a mock procurement engine that determines where to buy construction materials from, simulating realistic supplier APIs with distance calculations, price quotes, lead times, and ETAs.

---

## 🎯 Overview

PRISMA forecasts future material demand using LLM-based schema understanding (Ollama/Mistral) and LightGBM models. This **Procurement & Supplier Integration Layer** extends PRISMA by answering:

> "Given a demand forecast of **50 tons of cement** at **Bandlaguda Jagir**, where should we buy it from?"

### Core Features

- ✅ **Mock supplier data** for cement, sand, gravel, and bricks
- ✅ **Haversine distance calculation** from request origin
- ✅ **Intelligent ranking**: distance → price → lead time
- ✅ **Price quotes** with realistic ±1–2% jitter
- ✅ **Route & ETA calculation** with CO₂ emissions
- ✅ **Sandbox mode** with 200–600ms latency simulation
- ✅ **Caching** with 24-hour TTL
- ✅ **Retry logic** for 429 rate limits
- ✅ **Provenance metadata** on every response

---

## 🏗️ Supported Materials & Regions

### Materials
- **Cement** (Portland Cement)
- **Sand** (Construction Grade)
- **Gravel** (Aggregate)
- **Bricks** (Red Clay Bricks)

### Hyderabad Regions
- Bandlaguda Jagir
- Mehdipatnam
- Attapur
- Langar Houz
- Rajendranagar

Each material has **3 mock suppliers per region** with realistic stock, prices, ratings, and locations.

---

## 📦 Project Structure

```
Proccurement/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Configuration (USE_MOCK=true)
├── README.md              # This file
│
├── src/
│   ├── routes/            # API route handlers
│   ├── domain/            # Pydantic schemas & models
│   │   └── schemas.py     # All data contracts
│   └── core/              # Configuration & utilities
│       └── config.py      # Environment settings
│
└── data/                  # Mock JSON data
    ├── cement_suppliers_mock.json
    ├── sand_suppliers_mock.json
    ├── gravel_suppliers_mock.json
    └── bricks_suppliers_mock.json
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Ensure `.env` has:

```env
USE_MOCK=true
SOURCE_MODE=sandbox
API_PORT=8000
```

### 3. Run Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --port 8000
```

### 4. Test Health Endpoint

```bash
curl http://localhost:8000/
```

**Expected Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "mode": "sandbox",
  "timestamp": "2025-11-08T10:30:00Z"
}
```

---

## 📡 API Endpoints

### 1. `/ext/suppliers/search` - Supplier Search

**POST** `/ext/suppliers/search`

Find and rank suppliers based on location, material, and quantity.

#### Request Body

```json
{
  "origin": {
    "latitude": 17.3352,
    "longitude": 78.4537,
    "region_name": "Bandlaguda Jagir"
  },
  "material": "cement",
  "quantity_tons": 50.0
}
```

#### Response (`SupplierBundle`)

```json
{
  "origin": {
    "latitude": 17.3352,
    "longitude": 78.4537,
    "region_name": "Bandlaguda Jagir"
  },
  "material": "cement",
  "quantity_tons": 50.0,
  "suppliers": [
    {
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
  ],
  "recommended": {
    "supplier_id": "SUP-CEM-001",
    "name": "Bandlaguda Cement Depot",
    "distance_km": 2.3
  },
  "ranking_criteria": ["distance", "price", "lead_time"],
  "provenance": {
    "provider": "mock-sandbox",
    "cache": false,
    "cache_age_seconds": null,
    "request_id": "req-abc123def456",
    "generated_at": "2025-11-08T10:30:00Z",
    "sources": ["mock-suppliers-db", "haversine-distance-calc"]
  }
}
```

---

### 2. `/ext/suppliers/quote` - Price Quote

**POST** `/ext/suppliers/quote`

Request a price quote from a specific supplier with ±1–2% jitter.

#### Request Body

```json
{
  "supplier_id": "SUP-CEM-001",
  "material": "cement",
  "quantity_tons": 50.0,
  "origin": {
    "latitude": 17.3352,
    "longitude": 78.4537
  }
}
```

#### Response (`Quote`)

```json
{
  "quote_id": "QUO-20251108-001",
  "supplier": {
    "supplier_id": "SUP-CEM-001",
    "name": "Bandlaguda Cement Depot",
    "price_inr_per_ton": 6800.0
  },
  "material": "cement",
  "quantity_tons": 50.0,
  "unit_price_inr": 6850.0,
  "total_price_inr": 342500.0,
  "valid_until": "2025-11-10T10:30:00Z",
  "notes": "Price includes GST. Subject to availability.",
  "provenance": {
    "provider": "mock-sandbox",
    "cache": false,
    "request_id": "req-quote-xyz789",
    "generated_at": "2025-11-08T10:30:00Z",
    "sources": ["mock-pricing-engine"]
  }
}
```

---

### 3. `/ext/route/eta` - Route & ETA Calculation

**POST** `/ext/route/eta`

Calculate distance, ETA, and CO₂ emissions for delivery route.

#### Request Body

```json
{
  "origin": {
    "latitude": 17.3352,
    "longitude": 78.4537,
    "region_name": "Bandlaguda Jagir"
  },
  "destination": {
    "latitude": 17.3345,
    "longitude": 78.4512,
    "name": "Bandlaguda Cement Depot"
  }
}
```

#### Response (`RouteETA`)

```json
{
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
    "cache": false,
    "request_id": "req-route-456",
    "generated_at": "2025-11-08T10:30:00Z",
    "sources": ["mock-routing-engine"]
  }
}
```

---

### 4. `/ext/sources` - Integration Health

**GET** `/ext/sources`

Check health status of all data source integrations.

#### Response (`SourcesResponse`)

```json
{
  "overall_status": "healthy",
  "sources": [
    {
      "source_name": "mock-suppliers-db",
      "status": "healthy",
      "response_time_ms": 50,
      "last_check": "2025-11-08T10:30:00Z",
      "error_rate": 0.0
    },
    {
      "source_name": "haversine-distance-calc",
      "status": "healthy",
      "response_time_ms": 5,
      "last_check": "2025-11-08T10:30:00Z",
      "error_rate": 0.0
    },
    {
      "source_name": "mock-pricing-engine",
      "status": "healthy",
      "response_time_ms": 30,
      "last_check": "2025-11-08T10:30:00Z",
      "error_rate": 0.0
    }
  ],
  "provenance": {
    "provider": "mock-sandbox",
    "cache": false,
    "request_id": "req-health-789",
    "generated_at": "2025-11-08T10:30:00Z",
    "sources": ["system-health-monitor"]
  }
}
```

---

## 📊 Data Schemas

### Core Models

#### `Origin`
Request origin location.

```json
{
  "latitude": 17.3352,
  "longitude": 78.4537,
  "region_name": "Bandlaguda Jagir"
}
```

#### `Supplier`
Individual supplier details.

```json
{
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
```

#### `Provenance`
Response metadata and traceability.

```json
{
  "provider": "mock-sandbox",
  "cache": false,
  "cache_age_seconds": null,
  "request_id": "req-abc123def456",
  "generated_at": "2025-11-08T10:30:00Z",
  "sources": ["mock-suppliers-db", "haversine-distance-calc"]
}
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_MOCK` | `true` | Enable mock data mode |
| `SOURCE_MODE` | `sandbox` | Operating mode (sandbox/live) |
| `API_PORT` | `8000` | Server port |
| `MIN_LATENCY_MS` | `200` | Minimum simulated latency |
| `MAX_LATENCY_MS` | `600` | Maximum simulated latency |
| `CACHE_TTL_HOURS` | `24` | Cache time-to-live |
| `PRICE_JITTER_MIN` | `0.99` | Minimum price multiplier (−1%) |
| `PRICE_JITTER_MAX` | `1.02` | Maximum price multiplier (+2%) |

---

## 🔧 Development

### Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Testing Endpoints

```bash
# Health check
curl http://localhost:8000/

# Supplier search (example)
curl -X POST http://localhost:8000/ext/suppliers/search \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"latitude": 17.3352, "longitude": 78.4537, "region_name": "Bandlaguda Jagir"},
    "material": "cement",
    "quantity_tons": 50.0
  }'
```

---

## 🎨 Design Principles

1. **Mock but Realistic**: Data looks like it came from real APIs (Geoapify, ONDC)
2. **Latency Simulation**: 200–600ms delays to mimic network calls
3. **Provenance First**: Every response includes source metadata
4. **Ranking Intelligence**: Distance → price → lead time priority
5. **Sandbox Mode**: Safe testing environment with controlled behavior

---

## 📝 Next Steps

1. ✅ **Step 1 Complete**: Scaffold & contracts
2. ⏳ **Step 2**: Mock data generation
3. ⏳ **Step 3**: Haversine distance calculation
4. ⏳ **Step 4**: Implement API endpoints
5. ⏳ **Step 5**: Caching & retry logic
6. ⏳ **Step 6**: Testing & validation

---

## 📄 License

MIT License - Part of the PRISMA supply chain optimization system.

---

**Built with ❤️ for intelligent construction procurement**

#   P r o c u r e m e n t  
 