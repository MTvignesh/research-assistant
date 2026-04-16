from langchain.agents import initialize_agent, Tool, AgentType
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from tavily import TavilyClient
import arxiv
import os
from dotenv import load_dotenv

load_dotenv()

llm = OpenAI(temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def web_search(query: str) -> str:
    return str(tavily.search(query, max_results=3))

def arxiv_search(query: str) -> str:
    search = arxiv.Search(query=query, max_results=3)
    return "\n".join([f"{r.title}: {r.summary[:200]}" for r in search.results()])

def local_pdf_search(query: str) -> str:
    pdf_dir = "./data/pdfs"
    if not os.path.exists(pdf_dir) or not os.listdir(pdf_dir):
        return "No PDFs found. Add PDF files to ./data/pdfs folder."
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    if not pdf_files:
        return "No PDF files found."
    
    loader = PyPDFLoader(os.path.join(pdf_dir, pdf_files[0]))
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
    vectorstore = Chroma.from_documents(chunks, embeddings)
    results = vectorstore.similarity_search(query, k=3)
    return "\n\n".join([doc.page_content[:500] for doc in results])

tools = [
    Tool(name="WebSearch", func=web_search, description="Search the web for current information"),
    Tool(name="ArxivSearch", func=arxiv_search, description="Search academic papers on ArXiv"),
    Tool(name="LocalPDFSearch", func=local_pdf_search, description="Search your local PDF documents")
]

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

print("=" * 50)
print("Personal Research Assistant Ready")
print("=" * 50)
print("Tools: Web Search, ArXiv Search, Local PDF Search")
print("Type 'exit' to quit")
print("=" * 50)

while True:
    query = input("\nYou: ").strip()
    if query.lower() == "exit":
        print("Goodbye")
        break
    if not query:
        continue
    
    try:
        response = agent.run(input=query)
        print(f"\nAssistant: {response}")
    except Exception as e:
        print(f"\nError: {str(e)}")
