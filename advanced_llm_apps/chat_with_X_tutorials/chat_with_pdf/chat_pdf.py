import os
import tempfile
import streamlit as st
from embedchain import App

def embedchain_bot(db_path, api_key):
    return App.from_config(
        config={
            "llm": {"provider": "google", "config": {"api_key": api_key, "model": "gemini-pro"}},
            "vectordb": {"provider": "chroma", "config": {"dir": db_path}},
            "embedder": {"provider": "google", "config": {"api_key": api_key, "model": "models/text-embedding-004"}},
        }
    )

st.title("Chat with PDF")

# Default Gemini API key
default_gemini_key = "AIzaSyAgRnhc4SWfs1acLBsD5Hc34pqFXiX6OPo"
gemini_api_key = st.text_input("Gemini API Key", value=default_gemini_key, type="password")

if gemini_api_key:
    db_path = tempfile.mkdtemp()
    app = embedchain_bot(db_path, gemini_api_key)

    pdf_file = st.file_uploader("Upload a PDF file", type="pdf")

    if pdf_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(pdf_file.getvalue())
            app.add(f.name, data_type="pdf_file")
        os.remove(f.name)
        st.success(f"Added {pdf_file.name} to knowledge base!")

    prompt = st.text_input("Ask a question about the PDF")

    if prompt:
        answer = app.chat(prompt)
        st.write(answer)

        