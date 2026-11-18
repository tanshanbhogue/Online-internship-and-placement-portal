# NFR-001 performance run

- Date: 18 November 2026   Build: a990a2f   Mode: managed
- Environment: Python 3.11.9, Windows 10
- Normal load used: 10 concurrent users, requests sent back to back (no think time), 30 requests per user per case
- Pass rule: at least 95% of requests within 2000 ms, no errors, no timeouts

| Case | Name | Requests | p50 ms | p95 ms | Max ms | Within 2 s | Errors | Result |
|---|---|---:|---:|---:|---:|---:|---:|---|
| PT-N01_01 | Login response time | 300 | 463 | 656 | 983 | 100.0% | 0 | Pass |
| PT-N01_02 | Internship listings page load | 300 | 75 | 108 | 128 | 100.0% | 0 | Pass |
| PT-N01_03 | Listings filter and search | 300 | 62 | 101 | 124 | 100.0% | 0 | Pass |
| PT-N01_04 | Application submission | 300 | 124 | 573 | 2266 | 99.7% | 0 | Pass |
| PT-N01_05 | Start a mock test | 300 | 146 | 1108 | 5830 | 98.3% | 0 | Pass |
| PT-N01_06 | Mock test submission | 300 | 291 | 1817 | 6494 | 94.3% | 3 | Fail |
| PT-N01_07 | Analytics dashboard load | 1200 | 85 | 121 | 158 | 100.0% | 0 | Pass |
| PT-N01_08 | Overall 95th percentile under normal load | 1480 | 70 | 243 | 1264 | 100.0% | 0 | Pass |

Overall: **Fail**
