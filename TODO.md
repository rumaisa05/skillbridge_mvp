# Task TODO

1. ✅ Fix footer "Post a Challenge" link in `frontend/app/page.tsx` (conditional on role).
2. ✅ Broaden talent search (`backend/app/routers/portfolio.py`) to include non-winning AI-evaluated candidates; update docstring. Update `frontend/app/talent/page.tsx` footer text based on `is_winner`.
3. ✅ Add org-specific profile fields (`org_type`, `website`):
   - ✅ `backend/app/models/user.py`
   - ✅ new migration `0003_add_org_profile_fields.py`
   - ✅ `backend/app/schemas/user.py` (UserOut/UserUpdate)
   - ✅ `frontend/app/profile/page.tsx` org-appropriate fields
4. ✅ Normalize skills shape in localStorage in `frontend/app/profile/page.tsx` save().
5. ✅ Remove "Demo" labels from homepage stat counters in `frontend/app/page.tsx`.
6. ✅ Rebuild `backend/app/seed.py` with realistic interconnected demo data:
   - ✅ 5 organizations (ngo/school/hospital/startup/company) with org_type + website
   - ✅ 8 participants with distinct skills/bios, incl. Richard (multi-submission)
   - ✅ 10 challenges (2 per org), each with 3 submissions
   - ✅ All 30 submissions run through real `evaluate_submission()` → real AIReports
   - ✅ 5 winners selected (one challenge per org) via `_select_winner` (replicates `select_winner()`)
   - ✅ Mix: 5 Organization-Verified winners + 25 AI-Evaluated non-winners
   - ✅ All accounts marked `[Demo account]` + `*.skillbridge.test` emails
   - ✅ Verified: challenges page populated, talent search shows verified + AI-evaluated, Richard has both winning & non-winning portfolio entries

Follow-up:
- ✅ Backend tests: 6 passed (pytest --ignore=test_flow.py)
- ✅ Frontend typecheck: npx tsc --noEmit (exit 0)
- ✅ Local DB reset + reseeded (skillbridge.db) with correct winner/non-winner mix
