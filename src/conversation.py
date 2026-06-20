"""
Conversation orchestration for:
Persona Detection
 RAG Retrieval
 Response Generation
 Escalation & Human Handoff
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from . import classifier
from . import generator
from . import escalator
from . import config
from .rag_pipeline import RAGPipeline


@dataclass
class TurnResult:
    user_message: str
    persona: str
    persona_confidence: float
    persona_method: str
    retrieved_chunks: List[Dict[str, Any]]
    escalated: bool
    escalation_reasons: List[str]
    response: str
    handoff_summary: Optional[Dict[str, Any]] = None


class ConversationSession:
    def __init__(self, rag: RAGPipeline, cfg: config.AppConfig = config.CONFIG):
        self.rag = rag
        self.cfg = cfg
        self.history: List[Dict[str, str]] = []
        self.attempted_steps: List[str] = []
        self.consecutive_unresolved_turns = 0

    def step(self, user_message: str) -> TurnResult:
        # 1. Persona detection
        persona_result = classifier.classify_persona(user_message)

        # 2. Retrieval
        retrieved = self.rag.retrieve(user_message, top_k=self.cfg.top_k)

        # 3. Escalation check (uses retrieval confidence + sensitive keywords +
        #    repeated-frustration counter accumulated across turns)
        decision = escalator.check_escalation(
            user_message=user_message,
            retrieved_chunks=retrieved,
            persona=persona_result.persona,
            consecutive_unresolved_turns=self.consecutive_unresolved_turns,
            cfg=self.cfg,
        )

        handoff_summary = None
        if decision.escalated:
            response = self._escalation_message(decision.reasons)
            handoff_summary = escalator.build_handoff_summary(
                persona=persona_result.persona,
                user_message=user_message,
                conversation_history=self.history + [{"role": "user", "content": user_message}],
                retrieved_chunks=retrieved,
                attempted_steps=self.attempted_steps,
                escalation_reasons=decision.reasons,
            )
        else:
            response = generator.generate_response(user_message, persona_result.persona, retrieved)
            # Track this resolution attempt for future handoff context.
            if retrieved:
                self.attempted_steps.append(f"Suggested guidance from {retrieved[0]['source']}")

        # Track frustration persistence across turns for the repeated-frustration trigger.
        if decision.escalated:
             self.consecutive_unresolved_turns = 0
        elif persona_result.persona == "Frustrated User":
            self.consecutive_unresolved_turns += 1
        else:
            self.consecutive_unresolved_turns = 0

        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": response})

        return TurnResult(
            user_message=user_message,
            persona=persona_result.persona,
            persona_confidence=persona_result.confidence,
            persona_method=persona_result.method,
            retrieved_chunks=retrieved,
            escalated=decision.escalated,
            escalation_reasons=decision.reasons,
            response=response,
            handoff_summary=handoff_summary,
        )

    @staticmethod
    def _escalation_message(reasons: List[str]) -> str:
        return (
            "I want to make sure this gets handled correctly, so I'm escalating this conversation "
            "to a human support specialist who can assist further. A structured summary of our "
            "conversation has been prepared for them so you won't need to repeat anything."
        )
