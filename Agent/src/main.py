from LLMClient import LLMClient
from PineconeHandler import PineconeHandler

def main():
    
    # Read the context prompt from file
    with open("config/contextPrompt.txt", "r", encoding="utf-8") as f:  
        contextPrompt= f.read()
    
    # Load pinecone API key and environment
    pineconeHandler = PineconeHandler()
    
    # Initialize the LLM client
    llmClient = LLMClient(reasoningModel=True)

    while True:
        # Prompt the user for a question
        prompt = input("\n\nAsk anything (or 'EXIT' to leave): \n>>>")

        if prompt.strip().upper() == "EXIT":
            break
        
        # Retrieve relevant chunks using the embeddings
        context = pineconeHandler.query(prompt)
        
        # Create the final prompt for the LLM
        finalPrompt = (
            f"{contextPrompt}\n\n"
            "### Question:\n"
            f"{prompt}\n\n"
            "### Articles context:\n"
            f"{context}"
        )

        # # Debugging output
        # print("\nContexto RAG:")
        # print(finalPrompt)
        # print("########")
        # print("########")
        # print("########\n")
        
        
        # Get the LLM response
        try:
            response = llmClient.generateResponse(finalPrompt)

            print("Resposta do LLM:")
            print(response)
            
        except Exception as e:
            print(e)
            continue

if __name__ == "__main__":
    main()
