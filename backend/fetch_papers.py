import requests
import psycopg2
import os
from dotenv import load_dotenv
import time

load_dotenv()

OPENALEX_API = "https://api.openalex.org"
INSTITUTION_ID = "https://openalex.org/I12912129"

def get_connection():
    database_url = os.getenv('DATABASE_URL')
    return psycopg2.connect(database_url)

def fetch_papers_from_openalex(institution_id, years_back=5, max_papers=5000):
    current_year = 2024
    start_year = current_year - years_back

    papers = []
    page = 1
    per_page = 100

    print(f"Fetching papers from {start_year} to {current_year}...")

    while len(papers) < max_papers:
        url = f"{OPENALEX_API}/works"
        params = {
            "filter": f"institutions.id:{institution_id},publication_year:{start_year}-{current_year}",
            "per-page": per_page,
            "page": page,
            "mailto": "example@example.com"
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break

        data = response.json()
        results = data.get("results", [])

        if not results:
            break

        papers.extend(results)
        print(f"Fetched page {page}, total papers: {len(papers)}")

        page += 1
        time.sleep(0.1)

        if len(papers) >= max_papers:
            papers = papers[:max_papers]
            break

    return papers

def process_and_save_papers(papers):
    conn = get_connection()
    cursor = conn.cursor()

    papers_saved = 0
    authors_saved = 0
    relations_saved = 0

    author_cache = {}

    print("Saving papers to database...")

    for paper in papers:
        try:
            paper_id = paper.get("id", "").replace("https://openalex.org/", "")
            title = paper.get("title", "Untitled")
            year = paper.get("publication_year")
            citation_count = paper.get("cited_by_count", 0)

            primary_topic = paper.get("primary_topic")
            if primary_topic:
                field = primary_topic.get("domain", {}).get("display_name", "Unknown")
            else:
                field = "Unknown"

            if not paper_id or not year:
                continue

            cursor.execute(
                "INSERT INTO papers (id, title, year, field, citation_count) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (paper_id, title, year, field, citation_count)
            )
            papers_saved += cursor.rowcount

            authorships = paper.get("authorships", [])
            for authorship in authorships:
                author = authorship.get("author", {})
                author_id = author.get("id", "").replace("https://openalex.org/", "")
                author_name = author.get("display_name", "Unknown")

                institutions = authorship.get("institutions", [])
                affiliation = institutions[0].get("display_name", "Unknown") if institutions else "Unknown"

                if not author_id:
                    continue

                if author_id not in author_cache:
                    cursor.execute(
                        "INSERT INTO authors (id, name, affiliation) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING",
                        (author_id, author_name, affiliation)
                    )
                    authors_saved += cursor.rowcount
                    author_cache[author_id] = True

                cursor.execute(
                    "INSERT INTO author_paper (author_id, paper_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (author_id, paper_id)
                )
                relations_saved += cursor.rowcount

        except Exception as e:
            print(f"Error processing paper: {e}")
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\nSaved {papers_saved} papers, {authors_saved} authors, {relations_saved} author-paper relations")

def main():
    print("Starting data fetch from OpenAlex...")

    papers = fetch_papers_from_openalex(INSTITUTION_ID, years_back=5, max_papers=5000)

    print(f"\nFetched {len(papers)} papers")

    if papers:
        process_and_save_papers(papers)
        print("Data fetch complete!")
    else:
        print("No papers fetched")

if __name__ == "__main__":
    main()
