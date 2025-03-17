# Extração e Preparação de Dados

O objetivo para já é o uso de scripts em `python` para extração de dados. Os dados extraídos são armazenados em arquivos JSON para futuramente serem migrados para MongoDB.

## Estrutura do Projeto
```
.
├── keywords.json                  # Lista de palavras-chave para pesquisa
├── FirstLevel.json                # Dados processados em formato JSON
├── pubmed_abstracts.json          # Resumos extraídos do PubMed
├── google_scholar_papers.json     # Artigos extraídos do Google Scholar
├── google_scholar.py              # Script para extração no Google Scholar
├── pubmed_abstracts.py            # Script para extração no PubMed
└── README.md                      # Documentação do projeto
```

## Como Usar
1. Definir as palavras-chave no arquivo `keywords.json`.
2. Executar `pubmed_abstracts.py` para obter resumos do PubMed.
3. Executar `google_scholar.py` para obter artigos do Google Scholar.
4. Os resultados estarão nos arquivos JSON correspondentes.
5. Futuramente extrair os PDFs do `google_scholar_papers.json`.
6. Extrair texto dos PDFs.
8. Migrar tudo para MongoDB.
