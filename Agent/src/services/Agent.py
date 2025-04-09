from LLMClient import LLMClient
from PineconeHandler import PineconeHandler

class Agent:
    
    def __init__(self, reasoningModel=True):
        
        self.contextPrompt=self.loadInitialPrompt("config/contextPrompt.txt")
        self.pineconeHandler = PineconeHandler()
        self.llmClient = LLMClient(reasoningModel)
        
    def loadInitialPrompt(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
        
    def submitQuestion(self, prompt):
        
        context = self.pineconeHandler.query(prompt)
        
        # Create the final prompt for the LLM
        finalPrompt = (
            f"{self.contextPrompt}\n\n"
            "Question:\n"
            f"{prompt}\n\n"
            "Articles context:\n"
            f"{context}"
        )

        # # Debugging output 
        # print("\nAll context:")
        # print(finalPrompt)
        # print("########")
        # print("########")
        # print("########\n")
        
        
        # Get the LLM response
        try:
            response = self.llmClient.generateResponse(finalPrompt)

            print("Response:")
            print(response)
            
        except Exception as e:
            raise
            
            


        
if __name__ == "__main__":
    agent = Agent(reasoningModel=False)
    while True:
        # Prompt the user for a question
        prompt = input("\n\nAsk anything (or 'EXIT' to leave): \n>>>")

        if prompt.strip().upper() == "EXIT":
            break
        
        # Retrieve relevant chunks using the embeddings
        agent.submitQuestion(prompt)

