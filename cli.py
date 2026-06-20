

import json
import sys

from src.rag_pipeline import RAGPipeline
from src.conversation import ConversationSession
from src import llm_providers

DIVIDER = "-" * 70


def banner():
    provider = llm_providers.active_provider()

    print(DIVIDER)
    print(" Persona-Adaptive Customer Support Agent (CLI)")
    print(f" LLM/Embedding Provider: {provider}")

    if provider == "offline":
        print(" Running in offline mode")

    print(" Type 'exit' or 'quit' to leave")
    print(DIVIDER)


def print_turn(turn):
    print(
        f"\n[Detected Persona]   {turn.persona} "
        f"(confidence: {turn.persona_confidence:.2f}, "
        f"method: {turn.persona_method})"
    )

    if turn.retrieved_chunks:
        sources = ", ".join(
            f"{c['source']} (score={c['score']})"
            for c in turn.retrieved_chunks
        )

        print(f"[Retrieved Sources]  {sources}")
    else:
        print("[Retrieved Sources]  (none)")

    print(
        f"[Escalation Status]  "
        f"{'ESCALATED' if turn.escalated else 'Resolved by agent'}"
    )

    if turn.escalated:
        print(
            "[Escalation Reasons] "
            + "; ".join(turn.escalation_reasons)
        )

    print(f"\nAgent: {turn.response}\n")

    if turn.handoff_summary:
        print("[Human Handoff Summary JSON]")
        print(
            json.dumps(
                turn.handoff_summary,
                indent=2,
            )
        )

    print(DIVIDER)


def main():
    rag = RAGPipeline()

    if not rag.is_ready():
        print(
            "Vector index is empty. "
            "Run `python ingest.py` first."
        )
        sys.exit(1)

    session = ConversationSession(rag)

    banner()

    while True:
        try:
            user_message = input("You: ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_message:
            continue

        if user_message.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        turn = session.step(user_message)

        print_turn(turn)


if __name__ == "__main__":
    main()