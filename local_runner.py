"""
Run the Indiana crawler and save results to the local SQLite DB.
"""
from crawlers.indiana_crawler import IndianaCrawler
from data.sqlite_store import init_db, upsert_rfps, list_rfps

def run_once():
    init_db()
    crawler = IndianaCrawler()
    items = crawler.run()
    if not items:
        print("No items found.")
        return
    new = upsert_rfps(items)
    print(f"Found {len(items)} items, inserted {len(new)} new items.")
    if new:
        for n in new:
            print("-", n.get("title"), n.get("event_id"), n.get("url"))

if __name__ == "__main__":
    run_once()
