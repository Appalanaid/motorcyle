# React Frontend - Motorcycle Recommendation

## Architecture Overview

```
frontend/
├── public/
│   └── index.html           # HTML entry point
├── src/
│   ├── components/
│   │   ├── RecommendationForm.js       # Form for user input & image upload
│   │   ├── RecommendationForm.css      # Form styling
│   │   ├── RecommendationResult.js     # Results display
│   │   ├── RecommendationResult.css    # Results styling
│   │   ├── LoadingSpinner.js           # Loading indicator
│   │   └── LoadingSpinner.css          # Loading spinner styling
│   ├── api.js               # API client and utilities
│   ├── App.js              # Main app component
│   ├── App.css             # App styling
│   ├── index.js            # React entry point
│   └── index.css           # Global styles
└── package.json            # Dependencies
```

## Setup Instructions

### Prerequisites
- Node.js 14+ and npm installed

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file (optional, for custom API URL)
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

### Running Development Server

```bash
npm start
```

The app will open at http://localhost:3000

### Building for Production

```bash
npm run build
```

Creates optimized build in `build/` directory.

## Features

### 1. Recommendation Form
- **Image Upload**: Full-body photo with preview
- **Physical Metrics**: Height and weight input
- **Riding Preference**: Dropdown for commute/touring/sport
- **AI Image Generation**: Optional toggle
- **Input Validation**: Real-time error checking
- **Responsive Design**: Works on mobile and desktop

### 2. Recommendation Results
- **Motorcycle Details**: Name, brand, specs
- **Suitability Scores**: Overall match percentage
- **Score Breakdown**: Seat height, weight, ergonomics scores
- **Body Analysis**: Estimated inseam, torso, arm reach
- **Recommendation Reason**: Human-readable explanation
- **Generated Image**: AI image of user with recommended bike (if enabled)
- **Action Buttons**: Get new recommendation or compare bikes

### 3. Loading States
- **Spinner Overlay**: Shows during API requests
- **Progress Message**: Tells user what's happening
- **Disabled Input**: Prevents resubmission while loading

## Component Details

### RecommendationForm.js
Handles user input and image upload.

**State:**
```javascript
{
  height: string,           // User height in cm
  weight: string,           // User weight in kg
  preference: string,       // commute/touring/sport
  generateImage: boolean    // Generate AI image
}
```

**Props:**
- `onRecommendationReceived(result)` - Called when API returns recommendation
- `onLoading(isLoading)` - Called to update loading state

**Validation:**
- Image file size < 10MB
- Height: 1-250 cm
- Weight: 1-300 kg
- Valid MIME type (image/*)

### RecommendationResult.js
Displays recommendation and analysis results.

**Props:**
- `recommendation` - API response with bike, analysis, scores
- `onNewRecommendation()` - Called to reset form

**Data Display:**
- Motorcycle specifications
- Suitability scores with progress bar
- Score breakdown by category
- Body analysis metrics
- Generated AI image (if available)

### LoadingSpinner.js
Shows loading indicator during API requests.

**Props:**
- `message` (optional) - Loading status message

## API Integration

### Endpoints Used

#### POST /api/recommend
Send recommendation request with image and user data.

**Request:**
```javascript
{
  image_base64: string,           // Base64 encoded image
  height_cm: number,              // Height in cm
  weight_kg: number,              // Weight in kg
  riding_preference: string,      // commute/touring/sport
  generate_image: boolean         // Generate AI image
}
```

**Response:**
```javascript
{
  bike: {
    bike_id, name, brand,
    seat_height_cm, weight_kg, engine_cc,
    riding_style, suitability_score
  },
  body_analysis: {
    inseam_cm, torso_length_cm, arm_reach_cm,
    posture_type, confidence
  },
  recommendation_reason: string,
  generated_image_url: string,
  suitability_details: {
    seat_height, weight, ergonomics, overall
  }
}
```

#### GET /health
Check if backend API is running.

## Styling

### Color Scheme
- **Primary**: #ff6b35 (Orange)
- **Secondary**: #ffa500 (Amber)
- **Background**: #f9f9f9 (Light gray)
- **Text**: #333 (Dark gray)
- **Error**: #d32f2f (Red)

### Responsive Breakpoints
- Mobile: < 480px
- Tablet: 480px - 768px
- Desktop: > 768px

## Environment Variables

Optional `.env` file in frontend directory:

```env
# API base URL (default: http://localhost:8000)
REACT_APP_API_URL=http://localhost:8000

# Enable debug logging
REACT_APP_DEBUG=false
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- **Bundle Size**: ~150KB (gzipped)
- **Load Time**: < 2 seconds
- **Image Processing**: Real-time preview
- **API Response**: 35-65 seconds (with image generation)

## Troubleshooting

### API Connection Error
If you see "Backend API is not available":
1. Make sure backend is running: `python app.py`
2. Check backend is on http://localhost:8000
3. Verify CORS is configured in backend config.py

### Image Upload Issues
- Maximum file size: 10MB
- Supported formats: JPEG, PNG, WebP, GIF
- Must be full-body photo for accurate analysis

### No Results
- Ensure valid height (1-250 cm) and weight (1-300 kg)
- Check browser console for error messages
- Verify backend database has motorcycle data

## Development Notes

### Adding New Features
1. Create new component in `src/components/`
2. Import in `App.js`
3. Add styling in separate `.css` file
4. Update API calls in `api.js` if needed

### Testing with Mock Data
To test without backend:

```javascript
// In App.js
const mockRecommendation = {
  bike: { name: "Honda CB300F", ... },
  body_analysis: { inseam_cm: 81.4, ... },
  // ... full mock response
};

// In RecommendationForm.js handleSubmit:
setTimeout(() => {
  onRecommendationReceived(mockRecommendation);
}, 2000);
```

### Debugging
- Open browser DevTools (F12)
- Check Network tab for API calls
- Check Console for JavaScript errors
- Use React DevTools extension for component state

## Future Enhancements

1. **User Authentication**: Save recommendations to profile
2. **Motorcycle Comparison**: Compare multiple bikes side-by-side
3. **Dealer Locator**: Find nearby dealers for recommended bikes
4. **Reviews & Ratings**: Community feedback on bikes
5. **Test Drive Booking**: Schedule test rides
6. **Multiple Languages**: i18n support
7. **Progressive Web App**: Offline support
8. **Mobile App**: Native iOS/Android versions
