# Ireland Cyber Job Agent

Automated job-alert agent that sweeps multiple sources every morning for
cybersecurity internships and entry-level roles in Ireland (Dublin/Cork
focus) and posts new openings to a Discord channel via webhook.

## Sources

| Source | What it covers | Cost |
|---|---|---|
| Google Jobs (via SerpApi) | Aggregates Indeed, IrishJobs.ie, LinkedIn, Built In Dublin, recruiter sites and more | 2 API searches/run |
| LinkedIn jobs (public guest endpoint) | Direct listings, incl. a dedicated internship/entry-level pass (`f_E=1,2,3`) | free |
| LinkedIn #hiring posts (Google index via SerpApi) | Hiring announcements people post as regular LinkedIn posts | 1 API search/run |

## How it works

```
sources/*  →  filters (topic, location, seniority)  →  SQLite dedup  →  Discord webhook
```

- **Topic filter**: broad cyber/security include regex; excludes
  physical-security noise (guards, patrols).
- **Seniority filter**: drops confirmed-senior titles (senior/lead/head/
  manager/architect/…); keeps unmarked titles since many entry-level roles
  aren't labelled; confirmed junior roles get a gold 🎓 embed.
- **Dedup**: SHA-256 of normalized `company|title|location` (or post URL for
  LinkedIn posts), stored in `seen_jobs.db`, so the same job found via two
  sources — or on two different days — only notifies once.

## Running locally

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in SERPAPI_KEY and DISCORD_WEBHOOK_URL
python main.py
```

`SOURCES` env var selects sources for a run: `all` (default) or a
comma-separated subset, e.g. `SOURCES=linkedin`.

## Scheduling

GitHub Actions (`.github/workflows/daily-sweep.yml`) runs the full sweep
once daily at 06:30 UTC (07:30 Irish summer time / 06:30 winter) and commits
the updated `seen_jobs.db` back to the repo so dedup state persists between
runs. Secrets (`SERPAPI_KEY`, `DISCORD_WEBHOOK_URL`) live in encrypted
Actions secrets, never in code.
