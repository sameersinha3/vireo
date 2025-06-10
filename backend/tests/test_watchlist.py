from itertools import chain
import json


with open("../ingredient_watchlist.json") as f:
    watchlist = json.load(f)
    flattened_watchlist = set(
        i.lower() for i in chain.from_iterable(watchlist.values())
    )

