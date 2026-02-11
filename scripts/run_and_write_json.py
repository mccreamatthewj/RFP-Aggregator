#!/usr/bin/env python3
"""
Run the Indiana crawler and write results to docs/data.json for publishing.
The script merges with existing data.json (by event_id or url) and updates
discovered_at timestamps for new items.
"""
import os
import json
import datetime
from crawlers.indiana_crawler import IndianaCrawler

OUT_DIR = "docs"
OUT_FILE = os.path.join(OUT_DIR, "data.json")
MAX_ITEMS = int(os.getenv("MAX_ITEMS", "1000"))

def load_existing(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def key_for(item):
    # prefer event_id, else url
    eid = (item.get("event_id") or "").strip()
    if eid:
        return f"eid:{eid}"
    url = (item.get("url") or "").strip()
    return f"url:{url}"

def merge_items(old_items, new_items):
    by_key = {}
    for it in old_items:
        k = key_for(it)
        by_key[k] = it

    inserted = []
    now = datetime.datetime.utcnow().isoformat()

    for it in new_items:
        k = key_for(it)
        if k in by_key:
            # update some fields if missing but keep discovered_at
            existing = by_key[k]
            # keep existing discovered_at
            for fld in ("title","agency","description","due_date","url","contact_email","event_id"):
                if (not existing.get(fld)) and it.get(fld):
                    existing[fld] = it.get(fld)
            by_key[k] = existing
        else:
            it["discovered_at"] = now
            by_key[k] = it
            inserted.append(it)

    # produce list sorted by discovered_at desc
    merged = list(by_key.values())
    merged.sort(key=lambda x: x.get("discovered_at", ""), reverse=True)
    return merged[:MAX_ITEMS], inserted

def ensure_out_dir():
    os.makedirs(OUT_DIR, exist_ok=True)

def main():
    print("Running Indiana crawler...")
    crawler = IndianaCrawler()
    items = crawler.run()
    print(f"Scraped {len(items)} item(s).")

    existing = load_existing(OUT_FILE)
    merged, inserted = merge_items(existing, items)

    ensure_out_dir()
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(merged)} total items to {OUT_FILE}. Inserted {len(inserted)} new.")
    # exit with 0 always — workflow will commit only if file changed
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
