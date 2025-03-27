import requests
import pandas as pd
import typer
import json
from typing import Optional

# PubMed API Base URL
PUBMED_API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

def fetch_pubmed_papers(query: str, email: Optional[str] = None) -> list:
    """
    Fetch research papers from PubMed API based on the search query.
    Returns a list of papers with relevant metadata.
    """
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 20  # Fetch up to 20 papers
    }
    
    response = requests.get(PUBMED_API_URL, params=params)
    if response.status_code != 200:
        print("Error: Failed to fetch papers from PubMed.")
        return []
    
    result = response.json()
    paper_ids = result.get("esearchresult", {}).get("idlist", [])
    
    if not paper_ids:
        print("No papers found.")
        return []

    return get_paper_details(paper_ids, email)

def get_paper_details(paper_ids: list, email: Optional[str]) -> list:
    """
    Fetch details of papers using PubMed's ESummary API.
    """
    params = {
        "db": "pubmed",
        "id": ",".join(paper_ids),
        "retmode": "json"
    }

    response = requests.get(PUBMED_SUMMARY_URL, params=params)
    if response.status_code != 200:
        print("Error fetching details.")
        return []

    data = response.json()
    paper_details = []

    for paper_id in paper_ids:
        paper_info = data["result"].get(paper_id, {})
        if not paper_info:
            continue

        title = paper_info.get("title", "N/A")
        pub_date = paper_info.get("pubdate", "N/A")
        authors = paper_info.get("authors", [])
        
        # Extract non-academic authors
        non_academic_authors = [a["name"] for a in authors if is_pharma_company(a.get("affiliation", ""))]
        if not non_academic_authors:
            continue
        
        # Extract company affiliations
        company_affiliations = [a.get("affiliation", "N/A") for a in authors if is_pharma_company(a.get("affiliation", ""))]
        
        # Extract corresponding author email
        corresponding_email = email if email else "N/A"
        
        paper_details.append({
            "PubMedID": paper_id,
            "Title": title,
            "Publication Date": pub_date,
            "Non-academic Author(s)": ", ".join(non_academic_authors),
            "Company Affiliation(s)": ", ".join(company_affiliations),
            "Corresponding Author Email": corresponding_email
        })

    return paper_details

def is_pharma_company(affiliation: str) -> bool:
    """
    Identify if the affiliation is related to a pharmaceutical or biotech company.
    """
    keywords = ["pharmaceutical", "biotech", "inc", "corporation", "ltd", "biosciences"]
    return any(keyword.lower() in affiliation.lower() for keyword in keywords)

def save_to_csv(papers: list, filename: str):
    """
    Save paper details to a CSV file.
    """
    df = pd.DataFrame(papers)
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")
