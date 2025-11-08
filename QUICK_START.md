# PRISMA Procurement API - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Start the Server

```bash
cd "C:\Users\MUSTAFA IDRIS HASAN\Desktop\Proccurement"
python main.py
```

Server runs on: **http://localhost:8001**

### Step 2: Test the API

Open your browser:
- **API Documentation:** http://localhost:8001/docs
- **Health Check:** http://localhost:8001/

### Step 3: Run Demo

```bash
python scripts/demo.py
```

---

## 💡 Quick Examples

### Example 1: Find Cement Suppliers

```bash
curl -X POST http://localhost:8001/ext/suppliers/search \
  -H "Content-Type: application/json" \
  -d "{\"origin\": {\"latitude\": 17.3352, \"longitude\": 78.4537, \"region_name\": \"Bandlaguda Jagir\"}, \"material\": \"cement_opc_53\", \"quantity_tons\": 50.0}"
```

**Result:** 15 suppliers, ranked by distance → price → lead time

### Example 2: Get Price Quote

```bash
curl -X POST http://localhost:8001/ext/suppliers/quote \
  -H "Content-Type: application/json" \
  -d "{\"supplier_id\": \"SUP-CEM-001\", \"material\": \"cement_opc_53\", \"quantity_tons\": 50.0, \"origin\": {\"latitude\": 17.3352, \"longitude\": 78.4537}}"
```

**Result:** Quote with ±1-2% price jitter

### Example 3: Calculate Route & CO₂

```bash
curl -X POST http://localhost:8001/ext/route/eta \
  -H "Content-Type: application/json" \
  -d "{\"origin\": {\"latitude\": 17.3352, \"longitude\": 78.4537}, \"destination\": {\"latitude\": 17.3345, \"longitude\": 78.4512, \"name\": \"Supplier\"}, \"quantity_tons\": 50.0}"
```

**Result:** Distance, ETA, CO₂ emissions

---

## 📚 Available Materials

- `cement_opc_53` - Portland Cement
- `sand_river` - River Sand (M-Sand)
- `aggregate_20mm` - Gravel
- `bricks_red` - Red Clay Bricks

---

## 🌍 Hyderabad Regions

- **Bandlaguda Jagir** (17.3352, 78.4537)
- **Mehdipatnam** (17.3948, 78.4370)
- **Attapur** (17.3670, 78.4380)
- **Langar Houz** (17.3810, 78.4290)
- **Rajendranagar** (17.3210, 78.4020)

---

## 🎯 What's Working

✅ **All endpoints operational**
- Health checks
- Supplier search with ranking
- Price quotes with jitter
- Route calculation with CO₂
- System health monitoring

✅ **60+ mock suppliers loaded**
- 15 per material
- 3 per region
- Realistic prices, stock, ratings

✅ **Core features enabled**
- Haversine distance calculation
- Intelligent ranking algorithm
- 24-hour caching
- Latency simulation
- Provenance tracking

✅ **Tests passing: 6/6 (100%)**

---

## 📖 Documentation

- **Full README:** `README.md`
- **API Docs:** http://localhost:8001/docs
- **Test Results:** `TEST_RESULTS.md`
- **Implementation:** `IMPLEMENTATION_SUMMARY.md`
- **Demo Guide:** `scripts/demo.md`

---

## 🔧 Troubleshooting

**Server won't start?**
```bash
pip install -r requirements.txt
```

**Port 8001 in use?**
```bash
# Edit .env
API_PORT=8002
```

**Import errors?**
```bash
cd "C:\Users\MUSTAFA IDRIS HASAN\Desktop\Proccurement"
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## ✨ Next Steps

1. ✅ **System is ready** - All tests passed
2. 🔗 **Integrate with PRISMA** - Connect to forecasting module
3. 🌐 **Connect real APIs** - Replace mocks with Geoapify/ONDC
4. 🚀 **Deploy to production** - AWS/Azure/GCP

---

**Questions? Check:** `README.md` or `IMPLEMENTATION_SUMMARY.md`

**Everything is ready to go!** 🎉

