from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv
import os

load_dotenv()

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

@app.get("/")
async def root():
    return {"message": "Hello Vireo Backend!"}


from fastapi import FastAPI, HTTPException
from firebase_admin import firestore
from pydantic import BaseModel


class Product(BaseModel):
    barcode: str
    name: str
    brand: str
    packaging_recyclable: bool
    packaging_material: str

@app.get("/products/{barcode}", response_model=Product)
async def get_product(barcode: str):
    """
    Retrieves product data from Firestore based on the barcode.
    """
    if db is None:
        raise HTTPException(status_code=500, detail="Firebase not initialized")

    product_ref = db.collection("products").document(barcode)
    product_doc = product_ref.get()

    if product_doc.exists:
        product_data = product_doc.to_dict()
        return Product(**product_data)
    else:
        raise HTTPException(status_code=404, detail=f"Product with barcode '{barcode}' not found")
    
from fastapi import Request
import requests

class ScanRequest(BaseModel):
    barcode: str

@app.post("/scan")
async def scan_barcode(scan: ScanRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Firebase not initialized")

    barcode = scan.barcode
    product_ref = db.collection("products").document(barcode)
    product_doc = product_ref.get()

    if product_doc.exists:
        return product_doc.to_dict()

    OFF_URL = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    res = requests.get(OFF_URL)

    if res.status_code != 200 or res.json().get("status") == 0:
        raise HTTPException(status_code=404, detail="Product not found in OpenFoodFacts")

    off_data = res.json()["product"]

    name = off_data.get("product_name", "Unknown")
    brand = off_data.get("brands", "Unknown")
    packaging_material = off_data.get("packaging_materials_tags", ["unknown"])[0]
    packaging_recyclable = "recyclable" in off_data.get("packaging_tags", [])

    product_obj = {
        "barcode": barcode,
        "name": name,
        "brand": brand,
        "packaging_material": packaging_material,
        "packaging_recyclable": packaging_recyclable,
    }

    product_ref.set(product_obj)

    return product_obj
