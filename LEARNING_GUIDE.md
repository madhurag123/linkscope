# LinkScope — learning guide

## What it does

URL shortener with campaign analytics. The intended user is small campaign teams. Browser controls → validated Flask API → project analysis/workflow → results and export.

## Run and demonstrate

Follow the README installation block, then: Create a link to https://example.org/docs with alias docs-demo. Open its /s/docs-demo URL in another tab, refresh the dashboard, and inspect the new UTC-day count. Duplicate aliases are rejected.

## Important files

- `app.py` — local HTTP interface and request/error handling.
- `core.py` — project-specific logic.
- `tests/` — regression and correctness checks.
- `reports/` — recorded outputs and verification evidence.

## Three engineering decisions

1. SQLite transactions keep aliases unique and increment aggregate clicks atomically.
2. Store UTC day and referrer host only; visitor identifiers and full referrer URLs are discarded.
3. Accept only HTTP(S) destinations and enforce expiration at redirect time.

## Five interview questions

1. **How does a redirect become an analytics event?** The resolver validates the stored link, increments an aggregate row keyed by alias, UTC day and referrer host, then returns the destination. SQLite keeps the read and increment transactional.

2. **Why not store every visitor?** The dashboard only needs aggregate usage. Omitting IP addresses and full referrer URLs reduces retained personal data; it also means unique visitors and individual journeys cannot be measured.

3. **What prevents two links from sharing an alias?** The alias is the database primary key. An integrity error becomes a useful conflict message, so concurrent attempts cannot silently overwrite a destination.

4. **How are unsafe destinations and exports handled?** Destinations must be HTTP(S), have a hostname, and contain no embedded credentials. CSV output prefixes formula-like text so a campaign name cannot become a spreadsheet formula.

5. **What would public deployment require?** Add authenticated management, abuse reporting, rate limits and destination review. The local app is deliberately not presented as an abuse-resistant public shortening service.

## Independent exercise

Add a campaign filter to the analytics query and prove its totals reconcile to the unfiltered result.

Write down the expected behavior before editing. Add a meaningful regression check, run the existing suite, and describe what changed in your own words.

## Contribution and resume guidance

The implementation was developed with substantial AI assistance under Abhijith Viswanathan's direction. The verified contribution is the working artifact and the learning work actually completed, not invented employment or adoption.

Suggested factual bullet after personally validating the demo:

- Built a transactional SQLite URL shortener with expiring aliases, aggregate click analytics and spreadsheet-safe CSV export; verified 15 regression and API checks.

Use [VERIFICATION.md](VERIFICATION.md) to add only measured numbers. Do not claim production traffic, users, savings, upstream acceptance or cloud deployment without corresponding evidence.
