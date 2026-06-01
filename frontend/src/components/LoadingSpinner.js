/**
 * Loading Spinner Component
 * Displays during API requests
 */

import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ message = 'Processing...' }) => {
  return (
    <div className="loading-overlay">
      <div className="loading-container">
        <div className="spinner"></div>
        <p>{message}</p>
      </div>
    </div>
  );
};

export default LoadingSpinner;
