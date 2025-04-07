from together import Together
import os
from dotenv import load_dotenv
import re

class LLMClient:
    
    # Initialize the LLM client by loading the API key
    def __init__(self, reasoningModel: bool = False):
        load_dotenv()
        self.client = Together(api_key=os.getenv("TOGETHERAI_AI_KEY"))
        self.reasoningModel = reasoningModel
        
        if self.reasoningModel:
            self.model = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
        else:
            self.model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

    # Send a prompt to the LLM and return the response
    def generateResponse(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        
        if self.reasoningModel:
            cleanResponse = self.cleanResponse(response.choices[0].message.content)
        else:
            cleanResponse = response.choices[0].message.content
            
        return cleanResponse
    
    # Remove the <think>...</think> section from the response (present in reasoning models)
    def cleanResponse(self, response):
        return re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

    
