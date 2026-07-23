import uuid
import structlog
from typing import Dict, Any, List, Optional
from app.domain.models import PatientProfile

logger = structlog.get_logger()

class ConversationState:
    def __init__(self, conversation_id: Optional[str] = None):
        self.conversation_id = conversation_id or f"conv-{uuid.uuid4().hex[:8]}"
        self.symptom: Optional[str] = None
        self.duration_days: Optional[int] = None
        self.max_temp_f: Optional[float] = None
        self.age: Optional[int] = None
        self.pregnancy: Optional[bool] = None
        self.active_medications: List[str] = []
        self.comorbidities: List[str] = []
        self.red_flags: List[str] = []
        self.filled_slots: List[str] = []
        self.history: List[Dict[str, str]] = []
        self.patient_profile: Optional[PatientProfile] = None

class ConversationEngine:
    """
    Physician-like history taking and stateful dialogue intake manager.
    Ensures minimum clinical context slots are satisfied before triggering RAG execution.
    """
    REQUIRED_SLOTS_FOR_SYMPTOM = ["symptom", "duration_days", "age", "pregnancy"]

    def __init__(self):
        self.active_sessions: Dict[str, ConversationState] = {}

    def get_or_create_session(self, conversation_id: Optional[str]) -> ConversationState:
        if conversation_id and conversation_id in self.active_sessions:
            return self.active_sessions[conversation_id]
        
        session = ConversationState(conversation_id)
        self.active_sessions[session.conversation_id] = session
        return session

    def process_intake(self, text: str, conversation_id: Optional[str] = None, profile: Optional[PatientProfile] = None) -> Dict[str, Any]:
        session = self.get_or_create_session(conversation_id)
        if profile:
            session.patient_profile = profile
            if profile.age and "age" not in session.filled_slots:
                session.age = profile.age
                session.filled_slots.append("age")
            if profile.pregnancy is not None and "pregnancy" not in session.filled_slots:
                session.pregnancy = profile.pregnancy
                session.filled_slots.append("pregnancy")
            if profile.active_medications:
                session.active_medications = profile.active_medications

        session.history.append({"role": "user", "content": text})
        text_lower = text.lower()

        # Slot extraction rules
        symptoms_map = ["fever", "cough", "shortness of breath", "dyspnea", "chest pain", "headache", "diarrhea", "rash", "fatigue"]
        for sym in symptoms_map:
            if sym in text_lower and "symptom" not in session.filled_slots:
                session.symptom = sym
                session.filled_slots.append("symptom")
                break

        # Check pending slots
        pending = [s for s in self.REQUIRED_SLOTS_FOR_SYMPTOM if s not in session.filled_slots]

        if pending and session.symptom:
            next_question = self._generate_clarification_question(pending[0], session.symptom)
            logger.info("conversation_slot_filling_in_progress", conversation_id=session.conversation_id, pending=pending)
            return {
                "conversation_id": session.conversation_id,
                "status": "NEED_CLARIFICATION",
                "next_question": next_question,
                "filled_slots": session.filled_slots,
                "pending_slots": pending,
                "ready_for_rag": False
            }

        return {
            "conversation_id": session.conversation_id,
            "status": "READY",
            "filled_slots": session.filled_slots,
            "pending_slots": [],
            "ready_for_rag": True,
            "session": session
        }

    def _generate_clarification_question(self, slot: str, symptom: str) -> str:
        questions = {
            "duration_days": f"How many days has the {symptom} been present?",
            "age": f"What is the age of the patient experiencing {symptom}?",
            "pregnancy": f"Is the patient currently pregnant or breastfeeding?",
        }
        return questions.get(slot, f"Could you provide additional clinical context regarding the {symptom}?")
