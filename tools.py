from langchain.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from tavily import TavilyClient
import arxiv
import os

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
vectorstore = Chroma(persist_directory="./vector_store", embedding_function=embeddings)

@tool
def local_pdf_search(query: str) -> str:
    """Search your local PDF collection."""
    results = vectorstore.similarity_search(query, k=5)
    return "\n\n".join([f"[{doc.metadata['source']}]\n{doc.page_content[:500]}" for doc in results])

@tool
def web_search(query: str) -> str:
    """Search the live web."""
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = client.search(query, max_results=3)
    return "\n".join([f"{r['title']}: {r['content'][:300]}" for r in response['results']])

@tool
def arxiv_search(query: str) -> str:
    """Search academic papers."""
    search = arxiv.Search(query=query, max_results=3, sort_by=arxiv.SortCriterion.SubmittedDate)
    return "\n".join([f"{r.title} ({r.published.date()}): {r.summary[:300]}" for r in search.results()])