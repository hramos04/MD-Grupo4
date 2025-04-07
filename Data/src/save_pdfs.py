import json
import os
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
]

def create_session():
    session = requests.Session()
    session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[400, 403, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def get_pdf_link(session, page_url):
    """Tenta extrair o link PDF direto da página."""
    try:
        response = session.get(page_url, timeout=10)
        if response.status_code != 200:
            print(f"Erro ao aceder {page_url} (status code {response.status_code})")
            return None
    except Exception as e:
        print(f"Erro a aceder {page_url}: {e}")
        return None

    # Tenta usar o parser padrão; se falhar, tenta lxml
    try:
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Erro a fazer parsing com html.parser em {page_url}: {e}. A tentar lxml...")
        try:
            soup = BeautifulSoup(response.text, "lxml")
        except Exception as e:
            print(f"Erro a fazer parsing com lxml em {page_url}: {e}")
            return None

    pdf_link = None

    # Procura por links que contenham ".pdf"
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if ".pdf" in href.lower():
            pdf_link = href
            break

    # Se não encontrou em links, tenta em iframes
    if not pdf_link:
        iframe = soup.find("iframe", src=True)
        if iframe:
            src = iframe["src"]
            if ".pdf" in src.lower():
                pdf_link = src

    if pdf_link:
        pdf_link = urljoin(page_url, pdf_link)
    return pdf_link

def download_pdf(session, pdf_url, file_name):
    """Faz o download do PDF a partir do link direto."""
    try:
        response = session.get(pdf_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erro a descarregar {pdf_url}: {e}")
        return False

    try:
        with open(file_name, 'wb') as pdf_file:
            pdf_file.write(response.content)
        print(f"Ficheiro guardado: {file_name}")
        return True
    except Exception as e:
        print(f"Erro ao guardar {file_name}: {e}")
        return False

def main():
    json_file = "../JSON/google_scholar_papers.json"
    dir_path = "../PDF"
    os.makedirs(dir_path, exist_ok=True)

    if not os.path.exists(json_file):
        print(f"Erro: Ficheiro {json_file} não encontrado.")
        return

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            articles = json.load(f)
    except Exception as e:
        print(f"Erro a ler {json_file}: {e}")
        return

    session = create_session()

    articles = articles[50:]

    for article in articles:
        title = article.get("title", "untitled")
        page_url = article.get("pdf_link")
        if not page_url:
            print(f"Sem link para o artigo: {title}")
            continue

        print(f"Processando: {title}")
        pdf_url = get_pdf_link(session, page_url)
        if not pdf_url:
            print(f"Não foi possível encontrar link PDF para: {title}")
            continue

        safe_title = "".join(c for c in title if c.isalnum() or c in " _-")
        file_name = f"{safe_title}.pdf"
        file_path = os.path.join(dir_path, file_name)

        download_pdf(session, pdf_url, file_path)
        time.sleep(random.uniform(2, 5))
        print("------------------------------------------------")

if __name__ == "__main__":
    main()
