# FastAPI Commands & Project Structure Guide

## 🚀 FastAPI Run Commands (Like Flask)

### Simplest Way (Like `flask run`)
```bash
# Navigate to backend folder
cd backend

# Activate virtual environment
venv\Scripts\activate

# Run the app (simplest command)
uvicorn app:app --reload
```

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 📋 All FastAPI Run Commands

### 1. **Basic Run (Auto-reload for development)**
```bash
uvicorn app:app --reload
```
- ✅ Auto-reloads when you change code
- ✅ Default port: 8000
- ✅ Runs on localhost (local machine only)

### 2. **Run on Specific Port**
```bash
uvicorn app:app --port 5000 --reload
```
- Changes port from 8000 to 5000

### 3. **Run on All Network Interfaces (For others to connect)**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
- ✅ Accessible from other computers on network
- ✅ IP: Your computer IP:8000

### 4. **Production Mode (No auto-reload, faster)**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```
- ❌ No auto-reload
- ✅ Better performance
- ✅ Use this for deployment

### 5. **Multiple Workers (For production)**
```bash
uvicorn app:app --workers 4 --host 0.0.0.0 --port 8000
```
- ✅ Uses 4 CPU cores
- ✅ Better for high traffic

### 6. **With Logging**
```bash
uvicorn app:app --reload --log-level debug
```
- ✅ Shows detailed logs
- Options: debug, info, warning, error

---

## 🔄 Comparison: Flask vs FastAPI Commands

| Task | Flask | FastAPI |
|------|-------|---------|
| Simple run | `flask run` | `uvicorn app:app` |
| Specific port | `flask run --port 5000` | `uvicorn app:app --port 5000` |
| On all networks | `flask run --host 0.0.0.0` | `uvicorn app:app --host 0.0.0.0` |
| Production | `gunicorn app:app` | `uvicorn app:app --workers 4` |
| Auto-reload | `flask run` (default) | `uvicorn app:app --reload` |

---

## 📁 Project Structure Breakdown

```
backend/
├── venv/                           # Virtual environment (Python packages)
│   ├── Scripts/
│   │   ├── activate               # Activate environment (Windows)
│   │   ├── python.exe             # Python interpreter
│   │   └── uvicorn.exe            # Uvicorn server
│   └── Lib/site-packages/         # All installed packages
│
├── app.py                          # 🔴 MAIN ENTRY POINT
│   └── Creates FastAPI app
│   └── Registers routes
│   └── Configures middleware
│
├── config.py                       # Configuration & settings
│   └── Loads .env variables
│   └── Database connection string
│   └── API keys
│
├── database.py                     # Database connection helper
│   └── Creates SQL connections
│   └── Executes queries
│
├── models.py                       # Data validation (Pydantic)
│   └── RecommendationRequest
│   └── RecommendationResponse
│   └── BodyAnalysis
│
├── init_db.py                      # Database initialization
│   └── Creates tables
│   └── Inserts sample data
│
├── requirements.txt                # Python dependencies list
│   ├── fastapi
│   ├── uvicorn
│   ├── pydantic
│   ├── sqlalchemy
│   └── ... (25 total packages)
│
├── .env                            # 🔐 SECRET CONFIGURATION
│   ├── DB_SERVER=...
│   ├── OPENAI_API_KEY=...
│   └── Other secrets
│
├── routes/                         # API Endpoints
│   ├── __init__.py
│   ├── health.py                  # GET /health
│   └── recommendation.py           # POST /api/recommend
│
└── services/                       # Business Logic
    ├── recommendation_engine.py    # Scoring algorithm
    ├── image_analysis.py           # Image processing
    └── image_generation.py         # AI image creation
```

---

## 🔀 How Data Flows (Pin-to-Pin)

### Request Flow (User uploads image)

