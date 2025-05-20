from itertools import chain
import json


with open("../ingredient_watchlist.json") as f:
    watchlist = json.load(f)
    flattened_watchlist = set(
        i.lower() for i in chain.from_iterable(watchlist.values())
    )

if __name__ == '__main__':
    raw_ingredients = "carbonated water, caramel color, phosphoric acid, aspartame, potassium benzoate, natural flavors, potassium citrate, acesulfame potassium, caffeine"
    ingredients = raw_ingredients.split(',')
    summaries = {}
    for ingredient in ingredients:
        name = ingredient.lower().strip()
        if name not in flattened_watchlist:
            continue
        summary = "example summary"
        summaries[ingredient] = summary
    if not summaries.keys():
        summaries = {"Note": "This product has no ingredients that were flagged by our watchlist."}
    print(summaries)
