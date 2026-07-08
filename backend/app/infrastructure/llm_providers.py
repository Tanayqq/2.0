from groq import Groq
from app.domain.interfaces import LLMProviderProtocol

class GroqProvider(LLMProviderProtocol):
    """
    Implementation of the LLMProviderProtocol using Groq API.
    Optimized for speed during development.
    """
    def __init__(self, api_key: str, model_name: str = "llama3-8b-8192"):
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are MedRef, a highly strict Clinical Reference Assistant."},
                {"role": "user", "content": prompt}
            ],
            model=self.model_name,
            temperature=0.0, # Zero hallucination tolerance
        )
        return chat_completion.choices[0].message.content

class MedGemmaProvider(LLMProviderProtocol):
    """
    Target production medical model (Placeholder for Phase 1).
    Ensures architecture is ready for swapping.
    """
    def __init__(self):
        pass
    
    def generate(self, prompt: str) -> str:
        raise NotImplementedError("MedGemma integration deferred to production phase.")
