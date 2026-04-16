from langchain.agents import create_react_agent, AgentExecutor
from langchain_groq import ChatGroq
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

# Use a currently available Groq model
# Options: "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Latest Llama model on Groq
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

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
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    if not pdf_files:
        return "No PDF files found in ./data/pdfs"
    
    try:
        all_chunks = []
        for pdf_file in pdf_files[:2]:
            loader = PyPDFLoader(os.path.join(pdf_dir, pdf_file))
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

template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat 3 times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}'''

prompt = PromptTemplate.from_template(template)

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5
)

print("=" * 60)
print("🤖 Research Assistant (Groq - Llama 3.3 70B)")
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
        response = agent_executor.invoke({"input": query})
        print(f"\nAssistant: {response['output']}")
    except Exception as e:
        print(f"\nError: {str(e)}")
