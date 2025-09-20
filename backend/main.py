from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import json
import requests
from itertools import chain
import os
from backend.firebase_init import db


from backend.utils.rag import rag_analysis
from backend.utils.firestore import get_summary_from_firestore, store_summary_in_firestore
from backend.utils.ingredient_service import IngredientService, IngredientCategory, Ingredient
from dataclasses import asdict

# Initialize ingredient service
ingredient_service = IngredientService()

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Models
class Ingredient(BaseModel):
    id: Optional[str] = None
    text: Optional[str] = None
    vegetarian: Optional[str] = None
    vegan: Optional[str] = None
    from_palm_oil: Optional[str] = None

class Product(BaseModel):
    barcode: str
    name: Optional[str]
    brand: Optional[str]
    packaging_recyclable: Optional[bool]
    packaging_material: Optional[str]
    nutriscore: Optional[str]
    eco_score_level: Optional[List[str]]
    ingredients: Optional[List[Ingredient]]
    ingredients_text: Optional[str]
    image_url: Optional[str]

class ScanRequest(BaseModel):
    barcode: str

class ProductSearchRequest(BaseModel):
    query: str
    limit: int = 10

class IngredientBriefRequest(BaseModel):
    ingredient: str

class IngredientCreateRequest(BaseModel):
    name: str
    aliases: List[str] = []
    category_id: str
    severity_level: str = "moderate"
    health_concerns: List[str] = []
    environmental_impact: Optional[str] = None
    research_summary: Optional[str] = None

class CategoryCreateRequest(BaseModel):
    name: str
    description: str
    severity_level: str = "moderate"

# Routes
@app.get("/")
async def root():
    return {"message": "Hello Vireo Backend!"}