```
1. USER BROWSER (http://localhost:3000)
   ├─ Clicks "Upload Image"
   ├─ Selects photo
   ├─ Enters height, weight
   └─ Clicks "Get Recommendation"
                ↓
2. FRONTEND (React - src/api.js)
   ├─ Converts image to base64
   ├─ Creates JSON request
   └─ Sends HTTP POST to backend
                ↓
3. NETWORK
   └─ POST http://127.0.0.1:8000/api/recommend
                ↓
4. BACKEND - FASTAPI (routes/recommendation.py)
   ├─ Receives request
   ├─ Validates with Pydantic models
   └─ Calls RecommendationRequest validator
                ↓
5. IMAGE ANALYSIS (services/image_analysis.py)
   ├─ Decodes base64 image
   ├─ Uses PIL to open image
   ├─ Analyzes body proportions
   └─ Returns BodyAnalysis object
                ↓
6. RECOMMENDATION ENGINE (services/recommendation_engine.py)
   ├─ Gets all 20 motorcycles from database
   ├─ Scores each motorcycle (0-100)
   ├─ Considers: seat height, weight, price
   ├─ Considers: user height, weight, budget
   └─ Returns: Top motorcycle match
                ↓
7. IMAGE GENERATION (services/image_generation.py)
   ├─ Creates prompt: "User on motorcycle..."
   ├─ Calls OpenAI DALL-E 3 API
   ├─ Receives AI-generated image
   └─ Returns image URL
                ↓
8. BACKEND RESPONSE (routes/recommendation.py)
   ├─ Packages all data
   ├─ Creates RecommendationResponse object
   ├─ Converts to JSON
   └─ Returns HTTP 200 OK
                ↓
9. NETWORK
   ├─ HTTP response with JSON
   ├─ Includes: bike name, specs, score, image
   └─ Sent to frontend
                ↓
10. FRONTEND (React)
    ├─ Receives response
    ├─ Parses JSON
    ├─ Updates state
    └─ Re-renders UI
                ↓
11. USER BROWSER
    ├─ Sees recommended motorcycle
    ├─ Sees bike specifications
    ├─ Sees AI-generated image
    └─ ✅ SUCCESS!
```

---

## 🗄️ Database Flow

```
app.py imports config.py
    ↓
config.py loads .env file
    ↓
.env contains: DB_SERVER, DB_USER, DB_PASSWORD, USE_WINDOWS_AUTH
    ↓
database.py creates connection string
    ↓
pyodbc.connect() connects to SQL Server
    ↓
Connection is ready for queries
    ↓
When needed: SELECT * FROM Motorcycles
    ↓
Returns 20 motorcycle records
    ↓
Recommendation engine scores them
    ↓
Top match returned to user
```

---

## 🔧 How Everything Connects

### File Dependency Tree

```
app.py (MAIN)
  ├─ imports config.py
  │   ├─ Loads .env file
  │   └─ Returns settings object
  ├─ imports routes/health.py
  │   └─ GET /health endpoint
  ├─ imports routes/recommendation.py
  │   ├─ imports models.py (Pydantic validation)
  │   ├─ imports services/recommendation_engine.py
  │   │   └─ imports database.py
  │   │       └─ Queries Motorcycles table
  │   ├─ imports services/image_analysis.py
  │   │   └─ Analyzes uploaded image
  │   └─ imports services/image_generation.py
  │       └─ Calls OpenAI API
  └─ Registers all routes and middleware
```

---

## 🚀 Step-by-Step Setup for Interview Explanation

### "How I Built This From Scratch"

#### Step 1: Create Project Structure
```bash
# Created backend folder
mkdir backend
cd backend

# Created virtual environment
python -m venv venv

# Activated it
venv\Scripts\activate

# Created requirements.txt with packages list
```

#### Step 2: Install Dependencies
```bash
# Installed all packages
pip install -r requirements.txt
```

