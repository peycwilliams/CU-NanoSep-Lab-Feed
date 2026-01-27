import os
import time
import requests
from feedgen.feed import FeedGenerator
from datetime import datetime

# =========================
# CONFIG
# =========================

OUTPUT_DIR = "rss"
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"

AUTHORS = [
    {"name": "Jay Werber", "authorId": "35255441"},
    {"name": "Viatcheslav Freger", "authorId": "7937200"},
    {"name": "Menachem Elimalech", "authorId": "2896168"},
    {"name": "Orlando Coronell", "authorId": "12649015"},
    {"name": "Ryan Lively", "authorId": "2832408"},
    {"name": "Jovan Kamcev", "authorId": "7646506"},
    {"name": "Benny Freeman", "authorId": "38087797"},
    {"name": "Geoffrey Geise", "authorId": "1867417"},
    {"name": "Chuyang Tang", "authorId": "2237102582"},
    {"name": "Jeff McCutcheon", "authorId": "39812318"},
    {"name": "Ryan Kingsbury", "authorId": "40390912"},
    {"name": "Manish Kumar", "authorId": "2109944022"},
    {"name": "Andrew Livingston", "authorId": "144456055"},
]

FIELDS = "title,abstract,year,venue,publicationDate,url"

# =========================
# FUNCTIONS
# =========================

def fetch_papers(author_id):
    url = f"{SEMANTIC_SCHOLAR_API}/author/{author_id}/papers"
    params = {
        "fields": FIELDS,
        "limit": 100
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("data", [])

def sanitize_filename(name):
    return name.lower().replace(" ", "_")

def create_rss(author_name, author_id, papers):
    fg = FeedGenerator()
    fg.id(f"https://www.semanticscholar.org/author/{author_id}")
    fg.title(f"{author_name}")
    fg.link(
        href=f"https://www.semanticscholar.org/author/{author_id}",
        rel="alternate"
    )
    fg.description(f"Semantic Scholar publications for {author_name}")
    fg.language("en")

    for paper in papers:
        fe = fg.add_entry()
        fe.id(paper.get("url", ""))
        fe.title(paper.get("title", "Untitled"))
        fe.link(href=paper.get("url", ""))

        summary = paper.get("abstract") or "No abstract available."
        fe.summary(summary)

        pub_date = paper.get("publicationDate")
        if pub_date:
            try:
                fe.published(datetime.fromisoformat(pub_date))
            except ValueError:
                pass

    return fg

# =========================
# MAIN
# =========================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for author in AUTHORS:
        name = author["name"]
        author_id = author["authorId"]
        print(f"Generating RSS for {name}...")
        
        try:
            papers = fetch_papers(author_id)
            
            # Your sorting logic here
            papers.sort(
                key=lambda x: x.get("publicationDate") or "0000-00-00", 
                reverse=True
            )

            fg = create_rss(name, author_id, papers)
            filename = f"{sanitize_filename(name)}.xml"
            filepath = os.path.join(OUTPUT_DIR, filename)
            fg.rss_file(filepath)
            
            # --- RATE LIMIT FIX ---
            print(f"Successfully generated {name}. Waiting 3 seconds...")
            time.sleep(3) # This prevents the 429 error
            # ----------------------
            
        except Exception as e:
            print(f"Error fetching {name}: {e}")
            continue # Move to the next author even if one fails
            
    print("Done! RSS feeds generated.")

if __name__ == "__main__":
    main()
