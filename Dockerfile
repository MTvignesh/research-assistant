FROM python:3.10-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install \
    langchain==0.0.340 \
    langchain-community==0.0.10 \
    openai==0.28.0 \
    python-dotenv==1.0.0 \
    tavily-python==0.5.0 \
    arxiv==2.0.0 \
    pypdf==3.9.0 \
    tiktoken==0.5.1 \
    langchain-groq \
    chromadb==0.4.22 \
    sentence-transformers==2.2.2 \
    streamlit==1.28.0

RUN mkdir -p /workspace/data/pdfs /workspace/vector_store

EXPOSE 8501

CMD ["streamlit", "run", "ui.py", "--server.port=8501", "--server.address=0.0.0.0"]