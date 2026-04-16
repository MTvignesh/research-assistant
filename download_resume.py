import arxiv
from pathlib import Path
import time
download_dir = Path("./data/pdfs/arxiv_papers")
download_dir.mkdir(parents=True, exist_ok=True)
topics = [
    "machine learning", "deep learning", "neural networks",
    "artificial intelligence", "computer vision", "NLP",
    "reinforcement learning", "transformers", "LLM",
    "generative AI", "robotics", "quantum computing",
    "data science", "cybersecurity", "blockchain"
]
def get_count():
    return len(list(download_dir.rglob("*.pdf")))
target = 1000
current = get_count()
print(f"Current: {current} papers, Target: {target}")
for topic in topics:
    if current >= target:
        break
    print(f"\nSearching: {topic}")
    search = arxiv.Search(query=topic, max_results=70)
    topic_dir = download_dir / topic.replace(" ", "_")
    topic_dir.mkdir(exist_ok=True)
    for paper in search.results():
        if current >= target:
            break
        filename = f"{paper.get_short_id().replace('/', '_')}.pdf"
        filepath = topic_dir / filename
        if not filepath.exists():
            try:
                paper.download_pdf(dirpath=str(topic_dir), filename=filename)
                current += 1
                print(f"[{current}] {paper.title[:40]}")
                time.sleep(0.3)
            except:
                pass
print(f"\nDone! Total PDFs: {current}")
