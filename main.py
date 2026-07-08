import time

import requests

from config import SOURCES
from notifier import send_discord
from sources import linkedin_posts, linkedin_public, serpapi_jobs
from storage import SeenStore, dedup_key

SOURCE_REGISTRY = {
    "linkedin": linkedin_public.fetch_listings,
    "google_jobs": serpapi_jobs.fetch_listings,
    "linkedin_posts": linkedin_posts.fetch_listings,
}


def _selected_sources():
    if SOURCES.strip().lower() == "all":
        return list(SOURCE_REGISTRY)
    return [name.strip() for name in SOURCES.split(",") if name.strip() in SOURCE_REGISTRY]


def _dedupe_within_run(all_listings):
    seen_keys = set()
    unique = []
    for listing in all_listings:
        key = dedup_key(listing)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique.append((key, listing))
    return unique


def _notify_with_retry(listing, max_retries=3):
    for attempt in range(max_retries):
        try:
            send_discord(listing)
            return True
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 429 and attempt < max_retries - 1:
                retry_after = float(exc.response.headers.get("Retry-After", 1))
                time.sleep(retry_after)
                continue
            print(f"Failed to notify for {listing['title']} @ {listing['company']}: {exc}")
            return False
    return False


def main():
    all_listings = []
    for name in _selected_sources():
        try:
            found = SOURCE_REGISTRY[name]()
            print(f"[{name}] fetched {len(found)} listings")
            all_listings.extend(found)
        except Exception as exc:
            # One broken source must not kill the whole run.
            print(f"[{name}] FAILED: {exc}")

    unique = _dedupe_within_run(all_listings)
    print(f"{len(all_listings)} raw listings, {len(unique)} unique this run.")

    store = SeenStore()
    new_count = 0
    try:
        for key, listing in unique:
            if not store.is_new(key):
                continue
            if _notify_with_retry(listing):
                new_count += 1
                time.sleep(1)
            store.mark_seen(key)
    finally:
        store.close()

    print(f"Posted {new_count} new listing(s) to Discord.")


if __name__ == "__main__":
    main()
