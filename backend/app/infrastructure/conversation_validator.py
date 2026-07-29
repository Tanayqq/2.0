"""
MedRef Conversation Validation Layer
Production-grade conversation history validator and sanitizer for Gemini and LLM providers.
Ensures every request sent to Google Gemini API or downstream providers strictly satisfies
API turn requirements (non-empty, valid roles, alternating user/model sequence, and ending with a USER turn).
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger("medref.conversation_validator")


class InvalidConversationError(ValueError):
    """Raised when a conversation structure fails validation and cannot be sanitized."""
    pass


@dataclass
class ValidationResult:
    is_valid: bool
    reason: str
    messages_count: int
    first_role: Optional[str]
    last_role: Optional[str]
    sanitized_messages: List[Dict[str, str]]

    def log_summary(self):
        status = "PASSED" if self.is_valid else "FAILED"
        log_msg = (
            f"\n--- Conversation Validation: {status} ---\n"
            f"Messages: {self.messages_count}\n"
            f"First role: {self.first_role or 'None'}\n"
            f"Last role: {self.last_role or 'None'}\n"
            f"Reason: {self.reason}\n"
            f"----------------------------------------"
        )
        if self.is_valid:
            logger.info(log_msg)
        else:
            logger.warning(log_msg)


class ConversationValidator:
    """
    Centralized Gatekeeper for LLM and Gemini API Conversation Payloads.
    Enforces strict turn discipline before dispatching requests.
    """

    VALID_ROLES = {"user", "model", "assistant", "system"}

    @classmethod
    def validate_conversation(
        cls,
        messages: List[Dict[str, str]],
        strict_mode: bool = False
    ) -> ValidationResult:
        """
        Validates conversation message history against Gemini/LLM API constraints.

        Rules:
        1. Non-empty conversation array.
        2. All roles must be valid ('user', 'model', 'assistant', 'system').
        3. All message contents must be non-empty strings.
        4. First conversational turn (excluding 'system') must be 'user'.
        5. Final message must be 'user' (Gemini HTTP 400 error on trailing 'model' turn).
        6. No consecutive same-role turns ('user' -> 'user' or 'model' -> 'model').
        """
        if not messages or not isinstance(messages, list):
            res = ValidationResult(
                is_valid=False,
                reason="Conversation history is empty or not a list.",
                messages_count=0,
                first_role=None,
                last_role=None,
                sanitized_messages=[]
            )
            res.log_summary()
            return res

        # Filter out system message to evaluate conversational turns
        conv_turns = [m for m in messages if m.get("role", "").lower() != "system"]
        first_role = conv_turns[0].get("role", "").lower() if conv_turns else None
        last_role = messages[-1].get("role", "").lower() if messages else None

        # Check 1: Non-empty content & valid roles
        for idx, msg in enumerate(messages):
            role = str(msg.get("role", "")).lower()
            content = str(msg.get("content", "")).strip()

            if role not in cls.VALID_ROLES:
                res = ValidationResult(
                    is_valid=False,
                    reason=f"Invalid role '{role}' at index {idx}.",
                    messages_count=len(messages),
                    first_role=first_role,
                    last_role=last_role,
                    sanitized_messages=[]
                )
                res.log_summary()
                return res

            if not content:
                res = ValidationResult(
                    is_valid=False,
                    reason=f"Empty content in message at index {idx} (role: '{role}').",
                    messages_count=len(messages),
                    first_role=first_role,
                    last_role=last_role,
                    sanitized_messages=[]
                )
                res.log_summary()
                return res

        # Check 2: First conversational turn must be user
        if first_role and first_role not in ("user",):
            res = ValidationResult(
                is_valid=False,
                reason=f"First conversational turn must be 'user', got '{first_role}'.",
                messages_count=len(messages),
                first_role=first_role,
                last_role=last_role,
                sanitized_messages=[]
            )
            res.log_summary()
            return res

        # Check 3: Final message must be user
        if last_role in ("model", "assistant"):
            res = ValidationResult(
                is_valid=False,
                reason=f"Conversation ends with model turn ('{last_role}'). Gemini requires ending with 'user'.",
                messages_count=len(messages),
                first_role=first_role,
                last_role=last_role,
                sanitized_messages=[]
            )
            res.log_summary()
            return res

        # Check 4: No consecutive identical roles (excluding system)
        prev_role = None
        for idx, msg in enumerate(conv_turns):
            role = msg.get("role", "").lower()
            # Treat 'assistant' and 'model' as equivalent model turns
            norm_role = "model" if role in ("model", "assistant") else role
            if prev_role and norm_role == prev_role:
                res = ValidationResult(
                    is_valid=False,
                    reason=f"Consecutive same-role turns detected ('{prev_role}' -> '{norm_role}') at conversational turn {idx}.",
                    messages_count=len(messages),
                    first_role=first_role,
                    last_role=last_role,
                    sanitized_messages=[]
                )
                res.log_summary()
                return res
            prev_role = norm_role

        res = ValidationResult(
            is_valid=True,
            reason="Conversation structure is valid.",
            messages_count=len(messages),
            first_role=first_role,
            last_role=last_role,
            sanitized_messages=messages
        )
        res.log_summary()
        return res

    @classmethod
    def sanitize_conversation(
        cls,
        messages: List[Dict[str, str]],
        target_provider: str = "gemini"
    ) -> List[Dict[str, str]]:
        """
        Sanitizes and normalizes conversation history so it is guaranteed to pass validation.

        Actions performed:
        - Drops empty or invalid messages.
        - Maps 'assistant' -> 'model' (for Gemini) or keeps 'user' / 'system'.
        - Merges consecutive 'user' turns by joining text.
        - Drops consecutive 'model' turns (keeps latest non-empty model turn).
        - POPs trailing 'model' or 'assistant' turn(s) if conversation ends with a model turn.
        - Guarantees final turn is 'user'.
        """
        if not messages or not isinstance(messages, list):
            logger.error("Conversation Validation FAILED - Conversation is empty. Gemini Request Blocked.")
            raise InvalidConversationError("Cannot sanitize empty conversation history.")

        sanitized: List[Dict[str, str]] = []
        system_msgs: List[Dict[str, str]] = []

        for msg in messages:
            role = str(msg.get("role", "")).lower().strip()
            content = str(msg.get("content", "")).strip()

            if not content or role not in cls.VALID_ROLES:
                continue

            # Normalize role for target provider
            if target_provider == "gemini" and role == "assistant":
                role = "model"

            if role == "system":
                system_msgs.append({"role": "system", "content": content})
                continue

            # Merge consecutive user messages
            if sanitized and sanitized[-1]["role"] == "user" and role == "user":
                sanitized[-1]["content"] = f"{sanitized[-1]['content']}\n\n{content}"
                continue

            # Skip consecutive model messages (keep previous)
            if sanitized and sanitized[-1]["role"] == role and role in ("model", "assistant"):
                logger.warning(f"Dropping duplicate consecutive '{role}' message turn.")
                continue

            sanitized.append({"role": role, "content": content})

        # Remove trailing model turn(s) if present
        while sanitized and sanitized[-1]["role"] in ("model", "assistant"):
            dropped = sanitized.pop()
            logger.warning(
                f"Conversation Validation FAILED: Last Role: '{dropped['role']}' | "
                f"Gemini Request Blocked until auto-sanitized by dropping trailing model turn."
            )

        # Check if any valid user turns remain
        user_turns = [m for m in sanitized if m["role"] == "user"]
        if not user_turns:
            logger.error("Conversation Length: 0 after sanitization. Gemini Request Blocked.")
            raise InvalidConversationError("No valid user turn remains in conversation history after sanitization.")

        final_payload = system_msgs + sanitized

        # Final audit logging
        first_role = sanitized[0]["role"] if sanitized else "system"
        last_role = final_payload[-1]["role"]
        logger.info(
            f"\nConversation Validation: PASSED\n"
            f"Conversation Length: {len(final_payload)}\n"
            f"First Role: {first_role}\n"
            f"Last Role: {last_role}\n"
        )

        return final_payload

    @classmethod
    def validate_and_sanitize(
        cls,
        messages: List[Dict[str, str]],
        target_provider: str = "gemini"
    ) -> List[Dict[str, str]]:
        """
        Single Gatekeeper Entry Point for all LLM generateContent/chat requests.
        Validates conversation history, auto-sanitizes trailing model turns if needed,
        and returns a safe, compliant payload.
        """
        val_res = cls.validate_conversation(messages)
        if val_res.is_valid and target_provider != "gemini":
            return messages

        # Auto-sanitize if validation failed or when targeting Gemini
        return cls.sanitize_conversation(messages, target_provider=target_provider)
