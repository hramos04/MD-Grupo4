import requests
import json
import time

def fetch_semantic_scholar_abstracts(keywords, max_results=10, output_file="../JSON/semantic_scholar_abstracts.json", batch_size=5, api_key="TUA_API_KEY"):
    headers = {"x-api-key": api_key}
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    all_abstracts = []

    for topic, words in keywords.items():
        for word in words:
            print(f"Fetching papers for: {word} (Topic: {topic})...")
            offset = 0

            while offset < max_results:
                params = {
                    "query": word,
                    "limit": min(batch_size, max_results - offset),
                    "offset": offset,
                    "fields": "title,abstract,year,authors,url,externalIds"
                }

                response = requests.get(base_url, headers=headers, params=params)
                if response.status_code != 200:
                    print(f"Erro na request: {response.status_code} - {response.text}")
                    break

                data = response.json().get("data", [])
                if not data:
                    break

                for paper in data:
                    if not paper.get("abstract"):
                        continue

                    authors = [a.get("name") for a in paper.get("authors", []) if a.get("name")]
                    doi = paper.get("externalIds", {}).get("DOI", "No DOI available")

                    all_abstracts.append({
                        "topic": topic,
                        "title": paper.get("title", "No title available"),
                        "link": paper.get("url", "No link available"),
                        "year": paper.get("year", "No year available"),
                        "authors": authors,
                        "doi": doi,
                        "abstract": paper["abstract"]
                    })

                offset += batch_size
                time.sleep(1)

            print(f"Completed fetching papers for: {word}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_abstracts, f, ensure_ascii=False, indent=4)

    print(f"All abstracts saved to {output_file}")

if __name__ == "__main__":
    with open("../JSON/keywords.json", "r", encoding="utf-8") as f:
        keywords = json.load(f)

    fetch_semantic_scholar_abstracts(keywords, max_results=50, batch_size=5, api_key="TUA_API_KEY")
