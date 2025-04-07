import json
import time
import random
from scholarly import scholarly

def fetch_google_scholar_papers(query, topic, max_results=10, min_year=2019):
    try:
        search_query = scholarly.search_pubs(query)
    except Exception as e:
        print(f"Error searching '{query}': {e}")
        return []
    
    papers = []
    for _ in range(max_results * 2):
        try:
            paper = next(search_query)
        except StopIteration:
            break
        except Exception as e:
            print(f"Error getting paper: {e}")
            continue

        title = paper.get("bib", {}).get("title", "Title unavailable")
        authors = paper.get("bib", {}).get("author", "Authors unavailable")
        year = paper.get("bib", {}).get("pub_year", None)
        abstract = paper.get("bib", {}).get("abstract", "Abstract unavailable")
        pdf_link = paper.get("pub_url", "No PDF link available")
        doi = paper.get("bib", {}).get("doi", "DOI unavailable")
        
        if year and year.isdigit() and int(year) >= min_year:
            citations = paper.get("num_citations", 0)
            if citations >= 20:
                papers.append({
                    "topic": topic,
                    "title": title,
                    "authors": authors,
                    "year": int(year),
                    "abstract": abstract,
                    "pdf_link": pdf_link,
                    "doi": doi,
                    "citations": citations
                })

        if len(papers) >= max_results:
            break

        time.sleep(random.uniform(10, 20))

    return papers

if __name__ == "__main__":
    try:
        with open("../JSON/keywords.json", "r", encoding="utf-8") as f:
            keywords = json.load(f)
    except Exception as e:
        print(f"Error loading 'keywords.json': {e}")
        exit(1)

    try:
        with open("../JSON/google_scholar_papers.json", "r", encoding="utf-8") as file:
            all_papers = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        all_papers = []

    for topic, words in keywords.items():
        for word in words:
            print(f"Searching papers about: {word} (Topic: {topic})")
            papers = fetch_google_scholar_papers(word, topic, max_results=50, min_year=2019)
            
            if papers:
                all_papers.extend(papers)
                with open("../JSON/google_scholar_papers.json", "w", encoding="utf-8") as file:
                    json.dump(all_papers, file, ensure_ascii=False, indent=4)
            
            time.sleep(random.uniform(60, 120))

    print("Papers saved in 'google_scholar_papers.json'")
