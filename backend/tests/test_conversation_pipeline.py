"""
Unit and Integration Test Suite for ConversationPipeline.
Tests multi-stage conversation preprocessing: Provider Adapters, Dropped Message Preserver,
Token Budget Manager / Context Summarization, and Telemetry Logging.
"""

import pytest
from app.infrastructure.conversation_pipeline import (
    ConversationPipeline,
    PipelineResult,
    InvalidConversationError,
    ProviderAdapter,
    TokenBudgetManager
)


class TestConversationPipelineUnit:
    """Unit tests for ConversationPipeline architecture."""

    def test_pipeline_valid_user_turn(self):
        conv = [{"role": "user", "content": "What are the indications for Empagliflozin?"}]
        res = ConversationPipeline.process(conv, provider="gemini")
        assert res.is_valid is True
        assert res.telemetry.validation_status == "PASSED"
        assert res.telemetry.repaired is False
        assert len(res.processed_messages) == 1

    def test_pipeline_drops_and_preserves_trailing_model_turn(self):
        conv = [
            {"role": "user", "content": "Evaluate Warfarin INR."},
            {"role": "model", "content": "Target INR is 2.0-3.0."}
        ]
        res = ConversationPipeline.process(conv, provider="gemini", session_id="test_session_101")
        assert res.is_valid is True
        assert res.telemetry.validation_status == "FAILED_REPAIRED"
        assert res.telemetry.repaired is True
        assert res.telemetry.repair_reason == "Gemini API requires user-ending conversation"
        assert res.telemetry.dropped_messages_count == 1
        assert len(res.telemetry.dropped_records) == 1
        record = res.telemetry.dropped_records[0]
        assert record.role == "model"
        assert "Target INR" in record.content_snippet
        assert record.reason == "Gemini API requires user-ending conversation"

    def test_pipeline_provider_adapter_groq(self):
        conv = [
            {"role": "system", "content": "System directive."},
            {"role": "user", "content": "Query 1"},
            {"role": "model", "content": "Response 1"},
            {"role": "user", "content": "Query 2"}
        ]
        res = ConversationPipeline.process(conv, provider="groq")
        assert res.is_valid is True
        # Groq adapter normalizes 'model' -> 'assistant'
        roles = [m["role"] for m in res.processed_messages]
        assert roles == ["system", "user", "assistant", "user"]

    def test_pipeline_token_budget_manager_summarization(self):
        conv = []
        for i in range(30):
            conv.append({"role": "user", "content": f"User prompt {i}"})
            conv.append({"role": "model", "content": f"Model answer {i}"})
        conv.append({"role": "user", "content": "Final query"})

        res = ConversationPipeline.process(conv, provider="gemini", max_turns=10)
        assert res.is_valid is True
        assert len(res.processed_messages) <= 10
        # Check that older context was summarized
        has_summary = any("Prior Conversation Summary" in m["content"] for m in res.processed_messages)
        assert has_summary is True

    def test_telemetry_to_dict_serialization(self):
        conv = [
            {"role": "user", "content": "Check Spironolactone."},
            {"role": "model", "content": "Spironolactone is an MRA."}
        ]
        res = ConversationPipeline.process(conv, provider="gemini", session_id="sess_abc")
        telemetry_dict = res.telemetry.to_dict()
        assert telemetry_dict["session_id"] == "sess_abc"
        assert telemetry_dict["provider"] == "gemini"
        assert telemetry_dict["repaired"] is True
        assert telemetry_dict["dropped_messages_count"] == 1
        assert len(telemetry_dict["dropped_records"]) == 1
