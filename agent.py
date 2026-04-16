from langchain.agents import initialize_agent, Tool, AgentType
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from tools import local_pdf_search, web_search, arxiv_search
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

tools = [
    Tool(name="Local PDF Search", func=local_pdf_search, description="Search your local PDF collection"),
    Tool(name="Web Search", func=web_search, description="Search the live web for recent information"),
    Tool(name="ArXiv Search", func=arxiv_search, description="Search academic papers on ArXiv")
]

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)

print("🤖 Research Assistant Ready!")
print("Type 'exit' to quit")

while True:
    query = input("\n📚 You: ").strip()
    if query.lower() == "exit":
        print("Goodbye! 👋")
        break
    if not query:
        continue
    
    print("\n🔍 Researching...")
    try:
        response = agent.invoke({"input": query})
        print(f"\n🤖 Assistant: {response['output']}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
