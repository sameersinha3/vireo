# vireo

Vireo is an app to educate the world on our food choices. Unlike an app like MyFitnessPal, which focuses on overall caloric intake, micro- and macro- nutrient consumption, and hitting our overall nutrition goals, Vireo aims to alert users of the acutal ingredients and whether or not they are harmful. For example, while many Americans consider aspartame to be unsafe, current research suggests it's safe in moderation. On the other hand, very few Americans actively avoid things like "sodium benzoate," simply because we've never heard of it.

Vireo aims to make this information accessible to all, by allowing you to scan the barcode, and you will get a breakdown of the ingredients; which ones are good, which ones are bad, and whether or not you need to "fear" a certain ingredient. Upon scanning, we hope to link actual studies and evidence to justify whether certain ingredients are safe, risky, or need more research!

## Frontend

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