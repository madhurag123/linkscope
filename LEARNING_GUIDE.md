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

1. **What problem does this project solve, and what is its unit of work?** Explain url shortener with campaign analytics, identify small campaign teams as the audience, and trace one concrete example through the files above. Use the demonstration output rather than hypothetical impact.
2. **Why did you choose the first design decision?** SQLite transactions keep aliases unique and increment aggregate clicks atomically. Show the corresponding implementation and a test that would fail if that property were removed.
3. **How do you protect correctness when inputs or execution change?** Store UTC day and referrer host only; visitor identifiers and full referrer URLs are discarded. Explain the relevant invalid-input or edge-case test and distinguish a checked property from an untested assumption.
4. **How do you make results inspectable and reproducible?** Accept only HTTP(S) destinations and enforce expiration at redirect time. Point to actual outputs and recorded commands. Explain why a successful example is weaker evidence than a tested boundary or independently reconciled total.
5. **What would you improve before real deployment or real-data use?** Local single-user administration; no accounts, custom domains, abuse detection, bot filtering or unique-visitor estimates. A click count is a request count, not a human count. Choose one limitation, describe the missing evidence, and propose a measurable acceptance check rather than promising production readiness.

## Independent exercise

Add a campaign filter to the analytics query and prove its totals reconcile to the unfiltered result.

Write down the expected behavior before editing. Add a meaningful regression check, run the existing suite, and describe what changed in your own words.

## Contribution and resume guidance

The implementation was developed with substantial AI assistance under Abhijith Viswanathan's direction. The verified contribution is the working artifact and the learning work actually completed, not invented employment or adoption.

Suggested factual bullet after personally validating the demo:

- Implemented and validated url shortener with campaign analytics using Flask · SQLite, with validated links and documented correctness checks and limitations.

Use [VERIFICATION.md](VERIFICATION.md) to add only measured numbers. Do not claim production traffic, users, savings, upstream acceptance or cloud deployment without corresponding evidence.
