"""Download 1000+ Free Research Papers from ArXiv"""
import arxiv
import os
import time
from pathlib import Path
from datetime import datetime

# Create download directory
download_dir = Path("./data/pdfs/arxiv_papers")
download_dir.mkdir(parents=True, exist_ok=True)

# Search queries to get 1000+ papers
search_queries = [
    "machine learning",
    "deep learning", 
    "neural networks",
    "artificial intelligence",
    "transformer architecture",
    "attention mechanism",
    "large language models",
    "generative AI",
    "computer vision",
    "natural language processing",
    "reinforcement learning",
    "multimodal learning",
    "few shot learning",
    "self supervised learning",
    "diffusion models",
]

print("=" * 60)
print("📚 Downloading Free Research Papers")
print("=" * 60)
print(f"Start time: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 60)

total = 0
papers_per_query = 70  # 15 x 70 = 1050 papers

for query in search_queries:
    print(f"\n🔍 Searching: {query}")
    
    try:
        search = arxiv.Search(
            query=query,
            max_results=papers_per_query,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        topic_folder = download_dir / query.replace(" ", "_")
        topic_folder.mkdir(exist_ok=True)
        
        for paper in search.results():
            try:
                paper_id = paper.get_short_id().replace("/", "_")
                title = paper.title[:60].replace("/", "_").replace("\\", "_").replace(":", "_")
                filename = f"{paper_id}_{title}.pdf"
                filepath = topic_folder / filename
                
                if not filepath.exists():
                    paper.download_pdf(dirpath=str(topic_folder), filename=filename)
                    total += 1
                    print(f"  ✅ [{total}] {paper.title[:50]}...")
                    time.sleep(0.3)
                    
            except Exception as e:
                print(f"  ❌ Error: {str(e)[:50]}")
                
    except Exception as e:
        print(f"  ❌ Search failed: {e}")

print("\n" + "=" * 60)
print(f"✅ Downloaded {total} papers to {download_dir}")
print("=" * 60)