"""
Centralised configuration for the Persona-Adaptive Customer Support Agent.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

# Provider Configuration

PROVIDER_PRIORITY = ["gemini", "anthropic", "openai"]
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

ANTHROPIC_MODEL = os.environ.get(
    "ANTHROPIC_MODEL",
    "claude-sonnet-4-6"
)

OPENAI_MODEL = os.environ.get(
    "OPENAI_MODEL",
    "gpt-4o-mini"
)

GEMINI_MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

GEMINI_EMBED_MODEL = os.environ.get(
    "GEMINI_EMBED_MODEL",
    "gemini-embedding-001"
)

OPENAI_EMBED_MODEL = os.environ.get(
    "OPENAI_EMBED_MODEL",
    "text-embedding-3-small"
)


# RAG Configuration


CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", 60))
TOP_K = int(os.environ.get("TOP_K", 3))

COLLECTION_NAME = "support_kb"


# Escalation Configuration

RETRIEVAL_CONFIDENCE_THRESHOLD = float(
    os.environ.get("RETRIEVAL_CONFIDENCE_THRESHOLD", 0.32)
)

MAX_UNRESOLVED_TURNS = int(
    os.environ.get("MAX_UNRESOLVED_TURNS", 2)
)

SENSITIVE_KEYWORDS = [
    "refund",
    "chargeback",
    "dispute",
    "duplicate charge",
    "unauthorized charge",
    "fraud",
    "lawsuit",
    "legal",
    "sue",
    "attorney",
    "gdpr",
    "data deletion request",
    "delete my account",
    "delete my data",
    "cancel my contract",
    "breach",
    "lawyer",
    "subpoena",
    "compliance violation",
    "data leak",
    "hacked",
    "account takeover",
    "stolen",
    "unauthorized access",
]

FRUSTRATION_KEYWORDS = [
    "nothing works",
    "still not working",
    "still broken",
    "again",
    "ridiculous",
    "unacceptable",
    "worst",
    "furious",
    "fed up",
    "done with this",
    "cancel everything",
    "speak to a human",
    "speak to a manager",
    "real person",
    "actual human",
]

PERSONAS = [
    "Technical Expert",
    "Frustrated User",
    "Business Executive",
]

DEFAULT_PERSONA = "Frustrated User"


@dataclass
class AppConfig:
    chunk_size: int = CHUNK_SIZE
    chunk_overlap: int = CHUNK_OVERLAP
    top_k: int = TOP_K
    retrieval_confidence_threshold: float = RETRIEVAL_CONFIDENCE_THRESHOLD
    max_unresolved_turns: int = MAX_UNRESOLVED_TURNS
    sensitive_keywords: list = field(
        default_factory=lambda: list(SENSITIVE_KEYWORDS)
    )
    frustration_keywords: list = field(
        default_factory=lambda: list(FRUSTRATION_KEYWORDS)
    )


CONFIG = AppConfig()