#### Step 3: Create Main App File (app.py)
```python
from fastapi import FastAPI
from routes import health_router, recommendation_router

app = FastAPI()

# Add routes
app.include_router(health_router)
app.include_router(recommendation_router)

# If running this file directly, start server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Step 4: Created Configuration (config.py)
- Loads secrets from .env file
- Prevents hardcoding passwords

#### Step 5: Created Database Connection (database.py)
- Connects to SQL Server using pyodbc
- Manages connection pooling
- Executes queries

#### Step 6: Created Data Models (models.py)
- Validates incoming requests
- Validates responses
- Uses Pydantic library

#### Step 7: Created Routes (routes/recommendation.py)
```
POST /api/recommend
  1. Receive image + user data
  2. Analyze image
  3. Find best motorcycle
  4. Generate AI image
  5. Return everything
```

#### Step 8: Created Services (services/)
- **image_analysis.py** - Processes images
- **recommendation_engine.py** - Scoring algorithm
- **image_generation.py** - Calls OpenAI

#### Step 9: Created Database Schema (init_db.py)
- CREATE TABLE Motorcycles (20 columns)
- INSERT 20 motorcycle records
- CREATE TABLE Recommendations (analytics)

#### Step 10: Created Frontend (React)
- Image upload form
- Send data to backend
- Display results

---

## 📊 How to Explain to Interview

### "Here's My Full Stack Application..."

**"Let me walk you through the architecture:**

1. **Frontend** (React on port 3000)
   - User uploads image
   - Enters their metrics (height, weight)
   - Sends HTTP POST request with base64 image

2. **Backend** (FastAPI on port 8000)
   - Receives request through `/api/recommend` route
   - Validates with Pydantic models
   - Calls image analysis service
   - Gets body proportions
   - Queries database for motorcycles
   - Scores each motorcycle (0-100 scale)
   - Top scorer is recommendation
   - Generates AI image using OpenAI
   - Returns JSON response

3. **Database** (SQL Server)
   - 20 motorcycle records
   - Each with 20+ columns
   - Includes: seat height, weight, price, specs, ratings

4. **External APIs**
   - OpenAI DALL-E for image generation
   - GPT-4 Vision for optional analysis

5. **The Key Innovation**
   - Smart matching algorithm
   - Considers user body metrics
   - Matches to motorcycle seat height + weight rating
   - Scores on: comfort, performance, price alignment
   - Returns best match with AI-generated preview image"

---

## 🔑 Key Commands to Remember

### For Running
```bash
# Development (with auto-reload)
uvicorn app:app --reload

# Production
uvicorn app:app --host 0.0.0.0 --port 8000

# Specific port
uvicorn app:app --port 5000 --reload
```

### For Database
```bash
# Initialize database
python init_db.py

# Check database
sqlcmd -S LAPTOP-75RD0HFK -E -d Bike_DB
```

### For Frontend
```bash
cd frontend
npm start
```

---

## 📝 Quick Facts

- **Language**: Python (backend) + JavaScript (frontend)
- **Framework**: FastAPI (backend) + React (frontend)
- **Database**: SQL Server 2022
- **Packages**: 25+ Python, 1300+ npm
- **Data**: 20 motorcycles
- **API Endpoints**: 2 main endpoints
- **Lines of Code**: 2500+ backend, 600+ frontend
- **Deployment Ready**: Yes ✅

---

## ✨ What Makes This Professional

1. ✅ Modular code (separate files for routes, services, models)
2. ✅ Configuration management (.env for secrets)
3. ✅ Data validation (Pydantic models)
4. ✅ Error handling (try-catch blocks)
5. ✅ Documentation (inline comments, README files)
6. ✅ Database design (normalized schema, indexes)
7. ✅ API documentation (Swagger UI at /docs)
8. ✅ CORS enabled (frontend-backend communication)
9. ✅ Scalable architecture (can add more features)
10. ✅ Production ready (can deploy to cloud)

---

This is a **full-stack, production-ready application** built with best practices! 🚀
