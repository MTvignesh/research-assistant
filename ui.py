import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
import base64
import io
import re
from PIL import Image
from pathlib import Path
import urllib.parse

st.set_page_config(page_title="Research Assistant", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .stChatInput {
        position: fixed;
        bottom: 20px;
        left: 20%;
        right: 20%;
        width: 60%;
    }
    .winner-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 AGENTIC RESEARCH ASSISTANT")
st.caption("⚡ 7 Models Racing | Direct PDF Search | Unsplash Photos | YouTube Videos | Fastest Wins")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "last_source" not in st.session_state:
    st.session_state.last_source = ""
if "last_photo" not in st.session_state:
    st.session_state.last_photo = None
if "last_video" not in st.session_state:
    st.session_state.last_video = None
if "temp_photo" not in st.session_state:
    st.session_state.temp_photo = None
if "temp_photo_name" not in st.session_state:
    st.session_state.temp_photo_name = None
if "photo_used" not in st.session_state:
    st.session_state.photo_used = False
if "last_time" not in st.session_state:
    st.session_state.last_time = 0

# API Keys
YOUTUBE_API_KEY = "AIzaSyA7CMWXZf7QjKc1J1ga1WBcsDt3PEoIuAU"
TAVILY_KEY = "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"
GROQ_KEY = "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"
HF_TOKEN = "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"

# ============ RGBA to RGB Conversion ============
def convert_to_rgb(img):
    if img.mode in ('RGBA', 'LA', 'P'):
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        if img.mode == 'RGBA':
            rgb_img.paste(img, mask=img.split()[-1])
        else:
            rgb_img.paste(img)
        return rgb_img
    return img.convert('RGB')

# ============ FAST DIRECT PDF SEARCH (NO INDEXING) ============
def search_pdfs_direct(query):
    """Search PDFs directly - FAST, no indexing needed"""
    pdf_dir = Path("./data/pdfs")
    if not pdf_dir.exists():
        return "❌ PDF directory not found"
    
    pdf_files = list(pdf_dir.rglob("*.pdf"))
    if not pdf_files:
        return "⚠️ No PDF files found"
    
    results = []
    query_lower = query.lower()
    
    # Limit search to first 100 PDFs for speed
    max_pdfs = min(100, len(pdf_files))
    
    for i, pdf_file in enumerate(pdf_files[:max_pdfs]):
        try:
            loader = PyPDFLoader(str(pdf_file))
            documents = loader.load()
            
            for doc in documents:
                if query_lower in doc.page_content.lower():
                    # Find surrounding text
                    content = doc.page_content
                    idx = content.lower().find(query_lower)
                    start = max(0, idx - 150)
                    end = min(len(content), idx + 250)
                    snippet = content[start:end].replace('\n', ' ')
                    
                    results.append(f"📄 **{pdf_file.name}**\n...{snippet}...\n")
                    break  # One result per PDF
        except:
            pass
        
        if len(results) >= 5:
            break
    
    if results:
        return "\n\n".join(results[:5])
    else:
        return "No results found. Try different keywords."

# ============ PHOTO FETCH ============
def fetch_photo(query):
    """Fetch photo from Unsplash (works for ANYTHING - people, objects, places)"""
    search_term = query.strip().lower()
    search_term = re.sub(r'(photo|picture|image|of|give|me|show)', '', search_term).strip()
    
    if not search_term:
        search_term = query.strip()
    
    try:
        encoded = urllib.parse.quote(search_term)
        url = f"https://source.unsplash.com/featured/800x600/?{encoded}"
        r = requests.head(url, timeout=5)
        if r.status_code == 200:
            return url, "Unsplash"
    except:
        pass
    
    try:
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_term.replace(' ', '_')}"
        r = requests.get(wiki_url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            thumb = data.get('thumbnail', {}).get('source')
            if thumb:
                return thumb, "Wikipedia"
    except:
        pass
    
    return None, None

# ============ VIDEO FETCH ============
def fetch_video(query):
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={encoded}&key={YOUTUBE_API_KEY}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('items'):
                video_id = data['items'][0]['id']['videoId']
                return f"https://www.youtube.com/watch?v={video_id}"
    except:
        pass
    return None

# ============ 7 MODELS RACING ============
def model_duckduckgo(q):
    s = time.time()
    try:
        r = requests.get(f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1", timeout=8)
        if r.status_code == 200:
            d = r.json()
            ans = d.get('Answer') or d.get('AbstractText') or d.get('Definition')
            if ans and len(ans) > 5:
                return ans, time.time()-s, "🦆 DuckDuckGo"
    except:
        pass
    return None, time.time()-s, "🦆 DuckDuckGo"

def model_wikipedia_text(q):
    s = time.time()
    try:
        r = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&format=json", timeout=8)
        if r.status_code == 200:
            data = r.json()
            if data.get('query', {}).get('search'):
                title = data['query']['search'][0]['title']
                r2 = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}", timeout=8)
                if r2.status_code == 200:
                    extract = r2.json().get('extract', '')[:500]
                    if extract:
                        return extract, time.time()-s, "📚 Wikipedia"
    except:
        pass
    return None, time.time()-s, "📚 Wikipedia"

def model_tavily_text(q):
    s = time.time()
    try:
        headers = {"Authorization": f"Bearer {TAVILY_KEY}"}
        r = requests.post("https://api.tavily.com/search", json={"api_key": TAVILY_KEY, "query": q, "max_results": 1}, timeout=8)
        if r.status_code == 200:
            data = r.json()
            if data.get('results'):
                ans = data['results'][0].get('content', '')[:500]
                if ans:
                    return ans, time.time()-s, "🔍 Tavily"
    except:
        pass
    return None, time.time()-s, "🔍 Tavily"

def model_groq(q):
    s = time.time()
    try:
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": q}], "max_tokens": 200}
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=10)
        if r.status_code == 200:
            ans = r.json()['choices'][0]['message']['content']
            if ans:
                return ans, time.time()-s, "⚡ Groq"
    except:
        pass
    return None, time.time()-s, "⚡ Groq"

