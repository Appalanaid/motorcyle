/**
 * Recommendation Result Display Component
 * Shows the recommended motorcycle and generated image
 */

import React from 'react';
import './RecommendationResult.css';

const RecommendationResult = ({ recommendation, onNewRecommendation }) => {
  if (!recommendation) return null;

  const { bike, body_analysis, recommendation_reason, generated_image_url, suitability_details } = recommendation;

  return (
    <div className="result-container">
      <h2>Your Motorcycle Recommendation</h2>

      {/* Main Recommendation Card */}
      <div className="bike-card">
        <div className="bike-info">
          <h3>{bike.brand} {bike.name}</h3>
          
          <div className="specs-grid">
            <div className="spec">
              <label>Seat Height</label>
              <value>{bike.seat_height_cm} cm</value>
            </div>
            <div className="spec">
              <label>Weight</label>
              <value>{bike.weight_kg} kg</value>
            </div>
            <div className="spec">
              <label>Engine</label>
              <value>{bike.engine_cc} cc</value>
            </div>
            <div className="spec">
              <label>Style</label>
              <value>{bike.riding_style}</value>
            </div>
          </div>

          {/* Suitability Scores */}
          <div className="scores-section">
            <h4>Suitability Scores</h4>
            <div className="score-bar">
              <label>Overall Match</label>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${suitability_details.overall}%` }}
                >
                  {suitability_details.overall.toFixed(0)}%
                </div>
              </div>
            </div>
            
            <div className="score-details">
              <div className="score-item">
                <span>Seat Height</span>
                <span className="score-value">{suitability_details.seat_height.toFixed(0)}/100</span>
              </div>
              <div className="score-item">
                <span>Weight Match</span>
                <span className="score-value">{suitability_details.weight.toFixed(0)}/100</span>
              </div>
              <div className="score-item">
                <span>Ergonomics</span>
                <span className="score-value">{suitability_details.ergonomics.toFixed(0)}/100</span>
              </div>
            </div>
          </div>

          {/* Recommendation Reason */}
          <div className="reason-section">
            <h4>Why This Bike?</h4>
            <p>{recommendation_reason}</p>
          </div>

          {/* Body Analysis */}
          <div className="analysis-section">
            <h4>Your Body Analysis</h4>
            <div className="analysis-grid">
              <div className="analysis-item">
                <label>Estimated Inseam</label>
                <value>{body_analysis.inseam_cm.toFixed(1)} cm</value>
              </div>
              <div className="analysis-item">
                <label>Torso Length</label>
                <value>{body_analysis.torso_length_cm.toFixed(1)} cm</value>
              </div>
              <div className="analysis-item">
                <label>Arm Reach</label>
                <value>{body_analysis.arm_reach_cm.toFixed(1)} cm</value>
              </div>
              <div className="analysis-item">
                <label>Posture Type</label>
                <value>{body_analysis.posture_type}</value>
              </div>
              <div className="analysis-item">
                <label>Analysis Confidence</label>
                <value>{(body_analysis.confidence * 100).toFixed(0)}%</value>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Generated AI Image */}
      {generated_image_url && (
        <div className="generated-image-section">
          <h3>Your AI Image</h3>
          <img src={generated_image_url} alt="You with recommended bike" />
          <p className="image-note">
            AI-generated image showing you with the {bike.brand} {bike.name}
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="action-buttons">
        <button className="new-recommendation-btn" onClick={onNewRecommendation}>
          Get Another Recommendation
        </button>
        <a href="#compare" className="compare-btn">
          Compare Similar Bikes
        </a>
      </div>
    </div>
  );
};

export default RecommendationResult;
