# 🔴 CRITICAL ERRORS (Must Fix)

---

## 1. ❌ Non-Atomic Locking (Race Condition Still Possible)

**Where:** `planner_service.py`

**Problem:**

- `with_for_update()` is used, but not wrapped with status update in same transaction
- Two requests can still trigger generation

**Impact:**

- Duplicate LLM calls
- DB conflicts
- Wasted cost

---

## 2. ❌ Background Task Not Persistent

**Where:** `_background_generate()`

**Problem:**

- Uses in-process async task
- If server restarts → task dies

**Impact:**

- Chapter stuck in `GENERATING`
- No recovery

---

## 3. ❌ No Recovery for Stuck GENERATING State

**Where:** System-wide

**Problem:**

- If task crashes mid-way → status never changes

**Impact:**

- User stuck forever
- Polling keeps running

---

## 4. ❌ No Retry Mechanism for FAILED Chapters

**Where:** API layer

**Problem:**

- Once `FAILED`, no way to regenerate

**Impact:**

- Dead-end UX

---

## 5. ❌ Partial Transaction Risk

**Where:** Section insert + status update

**Problem:**

- Insert sections and status update not guaranteed atomic

**Impact:**

- Sections saved but status not updated (or vice versa)

---

# 🟠 HIGH PRIORITY ISSUES

---

## 6. ❌ Polling Mismatch (Frontend vs Backend)

**Problem:**

- Backend timeout = 90s
- Frontend polling = 120s

**Impact:**

- Extra useless requests
- inconsistent UX

---

## 7. ❌ No Polling Exit on FAILED

**Where:** Frontend (`ReadingMode.jsx`)

**Problem:**

- Polling continues even if backend returns FAILED

**Impact:**

- Infinite retry loop (soft)

---

## 8. ❌ Weak JSON Validation for Images

**Where:** `chapter_planner.py`

**Problem:**

- `"images"` field not validated

**Impact:**

- LLM may break structure
- parsing errors later

---

## 9. ❌ No Generation Timeout Recovery Handling

**Problem:**

- Timeout triggers exception
- but system does not ensure clean fallback everywhere

**Impact:**

- inconsistent FAILED handling

---

## 10. ❌ No Rate Limiting

**Problem:**

- User can spam generation endpoint

**Impact:**

- cost explosion
- system overload

---

# 🟡 MEDIUM ISSUES

---

## 11. ❌ No Observability / Logging Depth

**Problem:**

- Missing:
  - generation time
  - retry count
  - failure reasons tracking

**Impact:**

- debugging becomes hard
- no system insights

---

## 12. ❌ Teacher Context Still Incomplete

**Problem:**

- Only `position` added
- Missing:
  - completed sections count
  - learning progress

**Impact:**

- less adaptive teaching

---

## 13. ❌ No UI Error State

**Where:** Frontend

**Problem:**

- No proper error screen for FAILED

**Impact:**

- poor UX

---

## 14. ❌ No Safeguard on Retry Count (LLM)

**Problem:**

- Retry logic exists but no global control

**Impact:**

- potential cost spike

---

# 🟢 LOW PRIORITY / FUTURE RISKS

---

## 15. ❌ No Caching

**Impact:**

- repeated LLM calls
- higher cost

---

## 16. ❌ No Versioning of Generated Content

**Impact:**

- cannot regenerate safely

---

## 17. ❌ No Section Streaming

**Impact:**

- UX could be improved

---

## 18. ❌ No Image Pipeline Yet (Only Schema)

**Impact:**

- feature incomplete

---

# 🏁 FINAL SUMMARY

## 🔴 Critical (Fix Immediately)

- Locking not atomic
- Background tasks not persistent
- No recovery for GENERATING
- No retry endpoint
- Non-atomic DB writes

---

## 🟠 High Priority

- Polling mismatch
- No FAILED handling in UI
- Weak validation (images)
- No rate limiting

---

## 🟡 Medium

- Logging missing
- Teacher context incomplete
- No error UI
- Retry limits weak

---

## 🟢 Low

- No caching
- No versioning
- No streaming
- Image system incomplete

---

# 🔥 Final Truth

👉 Your system is **stable but not fully production-safe yet**
👉 Most issues are **edge-case failures**, not core design problems
