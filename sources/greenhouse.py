import re

import requests

from config import GREENHOUSE_COMPANIES
from filters import classify_level, title_ok

# Public board API: free, no key, no quota.
BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"

# Deliberately stricter than filters.location_ok: that helper treats a bare
# "remote" as a match, which here would let "Remote - United States" through.
_IRELAND_RE = re.compile(r"ireland|dublin|\bcork\b", re.IGNORECASE)


def fetch_listings():
    listings = []
    for slug in GREENHOUSE_COMPANIES:
        try:
            response = requests.get(BOARD_URL.format(slug=slug), timeout=30)
            response.raise_for_status()
            jobs = response.json().get("jobs", [])
        except Exception as exc:
            # A dead slug must not sink the other companies.
            print(f"  [greenhouse:{slug}] skipped: {exc}")
            continue

        for job in jobs:
            location = (job.get("location") or {}).get("name", "").strip()
            title = (job.get("title") or "").strip()
            if not _IRELAND_RE.search(location):
                continue
            if not title_ok(title):
                continue
            level = classify_level(title)
            if level == "senior":
                continue

            listings.append({
                "title": title,
                "company": (job.get("company_name") or slug).strip(),
                "location": location,
                "url": job.get("absolute_url", ""),
                "posted_date": (job.get("updated_at") or "")[:10],
                "source": "Greenhouse",
                "level": level,
            })

    return listings
