import requests

from config import DISCORD_EVENTS_WEBHOOK_URL, DISCORD_WEBHOOK_URL

COLOR_DEFAULT = 0x2ECC71  # green — regular listing
COLOR_JUNIOR = 0xF1C40F   # gold — confirmed intern/entry-level
COLOR_POST = 0x3498DB     # blue — LinkedIn #hiring post
COLOR_EVENT = 0x9B59B6    # purple — conference / job fair


def _event_embed(listing):
    prefix = "🇮🇪 " if listing.get("region") == "ireland" else "🎤 "
    fields = [
        {"name": "Where", "value": listing["location"] or "TBC", "inline": True},
        {"name": "Source", "value": listing["source"] or "n/a", "inline": True},
    ]
    if listing.get("posted_date"):
        fields.append({"name": "Announced", "value": str(listing["posted_date"]), "inline": True})
    embed = {
        "title": (prefix + listing["title"])[:256],
        "url": listing["url"],
        "color": COLOR_EVENT,
        "fields": fields,
    }
    if listing.get("snippet"):
        embed["description"] = listing["snippet"][:400]
    return embed


def _job_embed(listing):
    level = listing.get("level", "unknown")
    is_post = bool(listing.get("snippet"))

    if level == "junior":
        color, prefix = COLOR_JUNIOR, "🎓 "
    elif is_post:
        color, prefix = COLOR_POST, "📣 "
    else:
        color, prefix = COLOR_DEFAULT, ""

    fields = [
        {"name": "Company", "value": listing.get("company") or "Unknown", "inline": True},
        {"name": "Location", "value": listing.get("location") or "Ireland", "inline": True},
        {"name": "Source", "value": listing.get("source") or "n/a", "inline": True},
    ]
    if listing.get("posted_date"):
        fields.append({"name": "Posted", "value": str(listing["posted_date"]), "inline": True})

    embed = {
        "title": (prefix + listing["title"])[:256],
        "url": listing["url"],
        "color": color,
        "fields": fields,
    }
    if is_post:
        embed["description"] = listing["snippet"][:400]
    return embed


def send_discord(listing, webhook_url=None):
    """Events route to the events channel by default; jobs to the jobs channel.
    Pass webhook_url to override."""
    is_event = listing.get("kind") == "event"
    if webhook_url is None:
        webhook_url = DISCORD_EVENTS_WEBHOOK_URL if is_event else DISCORD_WEBHOOK_URL

    embed = _event_embed(listing) if is_event else _job_embed(listing)
    response = requests.post(webhook_url, json={"embeds": [embed]}, timeout=30)
    response.raise_for_status()
