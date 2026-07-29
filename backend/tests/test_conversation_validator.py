"""
Unit and Integration Test Suite for MedRef Conversation Validation Layer.
Verifies that all valid conversation structures pass, invalid/interrupted structures
(including trailing model turns that trigger HTTP 400 in Gemini) are correctly identified and sanitized,
and no invalid request can ever reach Gemini or downstream LLM providers.
"""

import pytest
from app.infrastructure.conversation_validator import (
    ConversationValidator,
    ValidationResult,
    InvalidConversationError
)
from app.infrastructure.llm_providers import GroqProvider, GeminiProvider


class TestConversationValidatorUnit:
    """Unit tests for conversation turn structure validation."""

    def test_single_user_turn_valid(self):
        conv = [{"role": "user", "content": "What are the indications for Empagliflozin?"}]
        res = ConversationValidator.validate_conversation(conv)
        assert res.is_valid is True
        assert res.messages_count == 1
        assert res.first_role == "user"
        assert res.last_role == "user"

    def test_user_model_user_valid(self):
        conv = [
            {"role": "user", "content": "Patient is taking Metformin 1000mg."},
            {"role": "model", "content": "Metformin is safe at current eGFR 60."},
            {"role": "user", "content": "What if eGFR drops to 25?"}
        ]
        res = ConversationValidator.validate_conversation(conv)
        assert res.is_valid is True
        assert res.messages_count == 3
        assert res.first_role == "user"
        assert res.last_role == "user"

    def test_user_model_user_model_user_valid(self):
        conv = [
            {"role": "user", "content": "Check Digoxin dosing."},
            {"role": "model", "content": "Digoxin standard dose is 0.125mg daily."},
            {"role": "user", "content": "Patient added Amiodarone."},
            {"role": "model", "content": "Reduce Digoxin dose by 50%."},
            {"role": "user", "content": "What is target trough level?"}
        ]
        res = ConversationValidator.validate_conversation(conv)
        assert res.is_valid is True
        assert res.messages_count == 5

    def test_reject_trailing_model_turn(self):
        conv = [
            {"role": "user", "content": "Evaluate Warfarin INR."},
            {"role": "model", "content": "Target INR is 2.0-3.0."}
        ]
        res = ConversationValidator.validate_conversation(conv)
        assert res.is_valid is False
        assert "Conversation ends with model turn" in res.reason
        assert res.last_role == "model"

    def test_reject_standalone_model_turn(self):
        conv = [{"role": "model", "content": "Hello, I am MedRef."}]
        res = ConversationValidator.validate_conversation(conv)
        assert res.is_valid is False
        assert res.last_role == "model"

    def test_reject_empty_conversation(self):
        res = ConversationValidator.validate_conversation([])
        assert res.is_valid is False
        assert res.messages_count == 0

    def test_reject_invalid_role(self):
        conv = [{"role": "admin", "content": "Execute test."}]
        res = ConversationValidator.validate_conversation(conv)
        assert res.is_valid is False
        assert "Invalid role 'admin'" in res.reason

    def test_reject_empty_content(self):
        conv = [{"role": "user", "content": "   "}]
        res = ConversationValidator.validate_conversation(conv)
        assert res.is_valid is False
        assert "Empty content" in res.reason

    def test_reject_consecutive_model_turns(self):
        conv = [
            {"role": "user", "content": "Check Spironolactone."},
            {"role": "model", "content": "Spironolactone is an MRA."},
            {"role": "model", "content": "Monitor potassium levels."},
            {"role": "user", "content": "What is the dose?"}
        ]
        res = ConversationValidator.validate_conversation(conv)
        assert res.is_valid is False
        assert "Consecutive same-role turns detected" in res.reason

    def test_reject_consecutive_user_turns(self):
        conv = [
            {"role": "user", "content": "Patient has eGFR 22."},
            {"role": "user", "content": "Patient is taking Metformin."}
        ]
        res = ConversationValidator.validate_conversation(conv)
        assert res.is_valid is False
        assert "Consecutive same-role turns detected" in res.reason