@app.get("/products/{barcode}", response_model=Product)
async def get_product(barcode: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Firebase not initialized")

    product_ref = db.collection("products").document(barcode)
    product_doc = product_ref.get()

    if product_doc.exists:
        return Product(**product_doc.to_dict())
    else:
        raise HTTPException(status_code=404, detail=f"Product with barcode '{barcode}' not found")

@app.post("/scan")
async def scan_barcode(scan: ScanRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Firebase not initialized")
    else:
        print("Firebase Initialized")

    barcode = scan.barcode
    product_ref = db.collection("products").document(barcode)
    product_doc = product_ref.get()
    

    #if product_doc.exists:
    #    return Product(**product_doc.to_dict())

    # Fetch from OpenFoodFacts
    OFF_URL = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    res = requests.get(OFF_URL)

    if res.status_code != 200 or res.json().get("status") == 0:
        raise HTTPException(status_code=404, detail="Product not found in OpenFoodFacts")

    off_data = res.json()["product"]

    raw_ingredients = off_data.get("ingredients_text", "")
    
    # Use the new ingredient service to flag ingredients
    flagged_ingredient_objects = await ingredient_service.flag_ingredients_in_text(raw_ingredients)
    flagged_ingredients = [flag.ingredient_name for flag in flagged_ingredient_objects]
    
    # Store flagged ingredient metadata for research brief generation
    flagged_ingredients_metadata = {
        flag.ingredient_name: {
            "category": flag.category,
            "severity": flag.severity,
            "health_concerns": flag.health_concerns,
            "has_research_summary": bool(flag.research_summary)
        } for flag in flagged_ingredient_objects
    }
    
    product_data = {
        "barcode": barcode,
        "name": off_data.get("product_name"),
        "brand": off_data.get("brands"),
        "packaging_material": off_data.get("packaging"),
        "packaging_recyclable": off_data.get("packaging_recycling") == "yes",
        "nutriscore": off_data.get("nutriscore_grade"),
        "eco_score_level": off_data.get("environment_impact_level_tags"),
        "ingredients_text": off_data.get("ingredients_text"),
        "ingredients": off_data.get("ingredients", []),
        "image_url": off_data.get("image_url")
    }
    # Store in Firestore
    product_ref.set(product_data)

    return {
        "product": product_data,
        "flagged_ingredients": flagged_ingredients,
        "flagged_ingredients_metadata": flagged_ingredients_metadata
    }

@app.post("/search-products")
async def search_products(request: ProductSearchRequest):
    """Search for products by name using OpenFoodFacts API"""
    try:
        # Use OpenFoodFacts search API
        search_url = "https://world.openfoodfacts.org/cgi/search.pl"
        search_params = {
            "search_terms": request.query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": request.limit
        }
        
        response = requests.get(search_url, params=search_params, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to search products")
        
        data = response.json()
        products = data.get("products", [])
        
        # Format the results
        formatted_products = []
        for product in products:
            if product.get("code") and product.get("product_name"):
                formatted_products.append({
                    "barcode": product.get("code"),
                    "name": product.get("product_name"),
                    "brand": product.get("brands"),
                    "image_url": product.get("image_url"),
                    "ingredients_text": product.get("ingredients_text", ""),
                    "nutriscore": product.get("nutriscore_grade")
                })
        
        return {
            "products": formatted_products,
            "total_results": len(formatted_products)
        }
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Search service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/ingredient-brief")
async def get_ingredient_brief(request: IngredientBriefRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Firebase not initialized")
    
    ingredient = request.ingredient.lower().strip()
    
    # Check if we have a stored summary in Firestore
    summary = get_summary_from_firestore(ingredient)
    
    if not summary:
        # Generate new summary using RAG for any flagged ingredient
        print(f"Generating research brief for flagged ingredient: {ingredient}")
        summary = rag_analysis(ingredient)
        store_summary_in_firestore(ingredient, summary)
        
        # Also store it in our ingredient database if it exists
        try:
            existing_ingredient = await ingredient_service.search_ingredient_by_name(ingredient)
            if existing_ingredient and not existing_ingredient.research_summary:
                # Update the ingredient with the generated summary
                existing_ingredient.research_summary = summary
                await ingredient_service.create_ingredient(existing_ingredient)  # This will update it
        except Exception as e:
            print(f"Error updating ingredient research summary: {e}")
    
    return {
        "ingredient": request.ingredient,
        "summary": summary
    }

# Admin endpoints for ingredient management
@app.post("/admin/categories")
async def create_category(request: CategoryCreateRequest):
    """Create a new ingredient category"""
    try:
        from datetime import datetime
        category_id = request.name.lower().replace(" ", "_")
        
        category = IngredientCategory(
            id=category_id,
            name=request.name,
            description=request.description,
            severity_level=request.severity_level,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        category_id = await ingredient_service.create_category(category)
        return {"message": "Category created successfully", "category_id": category_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/categories")
async def get_categories():
    """Get all ingredient categories"""
    try:
        categories = await ingredient_service.get_all_categories()
        return {"categories": [asdict(cat) for cat in categories]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/ingredients")
async def create_ingredient(request: IngredientCreateRequest):
    """Create a new ingredient"""
    try:
        from datetime import datetime
        ingredient_id = f"{request.category_id}_{request.name.lower().replace(' ', '_')}"
        
        ingredient = Ingredient(
            id=ingredient_id,
            name=request.name.lower(),
            aliases=request.aliases,
            category_id=request.category_id,
            severity_level=request.severity_level,
            health_concerns=request.health_concerns,
            environmental_impact=request.environmental_impact,
            research_summary=request.research_summary,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        ingredient_id = await ingredient_service.create_ingredient(ingredient)
        return {"message": "Ingredient created successfully", "ingredient_id": ingredient_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/ingredients")
async def get_ingredients():
    """Get all ingredients"""
    try:
        ingredients = await ingredient_service.get_all_ingredients()
        return {"ingredients": [asdict(ing) for ing in ingredients]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/migrate")
async def migrate_from_json():
    """Migrate ingredients from the old JSON watchlist"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), "ingredient_watchlist.json")
        with open(file_path) as f:
            json_data = json.load(f)
        
        await ingredient_service.migrate_from_json(json_data)
        return {"message": "Migration completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))