def model_flan(q):
    s = time.time()
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        r = requests.post("https://api-inference.huggingface.co/models/google/flan-t5-large", headers=headers, json={"inputs": q, "parameters": {"max_new_tokens": 150}}, timeout=10)
        if r.status_code == 200:
            res = r.json()
            if isinstance(res, list) and res:
                ans = res[0].get('generated_text', '')
                if ans:
                    return ans, time.time()-s, "🤗 Flan-T5"
    except:
        pass
    return None, time.time()-s, "🤗 Flan-T5"

def model_phi(q):
    s = time.time()
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        r = requests.post("https://api-inference.huggingface.co/models/microsoft/phi-2", headers=headers, json={"inputs": q, "parameters": {"max_new_tokens": 150}}, timeout=10)
        if r.status_code == 200:
            res = r.json()
            if isinstance(res, list) and res:
                ans = res[0].get('generated_text', '')
                if ans:
                    return ans, time.time()-s, "🤗 Phi-2"
    except:
        pass
    return None, time.time()-s, "🤗 Phi-2"

def model_zephyr(q):
    s = time.time()
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        r = requests.post("https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta", headers=headers, json={"inputs": q, "parameters": {"max_new_tokens": 200}}, timeout=10)
        if r.status_code == 200:
            res = r.json()
            if isinstance(res, list) and res:
                ans = res[0].get('generated_text', '')
                if ans:
                    return ans, time.time()-s, "🤗 Zephyr"
    except:
        pass
    return None, time.time()-s, "🤗 Zephyr"

def get_fastest_answer(question):
    models = [model_duckduckgo, model_wikipedia_text, model_tavily_text, model_groq, model_flan, model_phi, model_zephyr]
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = {executor.submit(model, question): model for model in models}
        for future in as_completed(futures):
            try:
                ans, elapsed, src = future.result(timeout=15)
                if ans and len(ans) > 5:
                    return ans, src, elapsed
            except:
                continue
    return "No answer found", "None", 0

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### 🏆 7 MODELS RACING")
    st.markdown("🦆 DuckDuckGo | 📚 Wikipedia | 🔍 Tavily | ⚡ Groq | 🤗 Flan-T5 | 🤗 Phi-2 | 🤗 Zephyr")
    
    st.divider()
    
    # ============ DIRECT PDF SEARCH (NO INDEXING) ============
    st.markdown("### 📚 PDF Search (Instant)")
    
    pdf_dir = "./data/pdfs"
    if os.path.exists(pdf_dir):
        pdf_count = sum(1 for _ in Path(pdf_dir).rglob("*.pdf"))
        st.metric("📚 PDF Library", pdf_count)
        
        st.markdown("---")
        st.markdown("### 🔍 Search PDFs")
        rag_query = st.text_input("", placeholder="Enter search term...", key="rag_search", label_visibility="collapsed")
        if st.button("🔍 Search", use_container_width=True):
            if rag_query:
                with st.spinner(f"Searching {min(100, pdf_count)} PDFs..."):
                    results = search_pdfs_direct(rag_query)
                    st.markdown("---")
                    st.markdown("### 📄 Results:")
                    st.markdown(results)
            else:
                st.warning("Enter a search term")
    
    st.divider()
    
    st.markdown("### 📸 Upload Photo (ONE TIME USE)")
    if not st.session_state.photo_used:
        uploaded = st.file_uploader("Select a photo", type=["jpg", "jpeg", "png"])
        if uploaded:
            img = Image.open(uploaded)
            img = convert_to_rgb(img)
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            st.session_state.temp_photo = base64.b64encode(buffered.getvalue()).decode()
            st.session_state.temp_photo_name = uploaded.name
            st.image(img, width=100)
            st.success(f"✅ Ready - Ask ONE question")
    
    if st.session_state.temp_photo and st.button("🗑️ Remove Photo"):
        st.session_state.temp_photo = None
        st.session_state.temp_photo_name = None
        st.session_state.photo_used = False
        st.rerun()
    
    st.divider()
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.last_answer = ""
        st.session_state.last_photo = None
        st.session_state.last_video = None
        st.rerun()

