from firebase_admin import firestore

db = firestore.client()

def get_summary_from_firestore(ingredient):
    doc_ref = db.collection("ingredient_summaries").document(ingredient.lower())
    doc = doc_ref.get()
    return doc.to_dict()["summary"] if doc.exists else None

def store_summary_in_firestore(ingredient, summary):
    doc_ref = db.collection("ingredient_summaries").document(ingredient.lower())
    doc_ref.set({"summary": summary})