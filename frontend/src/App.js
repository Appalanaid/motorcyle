/**
 * Main App Component
 * Orchestrates the recommendation form and result display
 */

import React, { useState, useEffect } from 'react';
import RecommendationForm from './components/RecommendationForm';
import RecommendationResult from './components/RecommendationResult';
import LoadingSpinner from './components/LoadingSpinner';
import './App.css';

function App() {
  const [recommendation, setRecommendation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiReady, setApiReady] = useState(false);

  // Check API health on component mount
  useEffect(() => {
    const checkAPI = async () => {
      try {
        const response = await fetch('http://localhost:8000/health', {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        if (response.ok) {
          setApiReady(true);
        }
      } catch (error) {
        console.error('API not available:', error);
        setApiReady(false);
      }
    };

    checkAPI();
  }, []);

  const handleRecommendationReceived = (result) => {
    setRecommendation(result);
  };

  const handleNewRecommendation = () => {
    setRecommendation(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🏍️ Motorcycle Recommendation</h1>
          <p>AI-powered motorcycle matching based on your body & preferences</p>
        </div>
      </header>

      <main className="app-main">
        {!apiReady && (
          <div className="api-error">
            <p>⚠️ Backend API is not available. Make sure the server is running on port 8000.</p>
            <code>python app.py</code>
          </div>
        )}

        {isLoading && <LoadingSpinner message="Analyzing image and generating recommendation..." />}

        {!recommendation ? (
          <RecommendationForm 
            onRecommendationReceived={handleRecommendationReceived}
            onLoading={setIsLoading}
          />
        ) : (
          <RecommendationResult 
            recommendation={recommendation}
            onNewRecommendation={handleNewRecommendation}
          />
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 Motorcycle Recommendation System | Powered by AI</p>
      </footer>
    </div>
  );
}

export default App;
