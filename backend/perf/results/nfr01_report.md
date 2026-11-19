# NFR-001 performance run

- Date: 18 November 2026   Build: a990a2f   Mode: managed
- Environment: Python 3.11.9, Windows 10
- Normal load used: 10 concurrent users, requests sent back to back (no think time), 30 requests per user per case
- Pass rule: at least 95% of requests within 2000 ms, no errors, no timeouts

| Case | Name | Requests | p50 ms | p95 ms | Max ms | Within 2 s | Errors | Result |
|---|---|---:|---:|---:|---:|---:|---:|---|
| PT-N01_01 | Login response time | 300 | 534 | 681 | 853 | 100.0% | 0 | Pass |
| PT-N01_02 | Internship listings page load | 300 | 91 | 158 | 212 | 100.0% | 0 | Pass |
| PT-N01_03 | Listings filter and search | 300 | 93 | 136 | 228 | 100.0% | 0 | Pass |
| PT-N01_04 | Application submission | 300 | 110 | 155 | 194 | 100.0% | 0 | Pass |
| PT-N01_05 | Start a mock test | 300 | 28 | 263 | 4841 | 99.0% | 0 | Pass |
| PT-N01_06 | Mock test submission | 300 | 79 | 462 | 6992 | 97.7% | 0 | Pass |
| PT-N01_07 | Analytics dashboard load | 1200 | 106 | 162 | 227 | 100.0% | 0 | Pass |
| PT-N01_08 | Overall 95th percentile under normal load | 1480 | 89 | 285 | 1179 | 100.0% | 0 | Pass |

Overall: **Pass**
