import requests
import google.generativeai as genai
import os

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")

def retrieve_studies(ingredient: str, limit=3) -> list[str]:
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={ingredient}&limit={limit}&fields=title,abstract"
    response = requests.get(url)
    papers = response.json().get("data", [])
    return papers  # return full paper dicts (title + abstract)

def rag_analysis(ingredient):
    papers = retrieve_studies(ingredient)
    
    if not papers:
        return f"No relevant research found for {ingredient}."

    context = "\n\n".join(
        f"{paper['title']}:\n{paper.get('abstract', 'No abstract available.')}"
        for paper in papers
    )

    prompt = f"""
You are a food science expert analyzing current research.

Based on the abstracts below, what does current research suggest about the health risks of the food ingredient '{ingredient}'?

If there is public concern but evidence suggests safety, say "despite concerns, research suggests...". Be honest about uncertainty. Use simple language.

Research abstracts:
{context}
"""

    response = model.generate_content(prompt)
    return response.text
