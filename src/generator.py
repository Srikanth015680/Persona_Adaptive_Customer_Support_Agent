from typing import List, Dict, Any

from . import llm_providers


PERSONA_INSTRUCTIONS = {
    "Technical Expert": (
        "You are a Senior Support Engineer speaking to a technically sophisticated user. "
        "Be precise and detailed. Include relevant configuration values, error codes, "
        "API endpoints, and troubleshooting steps."
    ),
    "Frustrated User": (
        "You are an empathetic customer support specialist. "
        "Acknowledge the user's frustration briefly, then provide simple, clear steps "
        "to resolve the issue."
    ),
    "Business Executive": (
        "You are a client relations manager. "
        "Keep responses concise, outcome-focused, and avoid unnecessary technical details."
    ),
}


GROUNDING_RULES = (
    "CRITICAL RULES:\n"
    "- Use only the information provided in the context.\n"
    "- Do not invent facts, policies, numbers, or troubleshooting steps.\n"
    "- If the context does not fully answer the question, say so.\n"
    "- Keep the answer concise and relevant.\n"
)


def generate_response(
    user_query: str,
    persona: str,
    context_chunks: List[Dict[str, Any]],
) -> str:

    if not context_chunks:
        return None

    if llm_providers.active_provider() == "offline":
        return _extractive_fallback(
            user_query,
            persona,
            context_chunks,
        )

    persona_prompt = PERSONA_INSTRUCTIONS.get(
        persona,
        PERSONA_INSTRUCTIONS["Frustrated User"],
    )

    context_text = "\n\n".join(
        f"Source [{c['source']}"
        f"{' - ' + c['section'] if c.get('section') else ''}]: "
        f"{c['text']}"
        for c in context_chunks
    )

    system_prompt = (
        f"{persona_prompt}\n\n"
        f"{GROUNDING_RULES}\n\n"
        f"FACTUAL CONTEXT:\n{context_text}"
    )

    raw = llm_providers.chat(
        system_prompt,
        user_query,
        temperature=0.2,
        max_tokens=600,
    )

    if raw == llm_providers._OFFLINE_SENTINEL:
        return _extractive_fallback(
            user_query,
            persona,
            context_chunks,
        )

    return raw.strip()


def _extractive_fallback(
    user_query: str,
    persona: str,
    context_chunks: List[Dict[str, Any]],
) -> str:

    top = context_chunks[0]

    sources = ", ".join(
        sorted({c["source"] for c in context_chunks})
    )

    lines = [
        line.strip("-* ").strip()
        for line in top["text"].splitlines()
        if line.strip()
    ]

    key_lines = [
        line
        for line in lines
        if len(line) > 15
    ][:5]

    if not key_lines:
        key_lines = [top["text"][:400]]

    if persona == "Technical Expert":
        header = "Here is the relevant documentation:"
        body = "\n".join(
            f"- {line}"
            for line in key_lines
        )
        footer = (
            f"\n\n(Source: {sources}, "
            f"section: {top.get('section', 'General')})"
        )

    elif persona == "Frustrated User":
        header = (
            "I understand this is frustrating. "
            "Here are the recommended steps:"
        )

        body = "\n".join(
            f"{i + 1}. {line}"
            for i, line in enumerate(key_lines)
        )

        footer = (
            f"\n\nThis guidance comes from "
            f"{sources}."
        )

    else:
        header = "Summary:"

        body = (
            key_lines[0]
            if key_lines
            else top["text"][:200]
        )

        footer = f"\n\n(Reference: {sources})"

    return f"{header}\n{body}{footer}"