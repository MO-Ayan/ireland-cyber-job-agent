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
