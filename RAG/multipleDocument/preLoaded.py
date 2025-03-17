import os
import pickle
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# Define file paths for the saved embeddings and FAISS index
faiss_index_file = "embeddings/vectorstore.faiss"
faiss_metadata_file = "embeddings/vectorstore_metadata.pkl"

# Create embeddings using Ollama
embedding_function = OllamaEmbeddings(model="mistral")

# Check if the precomputed embeddings already exist
if os.path.exists(faiss_index_file) and os.path.exists(faiss_metadata_file):
    print("Loading precomputed embeddings...")
    # Load the FAISS index and the document metadata (with the flag to allow dangerous deserialization)
    vectorstore = FAISS.load_local(faiss_index_file, embedding_function, allow_dangerous_deserialization=True)
    with open(faiss_metadata_file, "rb") as f:
        texts = pickle.load(f)  # Load the metadata (documents)
else:
    print("Creating new embeddings...")
    
    # Load multiple documents (papers)
    documents = []
    papers = ["paper1.txt", "paper2.txt", "paper3.txt", "paper4.txt", "paper5.txt"]  # Add your paper files here
    
    for paper in papers:
        loader = TextLoader(paper, encoding="utf-8")
        documents.extend(loader.load())  # Concatenate all loaded documents into the list
    
    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    texts = text_splitter.split_documents(documents)
    
    # Create a FAISS vector store using the documents and embeddings
    vectorstore = FAISS.from_documents(texts, embedding_function)
    
    # Save the FAISS index and the metadata (documents)
    vectorstore.save_local(faiss_index_file)
    with open(faiss_metadata_file, "wb") as f:
        pickle.dump(texts, f)
    
    print("Embeddings created and saved.")

# Create the retriever
retriever = vectorstore.as_retriever()

# Create the Ollama language model
llm = OllamaLLM(model="mistral")

# Create the RAG chain
qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)

# Loop for continuous question and answer interaction
while True:
    query = input("Faça sua pergunta: ")
    
    if query.lower() == "sair":  # Exit the loop if user types 'sair'
        print("Saindo...")
        break
    
    # Get the answer to the query
    result = qa_chain.invoke(query)
    
    # Get the actual answer (usually in 'result' key)
    answer = result.get('result', '').strip()

    # Check if a valid answer was found
    if not answer:
        print("A resposta não foi encontrada nos documentos.")
    else:
        print("Resposta:", answer)
