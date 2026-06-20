Project Overview

This project is a Persona-Adaptive Customer Support Agent that automatically adjusts its responses based on the type of customer interacting with the system.

The goal is to provide more effective and personalized support by understanding how different users communicate. Before generating a response, the system identifies the customer's persona and adapts both the tone and level of detail accordingly.

The application supports three customer personas:

Technical Expert

Frustrated User

Business Executive

To ensure responses remain accurate and grounded, the system uses a Retrieval-Augmented Generation (RAG) pipeline. User queries are matched against a support knowledge base, and relevant document chunks are retrieved from a ChromaDB vector database. The retrieved information is then used as context for response generation, helping reduce hallucinations and improve factual accuracy.

The agent also includes a configurable escalation workflow. Conversations are escalated to a human support representative when relevant information cannot be found, retrieval confidence is low, sensitive topics are detected, or the issue cannot be resolved through the available documentation. During escalation, the system generates a structured handoff summary containing the detected persona, conversation details, retrieved documents, and recommended next steps.

The project provides both a command-line interface and a Streamlit-based web interface. Gemini is used for persona classification, embeddings, and response generation, while ChromaDB is used for vector storage and semantic retrieval.

This solution demonstrates the practical use of Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), adaptive communication, and human-in-the-loop support workflows.
