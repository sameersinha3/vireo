# vireo

Vireo is a website AND app to educate the world on our food choices. Unlike an app like MyFitnessPal, which focuses on overall caloric intake, micro- and macro- nutrient consumption, and hitting our overall nutrition goals, Vireo aims to alert users of the acutal ingredients and whether or not they are harmful. 


Things Vireo warns you about include:
### Chemical endings
Anything ending in -ate, -ide, -ene, -ol, or -ium
### Preservatives
Anything with benzoate, sorbate, nitrate/nitrite, sulfite, phosphate, propionate
### Artificial Colors
Red 40, Red 3, Yellow 5, etc., or anything with artificial or synthetic
### Emulsifiers
Anything with gum, carrageenan, polysorbate, lecithin, mono- and diglyceride
### Artificial Sweeteners
Aspartame, sucralose, saccharine, stevia, etc.
### Flavor Enhancers
Glutamate (MSG), Inosinate, guanylate

What this means is, when you scan a product, the system flags all ingredients matching these patterns and anything I've manually added, and generates a research brief so you can know if you really do need to avoid things like aspartame. Just because it sounds artificial doesn't mean it's bad!

## Frontend

To run the frontend navigate to web-frontend and run 

```bash
npm start
```

### Web UI

### Mobile App (Under development)

Vireo is a mobile app written in React Native.

To run the frontend, run
```bash
cd frontend/VireoApp
npx expo start
```


## Backend

Vireo's backend is written in Python with FastAPI, connected to our Google Firestore database. Upon receiving a barcode from the frontend, we query an open source API to retrieve the ingredients, identify potentially problematic ingredients, query PubMed for recent studies, and use Google Gemini to generate an overall safety analysis of each ingredient, so you can stay up to date with the most up to date knowledge. If an ingredient has been scanned recently, it will use the blurb in our database rather than generating a new summary.

To run the backend, run

```bash
source vireo/bin/activate
PYTHONPATH=$(pwd) uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Please note that we are not doctors, and if you have any sort of medical condition, you should consult your doctor. This is not medical advice; this is simply a tool to learn about various ingredients.