from LLMClient import LLMClient
from PineconeHandler import PineconeHandler

def main():
    
    # Read the context prompt from file
    with open("config/contextPrompt.txt", "r", encoding="utf-8") as f:
        contextPrompt= f.read()
    
    # Load pinecone API key and environment
    pineconeHandler = PineconeHandler()
    
    # Initialize the LLM client
    llmClient = LLMClient()

    while True:
        # Prompt the user for a question
        prompt = input("\n\nDigite a sua pergunta (ou 'EXIT' para sair): \n>>>")
        if prompt.strip().upper() == "EXIT":
            break
        
        # Retrieve relevant chunks using the embeddings
        context = pineconeHandler.query(prompt, topK=3)
        
        # Create the final prompt for the LLM
        finalPrompt = (
            f"{contextPrompt}\n\n"
            "### Pergunta:\n"
            f"{prompt}\n\n"
            "### Contexto de artigos:\n"
            f"{context}"
        )

        # Debugging output
        print("\nContexto RAG:")
        print(finalPrompt)
        print("########")
        print("########")
        print("########\n")
        
        
        # Get the LLM response
        response = llmClient.generateResponse(finalPrompt)

        print("Resposta do LLM:")
        print(response)

if __name__ == "__main__":
    main()
