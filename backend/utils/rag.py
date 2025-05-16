import requests
from google import genai

client = genai.Client(api_key="AIzaSyBVqnW7zVsp_LaF8w-A5zcXc4_Y3H56E4Q")

'''
RAG Search: Use Semantic Scholar to retrieve 3 studies on a certain ingredient
'''
def retrieve_studies(ingredient: str, limit=3) -> list[str]:
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={ingredient}&limit={limit}&fields=title,abstract,url"
    response = requests.get(url)
    papers = response.json().get("data", [])
    return [f"{p['title']}: {p.get('abstract', '')}" for p in papers]


def rag_analysis(ingredient):
    papers = retrieve_studies(ingredient) 
    context = "\n\n".join([f"{p['title']}:\n{p['abstract']}" for p in papers])
    
    prompt = f"""
    Based on these abstracts, what does current research suggest about the health risks of {ingredient}? 
    Be honest about uncertainty. Say 'despite concerns, research suggests...' if appropriate.
    
    {context}
    """

    gemini = genai.GenerativeModel("gemini-2.0-flash")
    response = gemini.generate_content(prompt)
    return response.text
