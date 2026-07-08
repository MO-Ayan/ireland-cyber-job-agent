import os

from dotenv import load_dotenv

load_dotenv()

# Each SerpApi query costs 1 search from the free monthly quota (~100).
# Budget: 2 job queries + 1 LinkedIn-posts query per daily full run = 90/month.
# Google Jobs matches semantically, so "cyber security jobs" already surfaces
# analyst/engineer/pentest/intern variants.
SERPAPI_QUERIES = [
    "cyber security jobs",
    "security analyst jobs",
]

# LinkedIn guest endpoint is free — can afford more keyword variety here.
LINKEDIN_KEYWORDS = [
    "cyber security",
    "security analyst",
    "penetration tester",
    "SOC analyst",
    "information security",
    "cloud security",
]

# Two passes per keyword: first with LinkedIn's own experience filter
# (1=internship, 2=entry level, 3=associate) so junior roles aren't crowded
# out of the 10-per-page window by senior ones; second unfiltered to catch
# roles the poster mislabeled (client-side seniority regex handles those).
LINKEDIN_EXPERIENCE_PASSES = ["1,2,3", None]

# Cities that count as a match. Listings located just "Ireland" (country-wide
# or remote) are also accepted — see filters.location_ok.
LOCATIONS = ["Dublin", "Cork"]

SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

DB_PATH = os.environ.get("JOB_AGENT_DB_PATH", "seen_jobs.db")

# Comma-separated source names to run this invocation ("all" = every source).
# Lets the scheduler run free sources hourly but quota-limited ones daily.
SOURCES = os.environ.get("SOURCES", "all")
