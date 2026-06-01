/**
 * API URL Configuration
 * Centralized URL management for easy deployment switching
 * 
 * Usage:
 * - Development: npm start (uses REACT_APP_API_URL or default localhost:8000)
 * - AWS Deployment: Set REACT_APP_API_URL environment variable
 * 
 * Examples:
 * - Local: http://localhost:8000
 * - AWS EC2: http://ec2-instance-ip:8000
 * - AWS ALB: http://my-alb-dns.us-east-1.elb.amazonaws.com
 * - Custom Domain: https://api.myapp.com
 */

// Get API URL from environment variable or use default
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// API Endpoints
export const API_URLS = {
  // Base URL
  BASE: API_BASE_URL,

  // Health check endpoint
  HEALTH: `${API_BASE_URL}/health`,

  // Recommendation endpoints
  RECOMMEND: `${API_BASE_URL}/api/recommend`,
  MOTORCYCLES: `${API_BASE_URL}/api/motorcycles`,

  // API Documentation (Swagger UI)
  DOCS: `${API_BASE_URL}/docs`,
  REDOC: `${API_BASE_URL}/redoc`,
};

/**
 * Get full API URL for a given endpoint
 * @param {string} endpoint - Endpoint path (e.g., '/api/recommend')
 * @returns {string} Full API URL
 */
export const getApiUrl = (endpoint) => {
  return `${API_BASE_URL}${endpoint}`;
};

/**
 * Get current API base URL
 * Useful for debugging and logging
 * @returns {string} Current API base URL
 */
export const getBaseUrl = () => {
  return API_BASE_URL;
};

export default API_URLS;
