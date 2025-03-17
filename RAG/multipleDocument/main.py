from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# Carregar múltiplos documentos (papers)
documents = []
papers = ["paper1.txt", "paper2.txt", "paper3.txt", "paper4.txt", "paper5.txt"]  # Add your papers here

for paper in papers:
    loader = TextLoader(paper, encoding="utf-8")  # Carregar cada documento
    documents.extend(loader.load())  # Concatenate all loaded documents into the list

# Dividir documentos em partes menores
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
texts = text_splitter.split_documents(documents)

# Criar embeddings usando Ollama
embedding_function = OllamaEmbeddings(model="mistral")

# Criar banco de dados vetorial usando FAISS
vectorstore = FAISS.from_documents(texts, embedding_function)

# Criar o retriever
retriever = vectorstore.as_retriever()

# Criar modelo de linguagem Ollama
llm = OllamaLLM(model="mistral")

# Criar cadeia RAG
qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)

# Loop para perguntas e respostas
while True:
    # Solicitar pergunta ao usuário
    query = input("Faça sua pergunta: ")
    
    if query.lower() == "sair":  # Se o usuário digitar "sair", o loop é interrompido
        print("Saindo...")
        break
    
    # Obter a resposta
    result = qa_chain.invoke(query)

    # A resposta geralmente está no valor da chave 'result'
    answer = result.get('result', '').strip()  # Get the actual answer text (assuming it is in 'result' key)

    # Verificar se a resposta foi encontrada nos documentos
    if not answer or "não encontrado" in answer.lower() or "irrelevante" in answer.lower():
        print("A resposta não foi encontrada nos documentos.")
    else:
        print("Resposta:", answer)
