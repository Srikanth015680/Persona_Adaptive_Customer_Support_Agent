import json

import streamlit as st

from src.rag_pipeline import RAGPipeline
from src.conversation import ConversationSession
from src import llm_providers


st.set_page_config(
    page_title="CloudSuite Support Agent",
    layout="centered",
)


@st.cache_resource
def get_rag_pipeline():
    return RAGPipeline()


if "session" not in st.session_state:
    rag = get_rag_pipeline()

    st.session_state.rag_ready = rag.is_ready()
    st.session_state.session = ConversationSession(rag)
    st.session_state.turns = []


st.title(" CloudSuite Support Agent")
st.caption(
    "Persona-aware · RAG-grounded · Human-escalation-ready"
)

provider = llm_providers.active_provider()

with st.sidebar:
    st.subheader("System Status")

    st.write(
        f"**LLM/Embedding provider:** `{provider}`"
    )

    if provider == "offline":
        st.warning(
            "No API key detected. Running in offline mode."
        )

    st.write(
        f"**Vector index ready:** "
        f"{'' if st.session_state.rag_ready else ''}"
    )

    st.divider()

    st.subheader("Try an example")

    examples = [
        "Can you explain the API authentication failure and provide error details?",
        "I've tried everything and nothing works! This is the third time I'm resetting my password!",
        "How does this outage impact our operations and when will it be resolved?",
        "My billing statement has unexpected duplicate charges. I demand an immediate refund!",
        "What's the weather like in Tokyo?",
    ]

    for ex in examples:
        if st.button(
            ex,
            use_container_width=True,
            key=ex,
        ):
            st.session_state.pending_message = ex


if not st.session_state.rag_ready:
    st.error(
        "Knowledge base index not found. Run python ingest.py first."
    )
    st.stop()


for turn in st.session_state.turns:
    with st.chat_message("user"):
        st.write(turn.user_message)

    with st.chat_message("assistant"):
        badge = (
            " Escalated to human agent"
            if turn.escalated
            else " Resolved by agent"
        )

        st.markdown(
            f"**Detected persona:** "
            f"`{turn.persona}` "
            f"(confidence {turn.persona_confidence:.2f}, "
            f"method: {turn.persona_method})"
        )

        if turn.retrieved_chunks:
            sources = ", ".join(
                f"{c['source']} (score={c['score']})"
                for c in turn.retrieved_chunks
            )

            st.markdown(
                f"**Retrieved sources:** {sources}"
            )
        else:
            st.markdown(
                "**Retrieved sources:** _none_"
            )

        st.markdown(
            f"**Escalation status:** {badge}"
        )

        st.write(turn.response)

        if turn.handoff_summary:
            with st.expander(
                " Human Handoff Summary"
            ):
                st.code(
                    json.dumps(
                        turn.handoff_summary,
                        indent=2,
                    ),
                    language="json",
                )


prefill = (
    st.session_state.pop(
        "pending_message",
        None,
    )
    if "pending_message" in st.session_state
    else None
)

user_input = (
    st.chat_input(
        "Type your support question..."
    )
    or prefill
)

if user_input:
    turn = st.session_state.session.step(
        user_input
    )

    st.session_state.turns.append(turn)

    st.rerun()