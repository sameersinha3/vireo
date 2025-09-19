"""
Scalable Ingredient Management Service
Handles ingredient categories, flags, and research data
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from backend.firebase_init import db
import logging

logger = logging.getLogger(__name__)

@dataclass
class IngredientCategory:
    """Represents an ingredient category (e.g., 'artificial sweeteners', 'preservatives')"""
    id: str
    name: str
    description: str
    severity_level: str  # 'low', 'moderate', 'high', 'critical'
    is_active: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class Ingredient:
    """Represents a single ingredient with metadata"""
    id: str
    name: str
    aliases: List[str]  # Alternative names, spellings
    category_id: str
    severity_level: str  # Can override category severity
    health_concerns: List[str]  # List of health concerns
    environmental_impact: Optional[str]
    research_summary: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class IngredientFlag:
    """Represents a flagged ingredient in a product scan"""
    ingredient_name: str
    category: str
    severity: str
    health_concerns: List[str]
    research_summary: str

class IngredientService:
    """Service for managing ingredients and categories"""
    
    def __init__(self):
        self.db = db
        if not self.db:
            raise Exception("Firestore not initialized")
    
    # Category Management
    async def create_category(self, category: IngredientCategory) -> str:
        """Create a new ingredient category"""
        try:
            doc_ref = self.db.collection("ingredient_categories").document(category.id)
            doc_ref.set(asdict(category))
            logger.info(f"Created category: {category.name}")
            return category.id
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            raise
    
    async def get_category(self, category_id: str) -> Optional[IngredientCategory]:
        """Get a category by ID"""
        try:
            doc = self.db.collection("ingredient_categories").document(category_id).get()
            if doc.exists:
                data = doc.to_dict()
                return IngredientCategory(**data)
            return None
        except Exception as e:
            logger.error(f"Error getting category: {e}")
            raise
    
    async def get_all_categories(self, active_only: bool = True) -> List[IngredientCategory]:
        """Get all categories"""
        try:
            query = self.db.collection("ingredient_categories")
            if active_only:
                query = query.where("is_active", "==", True)
            
            docs = query.stream()
            categories = []
            for doc in docs:
                data = doc.to_dict()
                categories.append(IngredientCategory(**data))
            return categories
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            raise
    
    # Ingredient Management
    async def create_ingredient(self, ingredient: Ingredient) -> str:
        """Create a new ingredient"""
        try:
            doc_ref = self.db.collection("ingredients").document(ingredient.id)
            doc_ref.set(asdict(ingredient))
            logger.info(f"Created ingredient: {ingredient.name}")
            return ingredient.id
        except Exception as e:
            logger.error(f"Error creating ingredient: {e}")
            raise
    
    async def get_ingredient(self, ingredient_id: str) -> Optional[Ingredient]:
        """Get an ingredient by ID"""
        try:
            doc = self.db.collection("ingredients").document(ingredient_id).get()
            if doc.exists:
                data = doc.to_dict()
                return Ingredient(**data)
            return None
        except Exception as e:
            logger.error(f"Error getting ingredient: {e}")
            raise
    
    async def search_ingredient_by_name(self, name: str) -> Optional[Ingredient]:
        """Search for ingredient by name or alias"""
        try:
            name_lower = name.lower().strip()
            
            # Search by exact name
            docs = self.db.collection("ingredients").where("name", "==", name_lower).limit(1).stream()
            for doc in docs:
                data = doc.to_dict()
                return Ingredient(**data)
            
            # Search by aliases
            docs = self.db.collection("ingredients").stream()
            for doc in docs:
                data = doc.to_dict()
                ingredient = Ingredient(**data)
                if name_lower in [alias.lower() for alias in ingredient.aliases]:
                    return ingredient
            
            return None
        except Exception as e:
            logger.error(f"Error searching ingredient: {e}")
            raise
    
    async def get_all_ingredients(self, active_only: bool = True) -> List[Ingredient]:
        """Get all ingredients"""
        try:
            query = self.db.collection("ingredients")
            if active_only:
                query = query.where("is_active", "==", True)
            
            docs = query.stream()
            ingredients = []
            for doc in docs:
                data = doc.to_dict()
                ingredients.append(Ingredient(**data))
            return ingredients
        except Exception as e:
            logger.error(f"Error getting ingredients: {e}")
            raise
    
    # Scanning Logic
    async def get_active_ingredient_names(self) -> Set[str]:
        """Get all active ingredient names and aliases for fast scanning"""
        try:
            ingredients = await self.get_all_ingredients(active_only=True)
            names = set()
            
            for ingredient in ingredients:
                names.add(ingredient.name.lower())
                names.update([alias.lower() for alias in ingredient.aliases])
            
            logger.info(f"Loaded {len(names)} ingredient names for scanning")
            return names
        except Exception as e:
            logger.error(f"Error getting ingredient names: {e}")
            raise
    
    async def flag_ingredients_in_text(self, ingredients_text: str) -> List[IngredientFlag]:
        """Flag ingredients found in product ingredients text"""
        try:
            if not ingredients_text:
                return []
            
            # Get all active ingredient names
            active_names = await self.get_active_ingredient_names()
            
            # Parse ingredients (split by comma and clean)
            ingredient_list = [ing.strip() for ing in ingredients_text.split(',')]
            
            flagged = []
            for ingredient_text in ingredient_list:
                name = ingredient_text.lower().strip()
                
                # Check if this ingredient is in our watchlist
                if name in active_names:
                    # Find the full ingredient record
                    ingredient = await self.search_ingredient_by_name(name)
                    if ingredient:
                        # Get category info
                        category = await self.get_category(ingredient.category_id)
                        
                        flagged.append(IngredientFlag(
                            ingredient_name=ingredient_text.strip(),
                            category=category.name if category else "Unknown",
                            severity=ingredient.severity_level or (category.severity_level if category else "moderate"),
                            health_concerns=ingredient.health_concerns or [],
                            research_summary=ingredient.research_summary or ""
                        ))
                else:
                    # Check if this ingredient should be flagged based on known patterns
                    should_flag = await self._should_flag_unknown_ingredient(name)
                    if should_flag:
                        flagged.append(IngredientFlag(
                            ingredient_name=ingredient_text.strip(),
                            category="Auto-Flagged",
                            severity="moderate",
                            health_concerns=[],
                            research_summary=""  # Will be generated when user clicks
                        ))
            
            return flagged
        except Exception as e:
            logger.error(f"Error flagging ingredients: {e}")
            raise
    
    async def _should_flag_unknown_ingredient(self, ingredient_name: str) -> bool:
        """Determine if an unknown ingredient should be flagged for research"""
        # List of patterns that suggest potentially problematic ingredients
        suspicious_patterns = [
            # Chemical-sounding names
            r'.*ate$',  # sulfates, phosphates, etc.
            r'.*ide$',  # chlorides, bromides, etc.
            r'.*ene$',  # benzene, propylene, etc.
            r'.*ol$',   # alcohols, phenols, etc.
            r'.*ium$',  # sodium, potassium, etc.
            
            # Common preservatives and additives
            r'.*benzoate.*',
            r'.*sorbate.*',
            r'.*nitrate.*',
            r'.*nitrite.*',
            r'.*sulfite.*',
            r'.*phosphate.*',
            r'.*propionate.*',
            
            # Artificial colors and flavors
            r'.*red\s*\d+.*',
            r'.*yellow\s*\d+.*',
            r'.*blue\s*\d+.*',
            r'.*green\s*\d+.*',
            r'.*artificial.*',
            r'.*synthetic.*',
            
            # Emulsifiers and thickeners
            r'.*gum.*',
            r'.*carrageenan.*',
            r'.*polysorbate.*',
            r'.*lecithin.*',
            r'.*mono.*diglyceride.*',
            
            # Sweeteners
            r'.*aspartame.*',
            r'.*sucralose.*',
            r'.*saccharin.*',
            r'.*stevia.*',
            r'.*xylitol.*',
            r'.*sorbitol.*',
            
            # MSG and flavor enhancers
            r'.*glutamate.*',
            r'.*inosinate.*',
            r'.*guanylate.*',
        ]
        
        import re
        for pattern in suspicious_patterns:
            if re.match(pattern, ingredient_name, re.IGNORECASE):
                return True
        
        return False
    
    # Migration from old system
    async def migrate_from_json(self, json_data: Dict) -> None:
        """Migrate ingredients from the old JSON format"""
        try:
            logger.info("Starting migration from JSON watchlist...")
            
            for category_name, ingredient_list in json_data.items():
                # Create category
                category_id = category_name.lower().replace(" ", "_")
                category = IngredientCategory(
                    id=category_id,
                    name=category_name,
                    description=f"Migrated from JSON watchlist: {category_name}",
                    severity_level=self._get_default_severity(category_name),
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                await self.create_category(category)
                
                # Create ingredients
                for ingredient_name in ingredient_list:
                    ingredient_id = f"{category_id}_{ingredient_name.lower().replace(' ', '_')}"
                    ingredient = Ingredient(
                        id=ingredient_id,
                        name=ingredient_name.lower(),
                        aliases=[ingredient_name],  # Original name as alias
                        category_id=category_id,
                        severity_level=category.severity_level,
                        health_concerns=[],
                        environmental_impact=None,
                        research_summary=None,
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    await self.create_ingredient(ingredient)
            
            logger.info("Migration completed successfully!")
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            raise
    
    def _get_default_severity(self, category_name: str) -> str:
        """Map category names to default severity levels"""
        severity_map = {
            "artificial sweeteners": "moderate",
            "preservatives": "moderate", 
            "food dyes": "moderate",
            "emulsifiers and thickeners": "low",
            "flavor enhancers": "low",
            "stimulants": "moderate",
            "controversial or emerging": "high",
            "sugar alcohols": "low"
        }
        return severity_map.get(category_name.lower(), "moderate")
