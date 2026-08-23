# Ireland Cyber Job Agent

Automated job-alert agent that sweeps multiple sources every morning for
cybersecurity internships and entry-level roles in Ireland (Dublin/Cork
focus) and posts new openings to a Discord channel via webhook.

## Sources

| Source | What it covers | Cost |
|---|---|---|
| Google Jobs (via SerpApi) | Aggregates Indeed, IrishJobs.ie, LinkedIn, Built In Dublin, recruiter sites | 2 API searches/run |
| LinkedIn jobs (public guest endpoint) | Direct listings, incl. a dedicated internship/entry-level pass (`f_E=1,2,3`) | free |
| LinkedIn #hiring posts (Google index via SerpApi) | Hiring announcements posted as regular LinkedIn posts | 1 API search/run |
| **Greenhouse public boards** | Direct-from-employer roles (Stripe, Intercom, Datadog, Cloudflare, Udemy, Flipdish) | free, no key |
| **Cyber Ireland + infosec-conferences RSS** | Conferences, webinars, job fairs — posted to a separate events channel | free |

### Sources evaluated and rejected

Tested live and found unusable for Ireland — documented so they aren't retried:

- **GitHub internship trackers** (SimplifyJobs et al.): of 14,544 entries, **1**
  was a real Republic-of-Ireland role. "Ireland" matches are Dublin *Ohio*,
  Dublin *California*, or Northern Ireland.
- **Adzuna**: no Ireland index at all (API lists supported countries; `ie` absent).
- **Arbeitnow** (0 Ireland results), **IrishJobs.ie RSS** (403),
  **Meetup RSS** (404), **Lever/Ashby** (no valid Irish slugs found).

## How it works

```
job sources/*    →  filters: topic, location, seniority  →┐
                                                          ├→ SQLite dedup →  Discord
event sources/*  →  filters: event-vs-blog, region       →┘   (jobs channel +
                                                                events channel)
```

- **Topic filter**: broad cyber/security include regex; excludes
  physical-security noise (guards, patrols).
- **Seniority filter**: drops confirmed-senior titles (senior/lead/head/
  manager/architect/…); keeps unmarked titles since many entry-level roles
  aren't labelled; confirmed junior roles get a gold 🎓 embed.
- **Event filter**: keeps conferences/webinars/CTFs/job fairs, drops blog posts
  and past-event recaps; Ireland events flagged 🇮🇪, US-only dropped.
- **Dedup**: SHA-256 of normalized `company|title|location` (or permalink for
  LinkedIn posts and events), stored in `seen_jobs.db`, so the same job found via two
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
runs. Secrets (`SERPAPI_KEY`, `DISCORD_WEBHOOK_URL`,
`DISCORD_EVENTS_WEBHOOK_URL`) live in encrypted Actions secrets, never in
code. If `DISCORD_EVENTS_WEBHOOK_URL` is unset, events fall back to the jobs
channel.
