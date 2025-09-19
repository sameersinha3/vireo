import axios from 'axios';

// API Configuration
export const API_BASE_URL = "http://192.168.10.107:8000";

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Endpoints
export const API_ENDPOINTS = {
  SCAN: '/scan',
  INGREDIENT_BRIEF: '/ingredient-brief',
  PRODUCT: '/products',
};
