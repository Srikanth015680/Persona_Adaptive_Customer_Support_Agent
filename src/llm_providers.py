import logging
from typing import Optional

from . import config

logger = logging.getLogger(__name__)

_OFFLINE_SENTINEL = "__OFFLINE_FALLBACK__"


def active_provider() -> str:
    providers = {
        "anthropic": config.ANTHROPIC_API_KEY,
        "openai": config.OPENAI_API_KEY,
        "gemini": config.GEMINI_API_KEY,
    }

    for provider in config.PROVIDER_PRIORITY:
        if providers.get(provider):
            return provider

    return "offline"


def chat(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.2,
    max_tokens: int = 700,
    json_mode: bool = False,
) -> str:

    provider = active_provider()

    try:
        if provider == "anthropic":
            return _chat_anthropic(
                system_prompt,
                user_message,
                temperature,
                max_tokens,
            )

        if provider == "openai":
            return _chat_openai(
                system_prompt,
                user_message,
                temperature,
                max_tokens,
                json_mode,
            )

        if provider == "gemini":
            return _chat_gemini(
                system_prompt,
                user_message,
                temperature,
                max_tokens,
                json_mode,
            )

    except Exception as exc:
        logger.warning(
            "LLM call to %s failed (%s); falling back to offline mode.",
            provider,
            exc,
        )

    return _OFFLINE_SENTINEL


def _chat_anthropic(
    system_prompt: str,
    user_message: str,
    temperature: float,
    max_tokens: int,
) -> str:

    import anthropic

    client = anthropic.Anthropic(
        api_key=config.ANTHROPIC_API_KEY
    )

    resp = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": user_message,
            }
        ],
    )

    return "".join(
        block.text
        for block in resp.content
        if block.type == "text"
    )


def _chat_openai(
    system_prompt: str,
    user_message: str,
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> str:

    from openai import OpenAI

    client = OpenAI(
        api_key=config.OPENAI_API_KEY
    )

    kwargs = {}

    if json_mode:
        kwargs["response_format"] = {
            "type": "json_object"
        }

    resp = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        **kwargs,
    )

    return resp.choices[0].message.content


def _chat_gemini(
    system_prompt: str,
    user_message: str,
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> str:

    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=config.GEMINI_API_KEY
    )

    gen_config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
        max_output_tokens=max_tokens,
        response_mime_type=(
            "application/json"
            if json_mode
            else "text/plain"
        ),
    )

    resp = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=user_message,
        config=gen_config,
    )

    return resp.text


def embed(text: str) -> Optional[list]:

    provider = active_provider()

    try:
        if provider == "anthropic":
            if config.OPENAI_API_KEY:
                return _embed_openai(text)

            if config.GEMINI_API_KEY:
                return _embed_gemini(text)

            return None

        if provider == "openai":
            return _embed_openai(text)

        if provider == "gemini":
            return _embed_gemini(text)

    except Exception as exc:
        logger.warning(
            "Embedding call to %s failed (%s); falling back to offline embedder.",
            provider,
            exc,
        )

    return None


def _embed_openai(text: str) -> list:

    from openai import OpenAI

    client = OpenAI(
        api_key=config.OPENAI_API_KEY
    )

    resp = client.embeddings.create(
        model=config.OPENAI_EMBED_MODEL,
        input=text,
    )

    return resp.data[0].embedding


def _embed_gemini(text: str) -> list:

    from google import genai

    client = genai.Client(
        api_key=config.GEMINI_API_KEY
    )

    resp = client.models.embed_content(
        model=config.GEMINI_EMBED_MODEL,
        contents=text,
    )

    return resp.embeddings[0].values