class TestConversationSanitizerUnit:
    """Unit tests for automatic conversation sanitization & recovery."""

    def test_sanitize_trailing_model_turn_popped(self):
        conv = [
            {"role": "user", "content": "Check Sacubitril/Valsartan."},
            {"role": "model", "content": "Requires 36-hour ACEi washout."}
        ]
        sanitized = ConversationValidator.sanitize_conversation(conv)
        assert len(sanitized) == 1
        assert sanitized[-1]["role"] == "user"
        assert sanitized[-1]["content"] == "Check Sacubitril/Valsartan."

    def test_sanitize_consecutive_user_turns_merged(self):
        conv = [
            {"role": "user", "content": "Patient has eGFR 22."},
            {"role": "user", "content": "Patient is taking Metformin."}
        ]
        sanitized = ConversationValidator.sanitize_conversation(conv)
        assert len(sanitized) == 1
        assert sanitized[0]["role"] == "user"
        assert "Patient has eGFR 22." in sanitized[0]["content"]
        assert "Patient is taking Metformin." in sanitized[0]["content"]

    def test_sanitize_consecutive_model_turns_deduped(self):
        conv = [
            {"role": "user", "content": "Check Atorvastatin interaction."},
            {"role": "model", "content": "First response."},
            {"role": "model", "content": "Clarithromycin inhibits CYP3A4."},
            {"role": "user", "content": "Should statin be held?"}
        ]
        sanitized = ConversationValidator.sanitize_conversation(conv)
        assert len(sanitized) == 3
        assert sanitized[0]["role"] == "user"
        assert sanitized[1]["role"] == "model"
        assert sanitized[1]["content"] == "First response."
        assert sanitized[2]["role"] == "user"

    def test_sanitize_empty_raises_error(self):
        with pytest.raises(InvalidConversationError):
            ConversationValidator.sanitize_conversation([])


class TestConversationValidatorIntegration:
    """Integration tests for restored sessions, cached history, and provider gatekeeping."""

    def test_restored_interrupted_session_recovery(self):
        # Simulates a session interrupted mid-stream where the last turn in DB is a partial model response
        restored_history = [
            {"role": "user", "content": "First query: Spironolactone dosing."},
            {"role": "model", "content": "Spironolactone is indicated for HFrEF."},
            {"role": "user", "content": "Second query: Patient K+ is 5.8."},
            {"role": "model", "content": "Partial response... [Connection Interrupted]"}
        ]
        # Gatekeeper cleans trailing interrupted model turn before dispatching new query
        safe_payload = ConversationValidator.validate_and_sanitize(restored_history, target_provider="gemini")
        assert safe_payload[-1]["role"] == "user"
        assert safe_payload[-1]["content"] == "Second query: Patient K+ is 5.8."

    def test_cached_history_sanitization(self):
        # Cached session replayed from Redis/Postgres containing assistant roles
        cached_session = [
            {"role": "system", "content": "System prompt."},
            {"role": "user", "content": "Check Clarithromycin + Warfarin."},
            {"role": "assistant", "content": "CYP2C9 inhibition increases INR."},
            {"role": "user", "content": "What is the INR target?"}
        ]
        sanitized = ConversationValidator.validate_and_sanitize(cached_session, target_provider="gemini")
        val_res = ConversationValidator.validate_conversation(sanitized)
        assert val_res.is_valid is True
        assert val_res.last_role == "user"

    def test_gatekeeper_blocks_invalid_gemini_request(self):
        # Simulates passing a payload ending with a model turn directly to validator
        invalid_gemini_history = [
            {"role": "user", "content": "Hi"},
            {"role": "model", "content": "Hello"}
        ]
        sanitized = ConversationValidator.validate_and_sanitize(invalid_gemini_history, target_provider="gemini")
        # Trailing model turn is auto-popped so final turn is 'user'
        assert sanitized[-1]["role"] == "user"
