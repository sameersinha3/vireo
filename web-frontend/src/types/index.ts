export interface Ingredient {
  id?: string;
  text?: string;
  vegetarian?: string;
  vegan?: string;
  from_palm_oil?: string;
}

export interface Product {
  barcode: string;
  name?: string;
  brand?: string;
  packaging_recyclable?: boolean;
  packaging_material?: string;
  nutriscore?: string;
  eco_score_level?: string[];
  ingredients?: Ingredient[];
  ingredients_text?: string;
  image_url?: string;
}

export interface ScanResponse {
  product: Product;
  flagged_ingredients: string[];
  flagged_ingredients_metadata?: {
    [ingredientName: string]: {
      category: string;
      severity: string;
      health_concerns: string[];
      has_research_summary: boolean;
    };
  };
}

export interface IngredientBriefRequest {
  ingredient: string;
}

export interface IngredientBriefResponse {
  ingredient: string;
  summary: string;
}
