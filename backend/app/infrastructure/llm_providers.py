"""
MedRef LLM Providers Module
Integrates Groq, Gemini, and MedGemma providers behind the common LLMProviderProtocol interface.
Enforces the centralized ConversationPipeline preprocessing gatekeeper before every API request to guarantee
no invalid conversation payload (such as ending with a model turn) reaches downstream LLM services.
"""

from typing import List, Dict, Any, Optional
from groq import Groq
from app.domain.interfaces import LLMProviderProtocol
from app.infrastructure.conversation_pipeline import ConversationPipeline, PipelineResult


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

    def generate_chat(self, messages: List[Dict[str, str]], session_id: Optional[str] = None) -> str:
        import time
        import re
        import groq

        # Centralized Conversation Pipeline Processing Gatekeeper
        pipeline_res: PipelineResult = ConversationPipeline.process(messages, provider="groq", session_id=session_id)
        sanitized_messages = pipeline_res.processed_messages

        # Model cascade order for rate limit failover
        models_to_try = [self.model_name, "llama-3.1-8b-instant", "llama-3.3-70b-versatile", "llama3-8b-8192"]
        models_to_try = list(dict.fromkeys(models_to_try))

        last_exception = None

        for model_choice in models_to_try:
            retries = 0
            max_retries = 3
            current_messages = [dict(m) for m in sanitized_messages]

            while retries < max_retries:
                try:
                    chat_completion = self.client.chat.completions.create(
                        messages=current_messages,
                        model=model_choice,
                        temperature=0.0,  # Zero hallucination tolerance
                        frequency_penalty=0.5,
                        presence_penalty=0.3,
                    )
                    return chat_completion.choices[0].message.content
                except groq.RateLimitError as e:
                    last_exception = e
                    msg = str(e)
                    wait_time = 5.0
                    match = re.search(r"try again in\s*([0-9.]+)", msg, re.IGNORECASE)
                    if match:
                        wait_time = float(match.group(1))

                    # If token size exceeded (413 / requested > limit)
                    if "413" in msg or "request too large" in msg.lower() or "limit" in msg.lower():
                        print(f"\n[Token Limit Exceeded] Compressing message payload for model '{model_choice}'...")
                        for m in current_messages:
                            if len(m.get("content", "")) > 4000:
                                m["content"] = m["content"][:4000] + "\n...[Context compressed to comply with Groq TPM token limits]..."
                        retries += 1
                        time.sleep(0.5)
                        continue
                    
                    # If wait time is manageable (<= 8s), wait and retry same model
                    if wait_time <= 8.0:
                        print(f"\n[RateLimit] Groq model '{model_choice}' rate limited. Waiting {wait_time:.2f}s before retry...")
                        time.sleep(wait_time + 0.5)
                        retries += 1
                    else:
                        # Otherwise break loop and cascade immediately to next model in list
                        print(f"\n[RateLimit Failover] Model '{model_choice}' wait time ({wait_time:.1f}s) too high. Cascading to next model...")
                        break
                except Exception as e:
                    last_exception = e
                    msg = str(e)
                    is_token_limit = any(k in msg.lower() for k in ["rate limit", "429", "413", "rate_limit_exceeded", "too large", "tpm"])
                    if is_token_limit:
                        if ("413" in msg or "too large" in msg.lower() or "limit" in msg.lower()) and retries == 0:
                            print(f"\n[Token Limit Exceeded] Compressing payload for model '{model_choice}' after exception...")
                            for m in current_messages:
                                if len(m.get("content", "")) > 4000:
                                    m["content"] = m["content"][:4000] + "\n...[Context compressed to comply with Groq TPM token limits]..."
                            retries += 1
                            time.sleep(0.5)
                            continue
                        break
                    else:
                        raise e

        # If all Groq models exhausted, attempt Gemini failover if key exists
        import os
        gemini_key = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
        if gemini_key:
            try:
                print("\n[RateLimit Failover] All Groq models rate limited. Failing over to Google Gemini Provider...")
                gemini_provider = GeminiProvider(api_key=gemini_key)
                return gemini_provider.generate_chat(messages, session_id=session_id)
            except Exception as gem_err:
                print(f"[RateLimit Failover Error] Gemini failover failed: {gem_err}")

        raise RuntimeError(f"Groq API rate limit reached across models. Details: {last_exception}")



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

    def generate_chat(self, messages: List[Dict[str, str]], session_id: Optional[str] = None) -> str:
        # Centralized Conversation Pipeline Processing Gatekeeper for Gemini
        pipeline_res: PipelineResult = ConversationPipeline.process(messages, provider="gemini", session_id=session_id)
        sanitized_messages = pipeline_res.processed_messages

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
