"""Fast Downloader - Resume Capable"""
import arxiv
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

download_dir = Path("./data/pdfs/arxiv_papers")
download_dir.mkdir(parents=True, exist_ok=True)

# More queries for 1000+ papers
queries = [
    "machine learning", "deep learning", "neural networks",
    "artificial intelligence", "computer vision", "NLP",
    "reinforcement learning", "transformers", "LLM",
    "generative AI", "robotics", "speech recognition",
    "optimization", "data mining", "big data"
] * 2  # Double for more papers

def download_paper(query, paper):
    topic_dir = download_dir / query.replace(" ", "_")
    topic_dir.mkdir(exist_ok=True)
    filename = f"{paper.get_short_id().replace('/', '_')}.pdf"
    filepath = topic_dir / filename
    
    if filepath.exists():
        return False, f"Exists: {paper.title[:40]}"
    
    try:
        paper.download_pdf(dirpath=str(topic_dir), filename=filename)
        return True, f"Downloaded: {paper.title[:40]}"
    except:
        return False, f"Failed: {paper.title[:40]}"

# Collect papers
all_papers = []
for query in queries:
    try:
        search = arxiv.Search(query=query, max_results=50)
        for paper in search.results():
            all_papers.append((query, paper))
    except:
        pass

print(f"📚 Downloading {len(all_papers)} papers...")

downloaded = 0
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(download_paper, q, p) for q, p in all_papers]
    for future in as_completed(futures):
        success, msg = future.result()
        if success:
            downloaded += 1
            print(f"[{downloaded}] {msg}")
        time.sleep(0.1)

print(f"\n✅ Complete! Downloaded {downloaded} new papers")