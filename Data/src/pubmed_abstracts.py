import requests
from xml.etree import ElementTree
import time
import json

def fetch_pubmed_abstracts(keywords, max_results=10, output_file="../JSON/pubmed_abstracts.json", batch_size=5):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    all_abstracts = []
    
    for topic, words in keywords.items():
        for word in words:
            print(f"Fetching abstracts for: {word} (Topic: {topic})...")

            search_query = f"{word} AND 2019/01/01:3000/12/31[DP]"
            search_url = f"{base_url}esearch.fcgi?db=pubmed&term={search_query}&retmax={max_results}&retmode=xml&sort=relevance"
            
            search_response = requests.get(search_url)
            search_root = ElementTree.fromstring(search_response.content)
            id_list = [id_elem.text for id_elem in search_root.findall(".//Id")]

            if not id_list:
                print(f"No articles found for: {word}")
                continue

            for i in range(0, len(id_list), batch_size):
                batch_ids = id_list[i:i + batch_size]
                ids = ",".join(batch_ids)
                
                fetch_url = f"{base_url}efetch.fcgi?db=pubmed&id={ids}&retmode=xml"
                fetch_response = requests.get(fetch_url)
                fetch_root = ElementTree.fromstring(fetch_response.content)
                
                for article in fetch_root.findall(".//PubmedArticle"):
                    pmid = article.find(".//PMID").text if article.find(".//PMID") is not None else ""
                    title_elem = article.find(".//ArticleTitle")
                    title = title_elem.text.strip() if title_elem is not None and title_elem.text else "No title available"
                    abstract_parts = article.findall(".//AbstractText")
                    abstract = " ".join([part.text.strip() for part in abstract_parts if part.text]) if abstract_parts else ""
                    if not abstract:
                        continue
                    date_elem = article.find(".//PubDate/Year")
                    date = date_elem.text if date_elem is not None else "No date available"
                    link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "No link available"
                    
                    authors = []
                    for author in article.findall(".//Author"):
                        last_name = author.find("LastName")
                        first_name = author.find("ForeName")
                        full_name = " ".join(filter(None, [first_name.text if first_name is not None else "", last_name.text if last_name is not None else ""]))
                        if full_name.strip():
                            authors.append(full_name)
                    
                    doi = "No DOI available"
                    for id_elem in article.findall(".//ArticleId"): 
                        if id_elem.attrib.get("IdType") == "doi":
                            doi = id_elem.text
                            break
                    
                    all_abstracts.append({
                        "topic": topic,
                        "title": title,
                        "link": link,
                        "year": date,
                        "authors": authors,
                        "doi": doi,
                        "abstract": abstract
                    })
                
                time.sleep(1)
            
            print(f"Completed fetching abstracts for: {word}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_abstracts, f, ensure_ascii=False, indent=4)
    
    print(f"All abstracts saved to {output_file}")

if __name__ == "__main__":
    with open("../JSON/keywords.json", "r", encoding="utf-8") as f:
        keywords = json.load(f)

    fetch_pubmed_abstracts(keywords, max_results=50, batch_size=5)
