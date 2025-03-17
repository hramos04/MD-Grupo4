from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# Carregar documentos
loader = TextLoader("documento.txt", encoding="utf-8")  # Substitua pelo seu arquivo de texto
documents = loader.load()

# Dividir documentos em partes menores
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# Criar embeddings usando Ollama
embedding_function = OllamaEmbeddings(model="mistral")  # Substitua pelo modelo desejado

# Criar banco de dados vetorial usando FAISS
vectorstore = FAISS.from_documents(texts, embedding_function)

# Criar o retriever
retriever = vectorstore.as_retriever()

# Criar modelo de linguagem Ollama
llm = OllamaLLM(model="mistral")

# Criar cadeia RAG
qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)

# Fazer uma pergunta ao RAG
query = "Qual é o resumo do documento?"
result = qa_chain.invoke(query)

print("Resposta:", result)