import re
from pdfminer.high_level import extract_text
import os
import requests
import time
from dotenv import load_dotenv
load_dotenv()

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HEADERS = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}


keywords = [
    # Álcool & Drogas
    "alcohol", "binge drinking", "alcoholism", "liver disease", "addiction", 
    "drugs", "substance abuse", "opioids", "cocaine", "cannabis", "overdose", "rehabilitation",

    # Saúde & Higiene Pública
    "health", "mental health", "physical health", "immune system", "nutrition", 
    "fitness", "exercise", "hygiene", "public hygiene", "infection control", "disease prevention",

    # Trabalho & Ergonomia
    "work", "occupational health", "workplace safety", "job stress", "burnout", 
    "productivity", "work-life balance", "ergonomics", "posture", "back pain", "chronic pain",

    # Sono & Qualidade de Vida
    "sleep", "sleep quality", "circadian rhythm", "REM sleep", "sleep deprivation", 
    "insomnia", "melatonin", "sleep hygiene", "cognitive performance", "fatigue", "alertness",

    # Tabagismo & Saúde Pulmonar
    "tobacco", "nicotine", "smoking", "cigarettes", "vaping", "smoking cessation", 
    "lungs", "respiratory health", "COPD", "lung cancer", "breathing exercises"
]


def extract_text_from_pdf(pdf_path):
    """Extrai o texto do PDF."""
    return extract_text(pdf_path)

def remove_page_numbers_and_headers(text):
    """Remove números de página, cabeçalhos e rodapés."""
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        if re.fullmatch(r'\s*\d+\s*', line):  # Remove números de página isolados
            continue
        if re.search(r'page\s+\d+\s+of\s+\d+', line, flags=re.IGNORECASE):  # "Page X of Y"
            continue
        if re.fullmatch(r'\s*[A-ZÀ-Ÿ ]{4,}\s*', line):  # Cabeçalhos em maiúsculas
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def remove_bibliographic_references(text):
    """Remove referências tipo [1] e (Smith, 2020)."""
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\([A-Za-zÀ-ÿ]+,\s*\d{4}\)', '', text)
    return text

def remove_titles_and_subtitles(text):
    """Remove títulos e subtítulos do texto."""
    lines = text.splitlines()
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Remove linhas curtas totalmente em maiúsculas (títulos comuns)
        if re.fullmatch(r'[A-ZÀ-Ÿ\s\-]{4,}', line):
            continue
        
        # Remove títulos com numeração (ex: "1. Introdução" ou "2.1 Definição")
        if re.fullmatch(r'\d+(\.\d+)*\s+[A-Za-zÀ-ÿ]+.*', line):
            continue
        
        # Remove títulos no formato "Capítulo X - Nome" ou "Seção X: Nome"
        if re.fullmatch(r'(Cap(í|i)tulo|Seç(ã|a)o)\s+\d+[:\-]\s+.*', line, re.IGNORECASE):
            continue
        
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def clean_text(text):
    """Remove elementos irrelevantes como cabeçalhos, rodapés, referências, links, títulos e espaços extras."""
    text = remove_page_numbers_and_headers(text)
    text = remove_bibliographic_references(text)
    text = remove_titles_and_subtitles(text)

    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)

    # Remove emails
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', '', text)

    # Remove caracteres estranhos ou sequências não naturais
    text = re.sub(r'[\[\]\(\)\{\}<>]', '', text)  # Remove parênteses e colchetes soltos
    text = re.sub(r'[_~#*]', '', text)  # Remove símbolos inúteis
    text = re.sub(r'\s+', ' ', text).strip()  # Remove espaços e quebras de linha excessivas

    return text

def filter_relevant_text(text, keywords):
    """Mantém apenas frases que contenham palavras-chave relevantes."""
    sentences = text.split(". ")
    relevant_sentences = [s for s in sentences if any(kw.lower() in s.lower() for kw in keywords)]
    return "\n ".join(relevant_sentences)


def summarize_text(text, max_retries=5):
    payload = {
        "inputs": text,
        "parameters": {"max_length": 200, "min_length": 50, "do_sample": False},
    }
    retries = 0
    while retries < max_retries:
        response = requests.post(API_URL, headers=HEADERS, json=payload)

        if response.status_code == 429:  # Too Many Requests
            wait_time = 2 ** retries  # 2, 4, 8, 16...
            print(f"Rate limit atingido! A aguardar {wait_time}s antes de tentar novamente...")
        
        elif response.status_code == 503:  # Service Unavailable
            wait_time = 10  
            print(f"Serviço temporariamente indisponível. A aguardar {wait_time}s antes de tentar novamente...")

        else:
            if response.status_code != 200:
                return f"Erro HTTP {response.status_code}: {response.text}"

            try:
                result = response.json()
                if isinstance(result, list):
                    return result[0].get("summary_text", "Erro: Resumo não encontrado.")
                return f"Erro: {result.get('error', 'Resposta inválida')}"
            except requests.exceptions.JSONDecodeError:
                return "Erro: Resposta vazia ou inválida da API."

        time.sleep(wait_time)
        retries += 1

    return "Erro: Número máximo de tentativas atingido. Tenta mais tarde."




def process_pdf(pdf_path):
    """Processa o PDF inteiro: extrai, limpa, filtra e resume."""
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(raw_text) 

    #filtered_text = filter_relevant_text(cleaned_text, keywords)
    
    # final_text = []
    # for line in filtered_text.split("\n"):  
    #     if len(line.split()) >= 30: 
    #         summarized_line = summarize_text(line)
    #         final_text.append(summarized_line)
    
    return cleaned_text
    return "\n".join(final_text)



if __name__ == "__main__":
    pdf_dir = "../PDF"
    output_dir = "../PDF_Text"

    os.makedirs(output_dir, exist_ok=True) 

    for filename in os.listdir(pdf_dir):

        if filename.lower().endswith(".pdf"): 
            pdf_path = os.path.join(pdf_dir, filename)
            processed_text = process_pdf(pdf_path)

            output_filename = os.path.splitext(filename)[0] + ".txt"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(processed_text)

            print(f"{filename} completed!")

    print(f"Processing completed! Extracted texts are saved in '{output_dir}'")