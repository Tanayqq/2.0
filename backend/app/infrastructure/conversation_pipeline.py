"""
MedRef Conversation Pipeline Architecture
Extensible multi-stage preprocessing pipeline for all LLM backends (Gemini, Groq, OpenAI, MedGemma).

Stages:
 1. Schema & Role Validator
 2. Role Normalizer & Duplicate Merger
 3. Token Budget Manager & Context Summarizer
 4. Provider-Specific Adapter (Gemini, Groq, OpenAI)
 5. Repair Engine & Dropped Message Preserver
 6. Structured Telemetry & Audit Logger
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
import datetime
import logging
import json

logger = logging.getLogger("medref.conversation_pipeline")


class InvalidConversationError(ValueError):
    """Raised when a conversation structure fails validation and cannot be repaired."""
    pass


@dataclass
class DroppedMessageRecord:
    timestamp: str
    reason: str
    role: str
    content_snippet: str
    original_index: int


@dataclass
class PipelineTelemetry:
    session_id: Optional[str]
    provider: str
    original_length: int
    final_length: int
    validation_status: str  # PASSED or FAILED_REPAIRED
    repaired: bool
    repair_reason: Optional[str]
    dropped_messages_count: int
    dropped_records: List[DroppedMessageRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "provider": self.provider,
            "original_length": self.original_length,
            "final_length": self.final_length,
            "validation_status": self.validation_status,
            "repaired": self.repaired,
            "repair_reason": self.repair_reason,
            "dropped_messages_count": self.dropped_messages_count,
            "dropped_records": [
                {
                    "timestamp": r.timestamp,
                    "reason": r.reason,
                    "role": r.role,
                    "snippet": r.content_snippet,
                    "index": r.original_index
                }
                for r in self.dropped_records
            ]
        }


@dataclass
class PipelineResult:
    is_valid: bool
    processed_messages: List[Dict[str, str]]
    telemetry: PipelineTelemetry


class ProviderAdapter:
    """Provider-specific role normalization and validation rules."""

    @staticmethod
    def adapt(
        messages: List[Dict[str, str]],
        provider: str
    ) -> Tuple[List[Dict[str, str]], List[DroppedMessageRecord], Optional[str]]:
        provider = provider.lower()
        adapted: List[Dict[str, str]] = []
        dropped: List[DroppedMessageRecord] = []
        repair_reason = None

        if provider == "gemini":
            # Gemini Rules:
            # - Roles must be 'user' or 'model' (system allowed as system_instruction or mapped)
            # - Strictly MUST END WITH 'user' turn
            # - No consecutive model turns
            system_msgs = []
            conv_turns = []

            for idx, m in enumerate(messages):
                role = m.get("role", "").lower()
                content = m.get("content", "").strip()

                if role == "system":
                    system_msgs.append({"role": "system", "content": content})
                elif role in ("assistant", "model"):
                    conv_turns.append({"role": "model", "content": content, "orig_idx": idx})
                else:
                    conv_turns.append({"role": "user", "content": content, "orig_idx": idx})

            # Check if trailing turn is model
            while conv_turns and conv_turns[-1]["role"] == "model":
                dropped_msg = conv_turns.pop()
                repair_reason = "Gemini API requires user-ending conversation"
                dropped.append(DroppedMessageRecord(
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    reason=repair_reason,
                    role=dropped_msg["role"],
                    content_snippet=dropped_msg["content"][:100],
                    original_index=dropped_msg.get("orig_idx", -1)
                ))
                logger.warning(
                    f"Conversation Repaired: Dropped trailing model turn. "
                    f"Reason: {repair_reason} | Role: {dropped_msg['role']}"
                )

            # Reconstruct
            for m in conv_turns:
                adapted.append({"role": m["role"], "content": m["content"]})
            adapted = system_msgs + adapted

        elif provider in ("groq", "openai", "medgemma"):
            # Groq / OpenAI Rules:
            # - Roles: system, user, assistant
            for idx, m in enumerate(messages):
                role = m.get("role", "").lower()
                content = m.get("content", "").strip()
                norm_role = "assistant" if role == "model" else role
                adapted.append({"role": norm_role, "content": content})

        else:
            adapted = messages

        return adapted, dropped, repair_reason


class TokenBudgetManager:
    """Manages conversation length and auto-summarizes over-budget contexts."""

    MAX_TURNS = 50

    @classmethod
    def apply_budget(
        cls,
        messages: List[Dict[str, str]],
        max_turns: int = MAX_TURNS
    ) -> List[Dict[str, str]]:
        if len(messages) <= max_turns:
            return messages

        logger.warning(
            f"Conversation turn count ({len(messages)}) exceeds max limit ({max_turns}). "
            f"Applying budget summarization..."
        )

        system_msgs = [m for m in messages if m.get("role", "").lower() == "system"]
        conv_turns = [m for m in messages if m.get("role", "").lower() != "system"]

        if len(conv_turns) <= max_turns:
            return messages

        # Preserve recent N turns, summarize older turns
        num_preserve = max_turns - 2
        older_turns = conv_turns[:-num_preserve]
        recent_turns = conv_turns[-num_preserve:]

        summary_text = "Prior Conversation Summary: " + " | ".join(
            f"{t['role'].upper()}: {t['content'][:80]}..." for t in older_turns
        )

        summarized_turn = {"role": "user", "content": summary_text}
        return system_msgs + [summarized_turn] + recent_turns


class ConversationPipeline:
    """
    Unified Preprocessing Pipeline for all LLM backends.
    """

    VALID_ROLES = {"user", "model", "assistant", "system"}

    @classmethod
    def process(
        cls,
        messages: List[Dict[str, str]],
        provider: str = "gemini",
        session_id: Optional[str] = None,
        max_turns: int = 50
    ) -> PipelineResult:
        """
        Executes the complete multi-stage conversation preprocessing pipeline.
        """
        orig_len = len(messages) if isinstance(messages, list) else 0

        # Stage 1: Schema & Role Validator
        if not messages or not isinstance(messages, list):
            telemetry = PipelineTelemetry(
                session_id=session_id,
                provider=provider,
                original_length=0,
                final_length=0,
                validation_status="FAILED",
                repaired=False,
                repair_reason="Empty conversation payload.",
                dropped_messages_count=0
            )
            logger.error(f"Conversation Pipeline Error: Empty conversation history for session {session_id}.")
            raise InvalidConversationError("Conversation history is empty.")

        # Stage 2: Normalization & Duplicate Merging
        normalized: List[Dict[str, str]] = []
        dropped_records: List[DroppedMessageRecord] = []

        for idx, m in enumerate(messages):
            role = str(m.get("role", "")).lower().strip()
            content = str(m.get("content", "")).strip()

            if not content or role not in cls.VALID_ROLES:
                dropped_records.append(DroppedMessageRecord(
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    reason="Invalid role or empty content",
                    role=role,
                    content_snippet=content[:50],
                    original_index=idx
                ))
                continue

            # Consecutive User Merge
            if normalized and normalized[-1]["role"] == "user" and role == "user":
                normalized[-1]["content"] = f"{normalized[-1]['content']}\n\n{content}"
                logger.info(f"Merged consecutive user turns at index {idx}.")
                continue

            # Consecutive Model Deduplication
            if normalized and normalized[-1]["role"] in ("model", "assistant") and role in ("model", "assistant"):
                dropped_records.append(DroppedMessageRecord(
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    reason="Duplicate consecutive model turn",
                    role=role,
                    content_snippet=content[:50],
                    original_index=idx
                ))
                logger.info(f"Deduplicated consecutive model turn at index {idx}.")
                continue

            normalized.append({"role": role, "content": content})

        # Stage 3: Token Budget Manager
        budgeted = TokenBudgetManager.apply_budget(normalized, max_turns=max_turns)

        # Stage 4 & 5: Provider-Specific Adapter & Repair Engine
        adapted, provider_dropped, repair_reason = ProviderAdapter.adapt(budgeted, provider=provider)
        dropped_records.extend(provider_dropped)

        # Ensure at least one valid user turn exists
        user_turns = [m for m in adapted if m["role"] == "user"]
        if not user_turns:
            telemetry = PipelineTelemetry(
                session_id=session_id,
                provider=provider,
                original_length=orig_len,
                final_length=0,
                validation_status="FAILED",
                repaired=bool(dropped_records),
                repair_reason="No user turn remaining after adaptation",
                dropped_messages_count=len(dropped_records),
                dropped_records=dropped_records
            )
            logger.error(f"Conversation Pipeline Error: No user turn remaining for session {session_id}.")
            raise InvalidConversationError("No valid user turn remains in conversation history.")

        repaired = len(dropped_records) > 0
        status = "FAILED_REPAIRED" if repaired else "PASSED"

        telemetry = PipelineTelemetry(
            session_id=session_id,
            provider=provider,
            original_length=orig_len,
            final_length=len(adapted),
            validation_status=status,
            repaired=repaired,
            repair_reason=repair_reason or ("Sanitized invalid turns" if repaired else None),
            dropped_messages_count=len(dropped_records),
            dropped_records=dropped_records
        )

        # Stage 6: Structured Telemetry Audit Log
        logger.info(
            f"Conversation Validation Audit: {json.dumps(telemetry.to_dict(), indent=2)}"
        )

        return PipelineResult(
            is_valid=True,
            processed_messages=adapted,
            telemetry=telemetry
        )


# Backward Compatibility Alias
class ConversationValidator:
    @classmethod
    def validate_conversation(cls, messages: List[Dict[str, str]]):
        try:
            res = ConversationPipeline.process(messages, provider="gemini")
            from app.infrastructure.conversation_validator import ValidationResult
            return ValidationResult(
                is_valid=not res.telemetry.repaired,
                reason=res.telemetry.repair_reason or "Valid",
                messages_count=res.telemetry.final_length,
                first_role=res.processed_messages[0]["role"] if res.processed_messages else None,
                last_role=res.processed_messages[-1]["role"] if res.processed_messages else None,
                sanitized_messages=res.processed_messages
            )
        except Exception as e:
            from app.infrastructure.conversation_validator import ValidationResult
            return ValidationResult(
                is_valid=False,
                reason=str(e),
                messages_count=0,
                first_role=None,
                last_role=None,
                sanitized_messages=[]
            )

    @classmethod
    def validate_and_sanitize(cls, messages: List[Dict[str, str]], target_provider: str = "gemini"):
        res = ConversationPipeline.process(messages, provider=target_provider)
        return res.processed_messages
