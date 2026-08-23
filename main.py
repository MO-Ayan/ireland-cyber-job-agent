import time

import requests

from config import SOURCES
from notifier import send_discord
from sources import greenhouse, linkedin_posts, linkedin_public, rss_events, serpapi_jobs
from storage import SeenStore, dedup_key

# Jobs post to the jobs channel; events to the events channel. Both are plain
# functions returning a list of dicts, so they stay framework-agnostic.
JOB_SOURCES = {
    "linkedin": linkedin_public.fetch_listings,
    "google_jobs": serpapi_jobs.fetch_listings,
    "linkedin_posts": linkedin_posts.fetch_listings,
    "greenhouse": greenhouse.fetch_listings,
}

EVENT_SOURCES = {
    "events": rss_events.fetch_listings,
}

SOURCE_REGISTRY = {**JOB_SOURCES, **EVENT_SOURCES}


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
            # .get() because events carry no "company" key.
            label = listing.get("company") or listing.get("source") or "?"
            print(f"Failed to notify for {listing['title']} @ {label}: {exc}")
            return False
    return False


def main():
    all_listings = []
    for name in _selected_sources():
        try:
            found = SOURCE_REGISTRY[name]()
            kind = "events" if name in EVENT_SOURCES else "listings"
            print(f"[{name}] fetched {len(found)} {kind}")
            all_listings.extend(found)
        except Exception as exc:
            # One broken source must not kill the whole run.
            print(f"[{name}] FAILED: {exc}")

    unique = _dedupe_within_run(all_listings)
    print(f"{len(all_listings)} raw items, {len(unique)} unique this run.")

    store = SeenStore()
    new_jobs = new_events = 0
    try:
        for key, listing in unique:
            if not store.is_new(key):
                continue
            if _notify_with_retry(listing):
                if listing.get("kind") == "event":
                    new_events += 1
                else:
                    new_jobs += 1
                time.sleep(1)
            store.mark_seen(key)
    finally:
        store.close()

    print(f"Posted {new_jobs} new job(s) and {new_events} new event(s) to Discord.")


if __name__ == "__main__":
    main()
