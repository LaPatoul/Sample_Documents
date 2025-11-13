/**
 * API Configuration
 * Automatically detects if user is accessing locally or externally
 * and uses the appropriate backend API endpoint
 */

const getApiBase = () => {
  const hostname = window.location.hostname;

  // If accessing via public IP or domain, use public API endpoint
  if (hostname === '5.49.237.223') {
    return 'http://5.49.237.223:45000/api';
  }

  // If accessing via local IP, use local API endpoint
  if (hostname === '192.168.1.46') {
    return 'http://192.168.1.46:5000/api';
  }

  // Default to localhost for development
  return 'http://localhost:5000/api';
};

export const API_BASE = getApiBase();
