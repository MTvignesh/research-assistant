from langchain.agents import initialize_agent, Tool, AgentType
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from tavily import TavilyClient
import arxiv
import os
from dotenv import load_dotenv

load_dotenv()

# Check if Groq API key exists, else use OpenAI
groq_key = os.getenv("GROQ_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

if groq_key:
    print("Using Groq LLM")
    from langchain.chat_models import ChatOpenAI
    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        temperature=0,
        openai_api_key=groq_key,
        base_url="https://api.groq.com/openai/v1"
    )
else:
    print("Using OpenAI LLM")
    from langchain.llms import OpenAI
    llm = OpenAI(temperature=0, api_key=openai_key)

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def web_search(query: str) -> str:
    try:
        result = tavily.search(query, max_results=3)
        return str(result.get('results', []))
    except Exception as e:
        return f"Web search error: {str(e)}"

def arxiv_search(query: str) -> str:
    try:
        search = arxiv.Search(query=query, max_results=3)
        results = []
        for paper in search.results():
            results.append(f"Title: {paper.title}\nSummary: {paper.summary[:300]}\n")
        return "\n".join(results) if results else "No papers found"
    except Exception as e:
        return f"ArXiv error: {str(e)}"

def local_pdf_search(query: str) -> str:
    pdf_dir = "./data/pdfs"
    if not os.path.exists(pdf_dir):
        return "No PDF directory found. Create './data/pdfs' and add PDF files."
    
    pdf_files = []
    for root, dirs, files in os.walk(pdf_dir):
        for f in files:
            if f.endswith('.pdf'):
                pdf_files.append(os.path.join(root, f))
    
    if not pdf_files:
        return "No PDF files found in ./data/pdfs"
    
    try:
        all_chunks = []
        for pdf_file in pdf_files[:2]:
            loader = PyPDFLoader(pdf_file)
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_documents(docs)
            all_chunks.extend(chunks)
        
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
        vectorstore = Chroma.from_documents(all_chunks, embeddings)
        results = vectorstore.similarity_search(query, k=3)
        return "\n\n".join([doc.page_content[:400] for doc in results])
    except Exception as e:
        return f"PDF search error: {str(e)}"

tools = [
    Tool(name="Web Search", func=web_search, description="Search the internet for current information"),
    Tool(name="ArXiv Search", func=arxiv_search, description="Search academic papers on ArXiv"),
    Tool(name="PDF Search", func=local_pdf_search, description="Search local PDF documents")
]

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)

print("=" * 60)
print("🤖 Research Assistant Ready!")
print("=" * 60)
print("Tools: Web Search, ArXiv Search, PDF Search")
print("Type 'exit' to quit")
print("=" * 60)

while True:
    query = input("\nYou: ").strip()
    if query.lower() == "exit":
        print("Goodbye!")
        break
    if not query:
        continue
    
    try:
        response = agent.run(input=query)
        print(f"\nAssistant: {response}")
    except Exception as e:
        print(f"\nError: {str(e)}")
