# TODO - Remove Employer Role & Enforce Submission Visibility

## Steps
- [x] Data check: found 1 employer test user (id 4, emp_dhfil@example.com), deleted it
- [x] Confirm plan with user
- [x] `models/user.py`: Remove `employer` from `UserRole` enum
- [x] `schemas/user.py`: Restrict `UserCreate.role` to `participant`/`organization`
- [x] `routers/submissions.py`:
  - `list_submissions`: participant → own; org → own challenges; admin → all
  - `get_report`: 403 unless admin / submitting participant / challenge-owning org
- [x] `register/page.tsx`: Remove employer from `roleMeta`
- [x] `page.tsx`: Update footer "Hire Talent" link to `/register?role=organization`
- [ ] Run existing test suite (test_flow.py, test_mvp_endpoints.py, etc.)
- [ ] Report pass/fail results
