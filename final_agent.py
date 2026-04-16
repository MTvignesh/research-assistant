from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from tavily import TavilyClient
import arxiv
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize Tavily for web search
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def web_search(query: str) -> str:
    """Search the web for current information"""
    try:
        result = tavily.search(query, max_results=3)
        return str(result.get('results', []))
    except Exception as e:
        return f"Web search error: {str(e)}"

def arxiv_search(query: str) -> str:
    """Search academic papers on ArXiv"""
    try:
        search = arxiv.Search(query=query, max_results=3, sort_by=arxiv.SortCriterion.SubmittedDate)
        results = []
        for paper in search.results():
            results.append(f"Title: {paper.title}\nAuthors: {', '.join([a.name for a in paper.authors[:3]])}\nSummary: {paper.summary[:300]}\n")
        return "\n".join(results) if results else "No papers found"
    except Exception as e:
        return f"ArXiv error: {str(e)}"

def local_pdf_search(query: str) -> str:
    """Search your local PDF documents"""
    pdf_dir = "./data/pdfs"
    if not os.path.exists(pdf_dir):
        return "No PDF directory found. Create './data/pdfs' and add PDF files."
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    if not pdf_files:
        return "No PDF files found in ./data/pdfs"
    
    try:
        all_chunks = []
        for pdf_file in pdf_files[:2]:  # Limit to 2 PDFs for speed
            loader = PyPDFLoader(os.path.join(pdf_dir, pdf_file))
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_documents(docs)
            all_chunks.extend(chunks)
        
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
        vectorstore = Chroma.from_documents(all_chunks, embeddings)
        results = vectorstore.similarity_search(query, k=3)
        return "\n\n".join([f"From {doc.metadata.get('source', 'PDF')}:\n{doc.page_content[:400]}" for doc in results])
    except Exception as e:
        return f"PDF search error: {str(e)}"

tools = [
    Tool(name="Web Search", func=web_search, description="Useful for searching the internet for current news, events, and real-time information"),
    Tool(name="ArXiv Search", func=arxiv_search, description="Useful for searching academic research papers on ArXiv"),
    Tool(name="PDF Search", func=local_pdf_search, description="Useful for searching through your local PDF documents")
]

# Create prompt template
template = """You are a helpful research assistant. You have access to the following tools:

{tools}

Use the following format:
Question: the input question
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat max 3 times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)

# Create agent
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5
)

print("=" * 60)
print("🤖 Personal Research Assistant - LangChain + RAG + Agentic AI")
print("=" * 60)
print("Tools: Web Search, ArXiv Search, Local PDF Search")
print("Type 'exit' to quit")
print("=" * 60)

while True:
    query = input("\n📚 You: ").strip()
    if query.lower() == "exit":
        print("Goodbye! 👋")
        break
    if not query:
        continue
    
    try:
        response = agent_executor.invoke({"input": query})
        print(f"\n🤖 Assistant: {response['output']}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
