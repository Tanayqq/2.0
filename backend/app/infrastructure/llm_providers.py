from groq import Groq
from app.domain.interfaces import LLMProviderProtocol

class GroqProvider(LLMProviderProtocol):
    """
    Implementation of the LLMProviderProtocol using Groq API.
    Optimized for speed during development.
    """
    def __init__(self, api_key: str, model_name: str = "llama-3.1-8b-instant"):
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        import time
        import re
        import groq

        retries = 0
        max_retries = 8
        while retries < max_retries:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are MedRef, a highly strict Clinical Reference Assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    model=self.model_name,
                    temperature=0.0, # Zero hallucination tolerance
                )
                return chat_completion.choices[0].message.content
            except groq.RateLimitError as e:
                wait_time = 35.0
                # Extract wait time from error message
                msg = str(e)
                match = re.search(r"try again in\s*([0-9.]+)", msg, re.IGNORECASE)
                if match:
                    wait_time = max(35.0, float(match.group(1)) + 1.0)
                
                print(f"\n[RateLimit] Groq API rate limit reached. Waiting for {wait_time:.2f} seconds before retrying (Attempt {retries+1}/{max_retries})...")
                time.sleep(wait_time)
                retries += 1
            except Exception as e:
                msg = str(e)
                if "rate limit" in msg.lower() or "429" in msg:
                    wait_time = 40.0
                    print(f"\n[RateLimit] Rate limit detected: {msg}. Waiting for {wait_time}s before retrying (Attempt {retries+1}/{max_retries})...")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    raise e
                    
        # If we exhausted all retries, raise the last exception
        raise RuntimeError("Groq API rate limit retries exhausted.")

class MedGemmaProvider(LLMProviderProtocol):
    """
    Target production medical model (Placeholder for Phase 1).
    Ensures architecture is ready for swapping.
    """
    def __init__(self):
        pass
    
    def generate(self, prompt: str) -> str:
        raise NotImplementedError("MedGemma integration deferred to production phase.")
