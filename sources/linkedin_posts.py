import requests

from config import SERPAPI_KEY

# Hashtag hiring posts: LinkedIn post search needs a login, but Google
# indexes public posts, so we search Google (via SerpApi) instead.
SEARCH_URL = "https://serpapi.com/search"

QUERY = (
    'site:linkedin.com/posts ("hiring" OR "we are hiring" OR "#hiring") '
    '("cyber security" OR cybersecurity OR "security analyst" OR "SOC" OR "infosec") '
    "(Ireland OR Dublin OR Cork)"
)


def fetch_listings():
    params = {
        "engine": "google",
        "q": QUERY,
        "tbs": "qdr:w",  # posted within the past week
        "num": 20,
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }
    response = requests.get(SEARCH_URL, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()

    listings = []
    for result in data.get("organic_results", []):
        url = result.get("link", "")
        if "linkedin.com/posts/" not in url:
            continue
        listings.append({
            "title": result.get("title", "LinkedIn hiring post").strip(),
            "company": "LinkedIn post",
            "location": "Ireland",
            "url": url,
            "posted_date": result.get("date", ""),
            "source": "LinkedIn #hiring post",
            "snippet": result.get("snippet", ""),
            # Post titles repeat ("X's Post"), so dedup on the post URL
            # (activity ID) instead of company+title+location.
            "dedup_id": url.split("?")[0],
            "level": "unknown",
        })

    return listings
