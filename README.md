# 🤖 AGENTIC RESEARCH ASSISTANT

⚡ **7 Models Racing | RAG PDF Search | Unsplash Photos | YouTube Videos | Fastest Wins**

## 📖 About This Project

This is an **AI-powered Research Assistant** that combines multiple AI models, web search, PDF search, image fetching, and video search into a single chat interface. It uses **Agentic AI** to decide which tool to use for each question and races 7 different models to give you the fastest answer.

## 🎯 What Makes This Special?

| Feature | Description |
|---------|-------------|
| **7 Models Racing** | DuckDuckGo, Wikipedia, Tavily, Groq, Flan-T5, Phi-2, Zephyr run in parallel - fastest valid answer wins |
| **RAG PDF Search** | Search through your personal PDF library using vector embeddings |
| **Photo Fetch** | Get real images from Unsplash for any query |
| **Video Fetch** | Search and play YouTube videos directly |
| **Photo Upload** | Upload your own photos and ask questions about them |
| **Voice Search** | Speech recognition support (limited on Windows Docker) |
| **Chat History** | Full conversation memory with clear chat option |

## 🧠 How It Works
User Question
↓
Agentic Decision Layer
↓
┌─────────────────────────────────────┐
│ Is this a PHOTO request? │ → Unsplash API
│ Is this a VIDEO request? │ → YouTube API
│ Is this a PDF search? │ → Direct PDF text search
│ Is this a general question? │ → 7 Models Racing
└─────────────────────────────────────┘
↓
Fastest valid answer returned to user

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **UI Framework** | Streamlit |
| **LLM Models** | Groq, Hugging Face (Flan-T5, Phi-2, Zephyr) |
| **Search APIs** | DuckDuckGo, Wikipedia, Tavily |
| **Image API** | Unsplash |
| **Video API** | YouTube Data API v3 |
| **PDF Processing** | PyPDF, LangChain |
| **Vector Database** | ChromaDB |
| **Container** | Docker |

## 📁 Project Structure
go and watch structure png 
