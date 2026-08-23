import re

import feedparser
import requests

from config import EVENT_FEEDS
from filters import event_ok, event_region

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text):
    return _TAG_RE.sub("", text or "").replace("&#8217;", "'").strip()


def fetch_listings():
    listings = []
    for feed_name, url in EVENT_FEEDS:
        try:
            # Fetch via requests so we control the UA and timeout; feedparser
            # only does the parsing.
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            parsed = feedparser.parse(response.content)
        except Exception as exc:
            print(f"  [events:{feed_name}] skipped: {exc}")
            continue

        for entry in parsed.entries:
            title = _clean(entry.get("title", ""))
            summary = _clean(entry.get("summary", ""))[:600]
            categories = [t.get("term", "") for t in entry.get("tags", []) or []]
            if not title or not event_ok(title, summary, categories):
                continue

            region = event_region(f"{title} {summary}")
            if region == "other":
                continue  # clearly US-only, not reachable from Ireland

            link = entry.get("link", "")
            listings.append({
                "title": title,
                "company": feed_name,
                "location": "Ireland" if region == "ireland" else "Europe / Online",
                "url": link,
                "posted_date": (entry.get("published", "") or "")[:16],
                "source": feed_name,
                "snippet": summary[:400],
                "kind": "event",
                "region": region,
                # Event titles repeat across reposts; the permalink is stable.
                "dedup_id": link.split("?")[0],
            })

    return listings
