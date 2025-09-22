import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv
from xml.etree import ElementTree

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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

    # Step 2: Fetch abstracts
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

def rag_analysis(ingredient: str):
    papers = retrieve_pubmed_studies(ingredient)

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

    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(prompt)

    return response.text

async def rag_analysis_with_progress(ingredient: str, progress_dict: dict):
    """RAG analysis with progress updates"""
    import asyncio
    
    # Update progress: searching research
    progress_dict[ingredient] = {
        "status": "searching_research",
        "message": "Searching PubMed for research..."
    }
    
    # Run PubMed search in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    papers = await loop.run_in_executor(None, retrieve_pubmed_studies, ingredient)

    if not papers:
        return f"No relevant research found for {ingredient}."

    # Update progress: generating summary
    progress_dict[ingredient] = {
        "status": "generating_summary", 
        "message": "Generating research summary..."
    }

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

    # Run Gemini generation in thread pool
    def generate_content():
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    
    summary = await loop.run_in_executor(None, generate_content)
    return summary
