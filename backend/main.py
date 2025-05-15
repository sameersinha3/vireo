from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

# Initialize Firebase
app = FastAPI()
credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

try:
    cred = credentials.Certificate(credentials_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase Admin SDK initialized successfully!")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    db = None

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
    raw_ingredients_text: Optional[str]
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

@app.post("/scan", response_model=Product)
async def scan_barcode(scan: ScanRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Firebase not initialized")
    else:
        print("Firebase Initialized")

    barcode = scan.barcode
    product_ref = db.collection("products").document(barcode)
    product_doc = product_ref.get()

    if product_doc.exists:
        return Product(**product_doc.to_dict())

    # Fetch from OpenFoodFacts
    OFF_URL = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    res = requests.get(OFF_URL)
    print(res)

    if res.status_code != 200 or res.json().get("status") == 0:
        raise HTTPException(status_code=404, detail="Product not found in OpenFoodFacts")

    off_data = res.json()["product"]

    product_data = {
        "barcode": barcode,
        "name": off_data.get("product_name"),
        "brand": off_data.get("brands"),
        "packaging_material": off_data.get("packaging"),
        "packaging_recyclable": off_data.get("packaging_recycling") == "yes",
        "nutriscore": off_data.get("nutriscore_grade"),
        "eco_score_level": off_data.get("environment_impact_level_tags"),
        "raw_ingredients_text": off_data.get("ingredients_text"),
        "ingredients": off_data.get("ingredients", []),
        "image_url": off_data.get("image_url")
    }

    # Store in Firestore
    product_ref.set(product_data)

    return Product(**product_data)