import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin
import re

BASE_URL = "https://www.in.gov"
OPPORTUNITIES_PATH = "/idoa/procurement/current-business-opportunities/"

HEADERS = {
    "User-Agent": "RFP-Aggregator-Bot/1.0 (+https://github.com/mccreamatthewj/RFP-Aggregator)"
}

def _clean_text(el) -> str:
    if el is None:
        return ""
    return " ".join(el.stripped_strings)

def _find_contact_email(text: str) -> Optional[str]:
    m = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return m.group(0) if m else None

class IndianaCrawler:
    """Crawler for Indiana Department of Administration procurement page.

    Extracts items with keys:
      title, event_id, agency, description, due_date, url, contact_email
    """

    def __init__(self, base_url: str = BASE_URL, path: str = OPPORTUNITIES_PATH):
        self.start_url = urljoin(base_url, path)

    def fetch(self, url: str) -> Optional[str]:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def parse_opportunities(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "lxml")
        results: List[Dict] = []

        # 1) Try to parse a table if present
        table = soup.find("table")
        if table:
            for row in table.find_all("tr"):
                cols = row.find_all(["td", "th"])
                if not cols:
                    continue
                texts = [_clean_text(c) for c in cols]
                entry = {
                    "title": texts[0] if len(texts) > 0 else "",
                    "agency": texts[1] if len(texts) > 1 else "",
                    "event_id": texts[2] if len(texts) > 2 else "",
                    "due_date": texts[-1] if len(texts) > 0 else "",
                    "url": None,
                    "description": "",
                    "contact_email": None,
                }
                a = row.find("a", href=True)
                if a:
                    entry["url"] = urljoin(BASE_URL, a["href"])
                results.append(entry)
            if results:
                return results

        # 2) Fallback: find candidate blocks (articles, list items, paragraphs)
        main = soup.find(id="main") or soup.find(class_="page-content") or soup

        candidates = main.find_all(["article", "li", "div", "p", "tr"], limit=300)
        for cand in candidates:
            a = cand.find("a", href=True)
            if not a:
                continue

            title = _clean_text(a) or _clean_text(cand.find("h3") or cand.find("h2") or cand)
            href = a["href"]
            url = urljoin(BASE_URL, href)

            text_blob = _clean_text(cand)
            contact = _find_contact_email(text_blob)

            # event id heuristics
            event_id = ""
            m = re.search(r"(Event\s*ID[:#]?\s*|ID[:#]?\s*)([A-Za-z0-9-]+)", text_blob, re.I)
            if m:
                event_id = m.group(2)

            # due date heuristics
            due_date = ""
            m2 = re.search(r"(Due\s*Date[:\-]?\s*)([A-Za-z0-9,\s:@-]+)", text_blob, re.I)
            if m2:
                due_date = m2.group(2).strip()

            # short description
            desc = ""
            p = cand.find_next_sibling("p")
            if p:
                desc = _clean_text(p)

            entry = {
                "title": title.strip(),
                "event_id": event_id.strip(),
                "agency": "",
                "description": desc,
                "due_date": due_date,
                "url": url,
                "contact_email": contact,
            }

            if entry["title"] and entry["url"]:
                results.append(entry)

        # Deduplicate by url or event_id
        seen = set()
        unique = []
        for r in results:
            key = r.get("event_id") or r.get("url")
            if not key:
                continue
            if key in seen:
                continue
            seen.add(key)
            unique.append(r)

        return unique

    def run(self) -> List[Dict]:
        html = self.fetch(self.start_url)
        if not html:
            return []
        items = self.parse_opportunities(html)
        return items

if __name__ == "__main__":
    crawler = IndianaCrawler()
    items = crawler.run()
    print(f"Found {len(items)} items")
    for i, it in enumerate(items, 1):
        print(f"--- #{i} ---")
        for k, v in it.items():
            print(f"{k}: {v}")
        print()
