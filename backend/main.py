from fastapi import FastAPI, HTTPException
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

file_path = os.path.join(os.path.dirname(__file__), "ingredient_watchlist.json")

with open(file_path) as f:
    watchlist = json.load(f)
    flattened_watchlist = set(
        i.lower() for i in chain.from_iterable(watchlist.values())
    )

load_dotenv()

app = FastAPI()

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
    ingredients = raw_ingredients.split(',')
    summaries = {}
    for ingredient in ingredients:
        name = ingredient.lower().strip()
        if name not in flattened_watchlist:
            continue
        
        summary = get_summary_from_firestore(name)
        summary = None
        if not summary:
            summary = "debug" #rag_analysis(name)
            store_summary_in_firestore(name, summary)
        summaries[ingredient] = summary
    
    if not summaries.keys():
        summaries = {"Note": "This product has no ingredients that were flagged by our watchlist."}

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

    return summaries