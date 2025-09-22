// API Configuration
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000";


export const API_ENDPOINTS = {
  SCAN: `${API_BASE_URL}/scan`,
  INGREDIENT_BRIEF: `${API_BASE_URL}/ingredient-brief`,
  INGREDIENT_BRIEF_PROGRESS: `${API_BASE_URL}/ingredient-brief-progress`,
};
