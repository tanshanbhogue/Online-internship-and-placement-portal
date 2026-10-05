# Internship & Placement Preparation Portal

A web platform that helps students prepare for placements and internships in one place: browse and apply to internship listings, practice aptitude/technical/coding questions, take timed mock tests, and track their progress through personal analytics.

---

## Table of Contents

- [Features](#features)
- [Requirements Overview](#requirements-overview)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Testing & Acceptance Criteria](#testing--acceptance-criteria)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Area | Description |
|------|-------------|
| **Authentication** | Student registration, login, and per-session authentication |
| **Internship Listings** | View listings posted by admin and apply with one click; duplicate applications are blocked |
| **My Applications** | Track every internship you've applied to |
| **Practice Question Bank** | Categorized aptitude, technical MCQs, and coding problems with scored results |
| **Timed Mock Tests** | Real-test simulation with auto-submit at the time limit and detailed answer analysis |
| **Personal Analytics** | Performance trends and strengths/weaknesses based on test and practice history |

---

## Requirements Overview

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | Student registration, login, and session authentication | High |
| FR-002 | View admin-posted internships and apply (no duplicate applications) | High |
| FR-003 | Practice aptitude, technical MCQs, and coding problems from a categorized bank | High |
| FR-004 | Timed mock tests with results and detailed answer analysis | Medium |
| FR-005 | Personal analytics summary (trends, strengths/weaknesses) | Medium |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-001 | Respond to user actions within 2 seconds under normal load (95th percentile) | High |
| NFR-002 | Hashed passwords, encrypted storage, and HTTPS for all data in transit | High |
| NFR-003 | Works on Chrome, Firefox, and Edge across desktop, tablet, and mobile | Medium |

---

## Tech Stack

> Update this section to match your implementation.

- **Frontend:** _e.g., React / HTML, CSS, JavaScript_
- **Backend:** _e.g., Node.js + Express / Django / Spring Boot_
- **Database:** _e.g., MySQL / PostgreSQL / MongoDB_
- **Auth:** _e.g., JWT / session-based with bcrypt password hashing_
- **Hosting:** _e.g., Render / Vercel / AWS_

---

## Getting Started

### Prerequisites

- Node.js (v18+) and npm _(or your stack's equivalent)_
- A running database instance
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

# 2. Install dependencies
npm install

# 3. Configure environment variables
cp .env.example .env
# then edit .env with your values

# 4. Run the development server
npm run dev
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `PORT` | Port the server runs on |
| `DATABASE_URL` | Database connection string |
| `JWT_SECRET` | Secret used to sign auth tokens |

---

## Project Structure

```
.
├── client/            # Frontend (UI, pages, components)
├── server/            # Backend (routes, controllers, models)
│   ├── auth/          # Registration, login, session handling
│   ├── internships/   # Listings and applications
│   ├── questions/     # Question bank and practice
│   ├── tests/         # Mock tests and scoring
│   └── analytics/     # Performance summaries
├── docs/              # SRS and other documentation
├── .env.example
└── README.md
```

---

## Usage

**Students**
1. Register and log in to reach your dashboard.
2. Browse internship listings and apply; check status under **My Applications**.
3. Pick a category in the question bank and practice with instantly scored results.
4. Take a timed mock test and review the answer breakdown afterward.
5. Open the analytics dashboard to see trends and focus areas.

**Admins**
- Post and manage internship listings.
- Manage the categorized question bank.

---

## Testing & Acceptance Criteria

| Req | Pass condition |
|-----|----------------|
| FR-001 | Valid credentials open the profile dashboard; invalid credentials show an error |
| FR-002 | Application appears under "My Applications"; duplicates are blocked |
| FR-003 | Chosen category returns relevant questions with a scored result |
| FR-004 | Test auto-submits at the time limit and shows score plus correct/incorrect breakdown |
| FR-005 | Dashboard reflects updated scores after every new attempt |
| NFR-001 | 95% of requests complete within 2 seconds |
| NFR-002 | Passwords stored hashed; all traffic over HTTPS |
| NFR-003 | Core features usable on Chrome, Firefox, Edge across desktop, tablet, and mobile |

Run the test suite:

```bash
npm test
```

---

## Roadmap

- [ ] FR-001: Authentication
- [ ] FR-002: Internship listings & applications
- [ ] FR-003: Practice question bank
- [ ] FR-004: Timed mock tests
- [ ] FR-005: Personal analytics
- [ ] NFR validation: performance, security, cross-browser

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

Distributed under the MIT License. See `LICENSE` for details.
