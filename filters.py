import re

from config import LOCATIONS

# Broad on purpose: the user wants volume, so anything security-adjacent passes.
_INCLUDE_TITLE_RE = re.compile(
    r"cyber|security|infosec|\bsoc\b|pentest|penetration|red team|appsec"
    r"|grc|threat|vulnerab|incident|forensic|siem|\biam\b",
    re.IGNORECASE,
)

# Physical-security noise that "security jobs" queries drag in.
_EXCLUDE_TITLE_RE = re.compile(
    r"security guard|static guard|door supervisor|retail security"
    r"|event security|mobile patrol",
    re.IGNORECASE,
)


def title_ok(title):
    if _EXCLUDE_TITLE_RE.search(title):
        return False
    return bool(_INCLUDE_TITLE_RE.search(title))


# Confirmed junior markers win over senior markers ("Graduate Programme -
# Security Leadership Track" is still junior).
_JUNIOR_RE = re.compile(
    r"\bintern(ship)?\b|graduate|junior|entry.level|entry level|trainee"
    r"|placement|apprentice|early careers?|\blevel 1\b|\bl1\b",
    re.IGNORECASE,
)

_SENIOR_RE = re.compile(
    r"\bsenior\b|\bsr\.?\b|\blead(er)?\b|principal|\bstaff\b|head of|\bhead\b"
    r"|director|manager|\bchief\b|architect|\bvp\b|vice president|executive|\bciso\b",
    re.IGNORECASE,
)


def classify_level(title):
    """'junior' = confirmed entry/intern, 'senior' = drop it, 'unknown' = keep
    (many entry-level roles carry no seniority marker in the title)."""
    if _JUNIOR_RE.search(title):
        return "junior"
    if _SENIOR_RE.search(title):
        return "senior"
    return "unknown"


def location_ok(location):
    loc = location.lower()
    if any(city.lower() in loc for city in LOCATIONS):
        return True
    # Country-level listings are usually remote or unspecified-Dublin;
    # keep them rather than lose real openings.
    return "remote" in loc or loc.strip() in ("ireland", "republic of ireland")


# --- Events (conferences, webinars, job fairs, CTFs) ---

_EVENT_RE = re.compile(
    r"conference|webinar|summit|meetup|symposium|workshop|bootcamp|hackathon"
    r"|\bctf\b|careers? fair|job fair|expo|briefing|training day|open day"
    r"|\bcfp\b|call for papers",
    re.IGNORECASE,
)

# Past-tense recaps ("Webinar Highlights | ...") are write-ups, not things
# you can still attend.
_EVENT_RECAP_RE = re.compile(
    r"highlights|recap|round.?up|takeaways|wrap.?up|\bwas held\b|report from",
    re.IGNORECASE,
)

_IRELAND_RE = re.compile(
    r"ireland|dublin|\bcork\b|galway|limerick|waterford|dundalk|belfast",
    re.IGNORECASE,
)
_EUROPE_RE = re.compile(
    r"europe|\beu\b|\buk\b|london|amsterdam|netherlands|berlin|germany|paris"
    r"|france|spain|portugal|lisbon|madrid|italy|rome|nordic|online|virtual|remote",
    re.IGNORECASE,
)
_US_ONLY_RE = re.compile(
    r"\busa\b|united states|\bu\.s\.|las vegas|san francisco|new york|orlando"
    r"|washington|texas|california|florida|toronto|canada",
    re.IGNORECASE,
)


def event_ok(title, description="", categories=()):
    """Keep genuine upcoming events; drop blog posts and past-event recaps."""
    if _EVENT_RECAP_RE.search(title):
        return False
    # Cyber Ireland tags real events with an "Events" category — trust it.
    if any("event" in str(c).lower() for c in categories):
        return True
    return bool(_EVENT_RE.search(title) or _EVENT_RE.search(description))


def event_region(text):
    """'ireland' | 'europe' | 'other' — used to flag local events and to drop
    US-only ones. Inclusive by design: anything not clearly US-only that
    mentions Europe/online counts as reachable."""
    if _IRELAND_RE.search(text):
        return "ireland"
    if _EUROPE_RE.search(text):
        return "europe"
    if _US_ONLY_RE.search(text):
        return "other"
    # Unknown location: keep it rather than risk missing an opportunity.
    return "europe"
