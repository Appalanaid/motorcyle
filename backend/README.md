"""
README - Motorcycle Recommendation Backend API

## Architecture Overview

```
backend/
├── app.py                    # Main FastAPI application entry point
├── config.py                 # Configuration management (env variables)
├── database.py              # SQL Server database connection utilities
├── models.py                # Pydantic data models and schemas
├── init_db.py              # Database initialization script
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── routes/
│   ├── __init__.py
│   ├── health.py           # Health check endpoints
│   └── recommendation.py    # Main recommendation API endpoint
└── services/
    ├── __init__.py
    ├── image_analysis.py    # Body analysis using MediaPipe + OpenAI
    ├── recommendation_engine.py  # Rule-based bike recommendation logic
    └── image_generation.py  # AI image generation using DALL-E
```

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- SQL Server with Bike_DB database
- OpenAI API key (for image generation)
- ODBC Driver 17 for SQL Server installed

### 2. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Copy `.env.example` to `.env` and fill in your values:

```env
DB_SERVER=your_server_name
DB_DATABASE=Bike_DB
DB_USER=your_username
DB_PASSWORD=your_password
OPENAI_API_KEY=sk-...
```

### 4. Database Initialization

```bash
# Create tables and insert sample data
python init_db.py
```

### 5. Run the API

```bash
# Development mode with auto-reload
python app.py

# Or use uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: http://localhost:8000

## API Endpoints

### Health Check
- **GET /health** - Service status
- **GET /info** - API information
- **GET /** - API overview

### Main Endpoints

#### POST /api/recommend
Generate motorcycle recommendation based on user photo and characteristics.

**Request:**
```json
{
  "image_base64": "data:image/jpeg;base64,...",
  "height_cm": 175,
  "weight_kg": 75,
  "riding_preference": "commute",
  "generate_image": true
}
```

**Response:**
```json
{
  "bike": {
    "bike_id": 1,
    "name": "CB300F",
    "brand": "Honda",
    "seat_height_cm": 73,
    "weight_kg": 130,
    "engine_cc": 300,
    "riding_style": "naked",
    "suitability_score": 92.5
  },
  "body_analysis": {
    "inseam_cm": 81.4,
    "torso_length_cm": 64.2,
    "arm_reach_cm": 180.3,
    "posture_type": "upright",
    "confidence": 0.85
  },
  "recommendation_reason": "...",
  "generated_image_url": "https://...",
  "suitability_details": {
    "seat_height": 95.0,
    "weight": 88.5,
    "ergonomics": 92.0,
    "overall": 92.5
  }
}
```

#### GET /api/motorcycles
List all available motorcycles in database.

**Response:**
```json
{
  "count": 11,
  "motorcycles": [
    {
      "id": 1,
      "name": "Honda CB300F",
      "seat_height_cm": 73,
      "weight_kg": 130,
      "engine_cc": 300,
      "style": "naked"
    }
  ]
}
```

## Key Components

### 1. Image Analysis (services/image_analysis.py)
- Uses **MediaPipe** for pose detection and landmark extraction
- Estimates body proportions based on height/weight and posture
- Calculates inseam, torso length, and arm reach
- Confidence scoring for analysis reliability

### 2. Recommendation Engine (services/recommendation_engine.py)
- **Rule-based matching** of user characteristics to motorcycles
- Scoring criteria:
  - **Seat Height Match** (45% weight): Ideal within ±5cm of inseam
  - **Weight Compatibility** (25% weight): Optimal user/bike weight ratio
  - **Riding Preference** (30% weight): Style matching (sport, touring, cruiser)
- Database queries for motorcycle specifications
- Sample motorcycle data included for development

### 3. Image Generation (services/image_generation.py)
- **OpenAI DALL-E 3** API integration
- Generates photorealistic images of rider with recommended bike
- Prompt engineering based on:
  - Physical characteristics (height, weight, BMI)
  - Riding position (upright, sporty, cruiser)
  - Motorcycle specifications
- Image size options: 1024x1024, 1792x1024, 1024x1792

### 4. Database Integration (database.py)
- SQL Server connection via ODBC
- Connection pooling for efficiency
- Parameterized queries for security
- Error handling and logging

## Database Schema

### Motorcycles Table
```sql
CREATE TABLE Motorcycles (
    bike_id INT PRIMARY KEY IDENTITY,
    name NVARCHAR(100),
    brand NVARCHAR(100),
    seat_height_cm FLOAT,
    weight_kg FLOAT,
    engine_cc INT,
    riding_style NVARCHAR(50),  -- 'naked', 'sport', 'cruiser', 'adventure'
    year INT,
    price_usd DECIMAL,
    comfort_rating FLOAT,
    performance_rating FLOAT,
    reliability_rating FLOAT,
    active BIT
)
```

### Recommendations Table (Analytics)
```sql
CREATE TABLE Recommendations (
    recommendation_id INT PRIMARY KEY IDENTITY,
    user_height_cm FLOAT,
    user_weight_kg FLOAT,
    riding_preference NVARCHAR(50),
    recommended_bike_id INT,
    overall_score FLOAT,
    seat_height_score FLOAT,
    weight_score FLOAT,
    preference_score FLOAT,
    image_url NVARCHAR(MAX),
    generated_image_url NVARCHAR(MAX),
    created_date DATETIME
)
```

## Scoring Algorithm

### Seat Height Score
- Perfect fit: inseam ±5cm → 100%
- Acceptable: 5-10cm difference → 85% - (excess × 3)
- Fair: 10-15cm difference → 70% - (excess × 2)
- Poor: >15cm difference → 60% - excess

### Weight Score
- Optimal ratio 1.0 (user = bike weight): 100%
- Range 0.5-1.5 (user 50-150% of bike): 100 - |ratio - 1.0| × 50
- Light riders (<0.5): 60 + ratio × 80
- Heavy riders (>1.5): 100 - min(40, excess × 40)

### Preference Score
- Perfect match: 95-100%
- Good match: 80-90%
- Acceptable: 60-70%
- Poor: 30-40%

### Overall Score
Final Score = (Seat × 0.45) + (Weight × 0.25) + (Preference × 0.30)

## Error Handling

Consistent error responses:
```json
{
  "error": "Invalid input",
  "detail": "Height must be between 1 and 250 cm",
  "status_code": 400
}
```

Status codes:
- 200: Success
- 400: Invalid input
- 500: Server error

## Development Notes

### Adding New Motorcycles
Insert directly into database or modify `insert_sample_motorcycles()` in init_db.py

### Customizing Recommendation Logic
Edit `RecommendationEngine` in services/recommendation_engine.py:
- Adjust weights in `calculate_overall_score()`
- Modify threshold values in scoring methods
- Add new scoring criteria

### Extending Image Analysis
Current implementation uses MediaPipe basics. To improve:
- Calculate detailed joint angles
- Implement posture classification (upright/sporty/cruiser)
- Use OpenAI Vision API for detailed analysis
- Extract clothing detection for realism

### Testing
```bash
# Using curl
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "...",
    "height_cm": 175,
    "weight_kg": 75,
    "riding_preference": "commute",
    "generate_image": false
  }'

# Using Python
import requests
response = requests.post(
    'http://localhost:8000/api/recommend',
    json={...}
)
```

## Performance Considerations

- Image processing: ~2-3 seconds
- Motorcycle matching: ~100ms
- AI image generation: ~30-60 seconds
- Total request: ~35-65 seconds (with image generation)

## Security Notes

- Parameterized SQL queries prevent injection
- CORS configured for frontend origin
- Input validation on all endpoints
- Environment variables for sensitive data
- HTTPS recommended for production

## Future Enhancements

1. User authentication and history
2. Advanced posture analysis using OpenAI Vision
3. Multi-language support
4. Caching of recommendations
5. Motorcycle comparison endpoint
6. Dealer locator integration
7. Test ride booking
8. Community reviews and ratings
"""
