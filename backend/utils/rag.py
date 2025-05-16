import requests
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

from xml.etree import ElementTree


load_dotenv()

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

    client = InferenceClient(
        provider="fireworks-ai",
        api_key = os.getenv("HUGGINGFACE_API_KEY")
    )
    
    if not papers:
        return f"No relevant research found for {ingredient}."

    context = "\n\n".join(
        f"{paper['title']}:\n{paper.get('abstract', 'No abstract available.')}"
        for paper in papers
    )

    
    prompt = f"""
You are a food science expert analyzing current research.

Based on the abstracts below, give advice to a potential consumer about the health risks of the food ingredient '{ingredient}'? 

If there is public concern but evidence suggests safety, say "despite concerns, research suggests...". Be honest about uncertainty. Use simple language.

Research abstracts:
{context}
"""
    #print("Successfully Prompted LLM")

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    completion = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct", 
        messages=messages, 
        temperature=0.5,
        max_tokens=500,
        top_p=0.7,
    )

    #response = model.generate_content(prompt)
    return completion.choices[0].message.content
