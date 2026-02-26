## 2026-02-26 — Issue #35: Add option to exclude 3xx status codes from email notifications

Add a boolean CLI flag that, when present, includes links with HTTP 3xx status codes in the email notification.

- The flag controls email content only — the CSV output must still list all 3xx links regardless.
- Default behaviour (flag absent): 3xx links are excluded from the email notification.
- Flag present: 3xx links are included in the email notification alongside other non-200 results.
