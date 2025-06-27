
// Environment configuration
const isDevelopment = import.meta.env.DEV;

export const API_BASE_URL = isDevelopment 
  ? 'http://127.0.0.1:8001/api'
  : import.meta.env.VITE_API_BASE_URL || 'https://your-production-api.com/api';

export const ENDPOINTS = {
  ITEMS: `${API_BASE_URL}/items/`,
  QUIZZES: `${API_BASE_URL}/quizzes`,
  PRODUCTS: `${API_BASE_URL}/products`,
} as const;
