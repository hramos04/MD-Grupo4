# Extração e Preparação de Dados

O objetivo para já é o uso de scripts em `python` para extração de dados. Os dados extraídos são armazenados em arquivos JSON para futuramente serem migrados para MongoDB.

## Estrutura do Projeto
```
.
├── JSON/
│   ├── keywords.json                # Lista de palavras-chave para pesquisa
│   ├── FirstLevel.json              # Dados processados e organizados em JSON
│   ├── google_scholar_papers.json   # Artigos extraídos do Google Scholar
│   └── pubmed_abstracts.json        # Resumos extraídos do PubMed
│
├── PDF/                             # PDFs descarregados dos links encontrados
│
├── PDF_Text/                        # Texto extraído de cada PDF (formato .txt)
│
├── src/
│   ├── google_scholar.py            # Extrai artigos do Google Scholar
│   ├── pubmed_abstracts.py          # Extrai resumos do PubMed
│   ├── save_pdfs.py                 # Faz download dos PDFs a partir dos links
│   └── extract_from_pdf.py          # Extrai texto dos PDFs (opcional/descontinuado)
│
└── README.md                        # Documentação do projeto

```

## Como Usar
1. Definir as palavras-chave no arquivo `keywords.json`.
2. Executar `pubmed_abstracts.py` para obter resumos do PubMed.
3. Executar `google_scholar.py` para obter artigos do Google Scholar.
4. Os resultados estarão nos arquivos JSON correspondentes.
5. Extrair os PDFs do `google_scholar_papers.json`.   # alterar a partir daqui
6. Extrair texto dos PDFs. 
8. Migrar tudo para MongoDB.
