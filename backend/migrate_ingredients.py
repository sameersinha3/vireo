#!/usr/bin/env python3
"""
Migration script to move from JSON watchlist to Firestore database
Run this once to migrate your existing data
"""

import asyncio
import json
import os
from backend.utils.ingredient_service import IngredientService

async def main():
    print("🚀 Starting ingredient migration...")
    
    try:
        # Initialize service
        service = IngredientService()
        
        # Load existing JSON data
        file_path = os.path.join(os.path.dirname(__file__), "ingredient_watchlist.json")
        with open(file_path) as f:
            json_data = json.load(f)
        
        print(f"📄 Loaded {len(json_data)} categories from JSON")
        
        # Migrate data
        await service.migrate_from_json(json_data)
        
        print("✅ Migration completed successfully!")
        print("\n📊 Summary:")
        
        # Show what was migrated
        categories = await service.get_all_categories()
        ingredients = await service.get_all_ingredients()
        
        print(f"   - {len(categories)} categories created")
        print(f"   - {len(ingredients)} ingredients created")
        
        print("\n🎯 Next steps:")
        print("   1. Test the /scan endpoint to ensure it works")
        print("   2. Use /admin endpoints to manage ingredients")
        print("   3. Add new ingredients via the API")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
