import html
import re
import time

import requests

from config import LINKEDIN_EXPERIENCE_PASSES, LINKEDIN_KEYWORDS
from filters import classify_level, location_ok, title_ok

# Public no-login endpoint that backs linkedin.com/jobs guest search pages.
SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
PAGES_PER_KEYWORD = 2  # 10 results per page
PAST_WEEK = "r604800"  # f_TPR filter: posted in the last 7 days

_TITLE_RE = re.compile(r'base-search-card__title">\s*(.*?)\s*</h3>', re.S)
_COMPANY_RE = re.compile(r'base-search-card__subtitle">\s*<a[^>]*>\s*(.*?)\s*</a>', re.S)
_LOCATION_RE = re.compile(r'job-search-card__location">\s*(.*?)\s*</span>', re.S)
_LINK_RE = re.compile(r'href="(https://[^"]*linkedin\.com/jobs/view/[^"?]+)')
_DATE_RE = re.compile(r'datetime="([\d-]+)"')


def _parse_card(chunk):
    title = _TITLE_RE.search(chunk)
    link = _LINK_RE.search(chunk)
    if not (title and link):
        return None
    company = _COMPANY_RE.search(chunk)
    location = _LOCATION_RE.search(chunk)
    posted = _DATE_RE.search(chunk)
    return {
        "title": html.unescape(title.group(1)).strip(),
        "company": html.unescape(company.group(1)).strip() if company else "Unknown",
        "location": html.unescape(location.group(1)).strip() if location else "Ireland",
        "url": link.group(1),
        "posted_date": posted.group(1) if posted else "",
        "source": "LinkedIn",
    }


def fetch_listings():
    listings = []
    for experience in LINKEDIN_EXPERIENCE_PASSES:
        for keyword in LINKEDIN_KEYWORDS:
            for page in range(PAGES_PER_KEYWORD):
                params = {
                    "keywords": keyword,
                    "location": "Ireland",
                    "f_TPR": PAST_WEEK,
                    "start": page * 10,
                }
                if experience:
                    params["f_E"] = experience
                response = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=30)
                if response.status_code != 200:
                    # Guest endpoint throttles with 429s; skip to next keyword
                    # rather than hammering it.
                    break

                cards = response.text.split("<li")[1:]
                for chunk in cards:
                    listing = _parse_card(chunk)
                    if not listing:
                        continue
                    if not (title_ok(listing["title"]) and location_ok(listing["location"])):
                        continue
                    level = classify_level(listing["title"])
                    if level == "senior":
                        continue
                    listing["level"] = level
                    listings.append(listing)

                if len(cards) < 10:
                    break  # no further pages
                time.sleep(1.5)

    return listings
