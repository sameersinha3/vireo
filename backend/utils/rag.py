import requests
import google.generativeai as genai
import os

from xml.etree import ElementTree

def retrieve_pubmed_studies(ingredient: str, limit=3) -> list[dict]:
    # Step 1: Search for PubMed IDs
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": ingredient,
        "retmode": "json",
        "retmax": limit,
    }
    search_response = requests.get(search_url, params=search_params)
    id_list = search_response.json().get("esearchresult", {}).get("idlist", [])

    if not id_list:
        return []

    # Step 2: Fetch abstracts for each PubMed ID
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml",
    }
    fetch_response = requests.get(fetch_url, params=fetch_params)
    root = ElementTree.fromstring(fetch_response.content)

    results = []
    for article in root.findall(".//PubmedArticle"):
        title_el = article.find(".//ArticleTitle")
        abstract_el = article.find(".//Abstract/AbstractText")
        title = title_el.text if title_el is not None else "No title"
        abstract = abstract_el.text if abstract_el is not None else "No abstract"
        results.append({"title": title, "abstract": abstract})

    return results



def retrieve_studies(ingredient: str, limit=3) -> list[str]:
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={ingredient}&limit={limit}&fields=title,abstract"
    response = requests.get(url)
    papers = response.json().get("data", [])
    return papers 

def rag_analysis(ingredient):
    papers = retrieve_pubmed_studies(ingredient)

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("models/gemini-2.0-flash")
    
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
    # print("Successfully Prompted LLM") IDK WHY ITS PROMPTING BUT LLM WONT ACCEPT
    response = model.generate_content(prompt)
    return response.text
