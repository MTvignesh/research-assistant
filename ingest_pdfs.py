import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")

pdf_dir = Path("./data/pdfs")
pdf_files = list(pdf_dir.glob("*.pdf"))
all_docs = []

for pdf_path in pdf_files:
    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = pdf_path.name
    all_docs.extend(docs)

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(all_docs)
vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="./vector_store")
print(f"✅ Done! Ingested {len(pdf_files)} PDFs, {len(chunks)} chunks created")