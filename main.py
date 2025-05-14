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