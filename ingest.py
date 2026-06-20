

import logging
import sys

from src.rag_pipeline import RAGPipeline
from src import llm_providers

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)


def main():
    provider = llm_providers.active_provider()

    print(
        f"Active embedding/LLM provider: {provider}"
    )

    rag = RAGPipeline()

    print("Ingesting knowledge base from ./data ...")

    n_chunks = rag.ingest(rebuild=True)

    print(
        f"Done. Indexed {n_chunks} chunks "
        f"into ChromaDB at ./chroma_db "
        f"(collection: support_kb)."
    )


if __name__ == "__main__":
    sys.exit(main())