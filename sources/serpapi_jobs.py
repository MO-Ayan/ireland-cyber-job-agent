import requests

from config import SERPAPI_KEY, SERPAPI_QUERIES
from filters import classify_level, location_ok, title_ok

SEARCH_URL = "https://serpapi.com/search"


def fetch_listings():
    listings = []
    for query in SERPAPI_QUERIES:
        params = {
            "engine": "google_jobs",
            "q": query,
            "location": "Ireland",
            "hl": "en",
            "api_key": SERPAPI_KEY,
        }
        response = requests.get(SEARCH_URL, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        for job in data.get("jobs_results", []):
            title = job.get("title", "").strip()
            location = job.get("location", "").strip() or "Ireland"
            if not title_ok(title) or not location_ok(location):
                continue
            level = classify_level(title)
            if level == "senior":
                continue

            apply_options = job.get("apply_options") or []
            url = apply_options[0].get("link", "") if apply_options else job.get("share_link", "")
            if not url:
                continue

            listings.append({
                "title": title,
                "company": (job.get("company_name") or "Unknown").strip(),
                "location": location,
                "url": url,
                "posted_date": (job.get("detected_extensions") or {}).get("posted_at", ""),
                "source": job.get("via") or "Google Jobs",
                "level": level,
            })

    return listings
