"""
MedRef LLM Providers Module
Integrates Groq, Gemini, and MedGemma providers behind the common LLMProviderProtocol interface.
Enforces the centralized Conversation Validation Layer before every API request to guarantee
no invalid conversation payload (such as ending with a model turn) reaches downstream LLM services.
"""

from typing import List, Dict, Any, Optional
from groq import Groq
from app.domain.interfaces import LLMProviderProtocol
from app.infrastructure.conversation_validator import ConversationValidator


class GroqProvider(LLMProviderProtocol):
    """
    Implementation of the LLMProviderProtocol using Groq API.
    Optimized for speed during development.
    """
    def __init__(self, api_key: str, model_name: str = "llama-3.1-8b-instant"):
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": "You are MedRef, a highly strict Clinical Reference Assistant. Never repeat sentences in a loop."},
            {"role": "user", "content": prompt}
        ]
        return self.generate_chat(messages)

    def generate_chat(self, messages: List[Dict[str, str]]) -> str:
        import time
        import re
        import groq

        # Centralized Conversation Validation Gatekeeper
        sanitized_messages = ConversationValidator.validate_and_sanitize(messages, target_provider="groq")

        retries = 0
        max_retries = 8
        while retries < max_retries:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=sanitized_messages,
                    model=self.model_name,
                    temperature=0.0,  # Zero hallucination tolerance
                    frequency_penalty=0.5,
                    presence_penalty=0.3,
                )
                return chat_completion.choices[0].message.content
            except groq.RateLimitError as e:
                wait_time = 35.0
                msg = str(e)
                match = re.search(r"try again in\s*([0-9.]+)", msg, re.IGNORECASE)
                if match:
                    wait_time = max(10.0, float(match.group(1)) + 1.0)
                
                if wait_time > 10.0:
                    raise RuntimeError(f"Groq API rate limit reached. Please try again in {int(wait_time)} seconds.")
                
                print(f"\n[RateLimit] Groq API rate limit reached. Waiting for {wait_time:.2f} seconds before retrying (Attempt {retries+1}/{max_retries})...")
                time.sleep(wait_time)
                retries += 1
            except Exception as e:
                msg = str(e)
                if "rate limit" in msg.lower() or "429" in msg:
                    raise RuntimeError(f"Groq API rate limit reached: {msg}. Please try again later.")
                else:
                    raise e
                    
        raise RuntimeError("Groq API rate limit retries exhausted.")


class GeminiProvider(LLMProviderProtocol):
    """
    Production-grade Google Gemini LLM Provider integration.
    Fully compliant with Google Gemini API turn discipline (strictly ending with a 'user' turn).
    """
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro"):
        self.api_key = api_key
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
            except ImportError:
                raise RuntimeError("google-generativeai package is not installed. Install via pip install google-generativeai.")
        return self._model

    def generate(self, prompt: str) -> str:
        messages = [
            {"role": "user", "content": prompt}
        ]
        return self.generate_chat(messages)

    def generate_chat(self, messages: List[Dict[str, str]]) -> str:
        # Centralized Conversation Validation Gatekeeper for Gemini
        sanitized_messages = ConversationValidator.validate_and_sanitize(messages, target_provider="gemini")

        # Format messages for Gemini SDK (contents format)
        gemini_contents = []
        for msg in sanitized_messages:
            role = "user" if msg["role"] in ("user", "system") else "model"
            gemini_contents.append({"role": role, "parts": [msg["content"]]})

        model = self._get_model()
        response = model.generate_content(gemini_contents)
        return response.text


class MedGemmaProvider(LLMProviderProtocol):
    """
    Target production medical model (Placeholder for Phase 1).
    Ensures architecture is ready for swapping.
    """
    def __init__(self):
        pass
    
    def generate(self, prompt: str) -> str:
        raise NotImplementedError("MedGemma integration deferred to production phase.")