# ============ MAIN ============

if st.session_state.last_answer:
    st.markdown("---")
    st.markdown(f'<div class="winner-box"><b>🏆 WINNER: {st.session_state.last_source}</b><br><br>{st.session_state.last_answer}<br><br>⚡ {st.session_state.last_time}s</div>', unsafe_allow_html=True)
    
    if st.session_state.last_photo:
        st.image(st.session_state.last_photo, width=500)
    if st.session_state.last_video:
        st.video(st.session_state.last_video)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("photo"):
            st.image(msg["photo"], width=150)

prompt = st.chat_input("Ask ANYTHING... (photo, video, question)")

if prompt and prompt != st.session_state.last_question:
    st.session_state.last_question = prompt
    
    is_video = 'video' in prompt.lower()
    is_photo = any(w in prompt.lower() for w in ['photo', 'picture', 'image', 'logo'])
    
    current_photo = st.session_state.temp_photo if not st.session_state.photo_used else None
    
    if current_photo:
        st.session_state.photo_used = True
    
    user_msg = {"role": "user", "content": prompt}
    if current_photo:
        img_data = base64.b64decode(current_photo)
        img = Image.open(io.BytesIO(img_data))
        user_msg["photo"] = img
    st.session_state.messages.append(user_msg)
    
    with st.chat_message("user"):
        st.markdown(prompt)
        if current_photo:
            st.image(img, width=150)
    
    with st.chat_message("assistant"):
        answer = ""
        src = ""
        tm = 0.0
        photo_url = None
        video_url = None
        
        # Handle uploaded photo
        if current_photo:
            with st.spinner("📸 Analyzing your photo..."):
                answer = f"📸 Photo '{st.session_state.temp_photo_name}' received! What would you like to know about this image?"
                src = "Assistant"
                tm = 0.0
        
        # Handle video request
        elif is_video:
            search_term = re.sub(r'(video|give|me|show|of|please|want|need)', '', prompt.lower()).strip()
            if not search_term or len(search_term) < 2:
                search_term = prompt.lower().replace('video', '').strip()
            
            with st.spinner(f"🎥 Fetching video..."):
                video_url = fetch_video(search_term)
                if video_url:
                    answer = f"🎥 Here's a video about {search_term.title()}"
                    src = "YouTube"
                else:
                    answer = f"❌ No video found for '{search_term}'"
                    src = "None"
        
        # Handle photo request
        elif is_photo:
            search_term = re.sub(r'(photo|picture|image|logo|give|me|show|of|please|want|need)', '', prompt.lower()).strip()
            if not search_term or len(search_term) < 2:
                search_term = prompt.lower().replace('photo', '').strip()
            
            with st.spinner(f"📸 Fetching photo of {search_term}..."):
                photo_url, src = fetch_photo(search_term)
                if photo_url:
                    answer = f"📸 Here's a photo of {search_term.title()}"
                else:
                    answer = f"❌ Could not find a photo of '{search_term}'. Try a different name."
                    src = "Unsplash"
        
        # Handle text question
        else:
            with st.spinner("🏁 Racing 7 models..."):
                answer, src, tm = get_fastest_answer(prompt)
        
        st.session_state.last_answer = answer
        st.session_state.last_source = src
        st.session_state.last_photo = photo_url
        st.session_state.last_video = video_url
        st.session_state.last_time = round(tm, 2)
        
        st.markdown(answer)
        if photo_url:
            st.image(photo_url, width=500)
        if video_url:
            st.video(video_url)
        if not photo_url and not video_url and not current_photo:
            st.caption(f"🏁 {src} | ⚡ {round(tm,2)}s")
        st.session_state.messages.append({"role": "assistant", "content": answer})
    
    if current_photo:
        st.session_state.temp_photo = None
        st.session_state.temp_photo_name = None
    
    st.rerun()