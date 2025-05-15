import json
import re
from pathlib import Path

class IngredientAnalyzer:
    def __init__(self, lookup_path: str = None):
        if lookup_path is None:
            lookup_path = Path(__file__).parent / "../ingredient_lookup.json"
        with open(lookup_path, "r") as f:
            self.lookup = json.load(f)

    def analyze(self, ingredients: list[str]) -> list[dict]:
        matches = []

        for raw in ingredients:
            normalized = self.normalize_ingredient(raw)

            for keyword in self.lookup:
                if keyword in normalized:
                    matches.append({
                        "ingredient": raw,
                        "match": keyword,
                        **self.lookup[keyword]
                    })
        return matches

    def normalize_ingredient(self, text: str) -> str:
        # Normalize lowercase and strip punctuation
        return re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()
