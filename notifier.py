import requests

from config import DISCORD_WEBHOOK_URL

COLOR_DEFAULT = 0x2ECC71  # green — regular listing
COLOR_JUNIOR = 0xF1C40F   # gold — confirmed intern/entry-level
COLOR_POST = 0x3498DB     # blue — LinkedIn #hiring post


def send_discord(listing):
    level = listing.get("level", "unknown")
    is_post = bool(listing.get("snippet"))

    if level == "junior":
        color, prefix = COLOR_JUNIOR, "🎓 "
    elif is_post:
        color, prefix = COLOR_POST, "📣 "
    else:
        color, prefix = COLOR_DEFAULT, ""

    fields = [
        {"name": "Company", "value": listing["company"] or "Unknown", "inline": True},
        {"name": "Location", "value": listing["location"] or "Ireland", "inline": True},
        {"name": "Source", "value": listing["source"] or "n/a", "inline": True},
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

    response = requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}, timeout=30)
    response.raise_for_status()
