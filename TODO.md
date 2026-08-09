# Task: Make Winner's project an "organization-verified" project

## Goal
Add an `is_winner` flag to the `PortfolioEntry` model (derived from `Submission.is_winner`),
expose it via the API (`PortfolioOut` + talent search), and display an "Organization Verified"
badge on the frontend for winning entries.

## Steps
- [x] 1. Add `is_winner` column to `PortfolioEntry` model (backend/app/models/portfolio.py)
- [x] 2. Add `is_winner` column to `portfolio_entries` migration (backend/migrations/versions/0001_initial_schema.py)
- [x] 3. Add `is_winner` field to `PortfolioOut` schema (backend/app/schemas/portfolio.py)
- [x] 4. Sync `is_winner` from submission in `_ensure_portfolio_entry` (backend/app/routers/submissions.py)
- [x] 5. Sync `is_winner` on portfolio entry in `select_winner` (backend/app/routers/challenges.py)
- [x] 6. Expose `is_winner` in talent search results (backend/app/routers/portfolio.py)
- [x] 7. Display "Organization Verified" badge on portfolio page (frontend/app/portfolio/page.tsx)
- [x] 8. Display "Organization Verified" badge on talent page (frontend/app/talent/page.tsx)
- [x] 9. Run backend tests to verify nothing breaks
