/**
 * API configuration and utilities
 * Handles all communication with the backend API
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for image generation
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * Convert image file to base64 string
 * @param {File} file - Image file from file input
 * @returns {Promise<string>} Base64 encoded image (without data URL prefix)
 */
export const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      // Remove the data:image/...;base64, prefix
      const base64String = reader.result.split(',')[1];
      resolve(base64String);
    };
    reader.onerror = error => reject(error);
  });
};

/**
 * Get motorcycle recommendation from backend
 * @param {Object} data - Request data
 * @param {string} data.imageBase64 - Full-body photo as base64
 * @param {number} data.height - Height in cm
 * @param {number} data.weight - Weight in kg
 * @param {string} data.preference - Riding preference (commute/touring/sport)
 * @param {boolean} data.generateImage - Whether to generate AI image
 * @returns {Promise<Object>} Recommendation response
 */
export const getRecommendation = async (data) => {
  try {
    const response = await apiClient.post('/api/recommend', {
      image_base64: data.imageBase64,
      height_cm: data.height,
      weight_kg: data.weight,
      riding_preference: data.preference,
      generate_image: data.generateImage
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Failed to get recommendation');
    }
    throw error;
  }
};

/**
 * Get list of available motorcycles
 * @returns {Promise<Object>} List of motorcycles
 */
export const getMotorcycles = async () => {
  try {
    const response = await apiClient.get('/api/motorcycles');
    return response.data;
  } catch (error) {
    console.error('Error fetching motorcycles:', error);
    throw error;
  }
};

/**
 * Check API health status
 * @returns {Promise<Object>} Health status
 */
export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('API health check failed:', error);
    throw error;
  }
};

export default apiClient;
