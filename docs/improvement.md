# 🚨 🔴 CRITICAL CHANGES (Must Fix First)

---

## 1. Fix Background Task Reliability

### 📁 File: `planner_service.py`

### ❌ Current

```python
asyncio.create_task(_background_generate(...))
```

### ✅ Change

#### Option A (quick fix)

Add failure handling + status update:

```python
async def _background_generate(...):
    try:
        sections = await planner.generate_chapter_sections(...)

        await planner_repo.insert_sections(...)
        await update_chapter_status(chapter_id, "READY")

    except Exception as e:
        await update_chapter_status(chapter_id, "FAILED", error=str(e))
```

---

#### Option B (recommended for production)

Replace with:

- Celery OR Redis queue

---

### 🎯 Goal

- No silent failures
- Recoverable system

---

## 2. Fix Locking Scope (Race Condition Edge Case)

### 📁 File: `planner_service.py`

### ❌ Current

Lock is only in:

```python
sections_exist()
```

---

### ✅ Change

Wrap **entire generation trigger** in transaction:

```python
async with db.begin():
    chapter = await db.execute(
        select(Chapter)
        .where(Chapter.id == chapter_id)
        .with_for_update()
    )

    if await planner_repo.sections_exist(db, chapter_id):
        return await planner_repo.get_sections(db, chapter_id)

    chapter.status = "GENERATING"
```

---

### 🎯 Goal

- Only ONE generator runs per chapter

---

## 3. Ensure Safe Status Transitions

### 📁 File: `planner_service.py`

---

### ❌ Problem

Chapter can get stuck in `GENERATING`

---

### ✅ Change

Ensure:

```python
START TX
→ insert sections
→ update status = READY
COMMIT
```

---

### Also add:

```python
if exception:
    status = FAILED
```

---

### 🎯 Goal

State machine is always valid:

```text
NOT_STARTED → GENERATING → READY / FAILED
```

---

## 4. Add Polling Safety

### 📁 Frontend (ReadingMode / API hook)

---

### ❌ Current

- infinite polling

---

### ✅ Change

Add:

```js
maxRetries = 20
interval = 2 sec
```

Stop if:

- retries exceeded
- status = FAILED

---

### 🎯 Goal

- no infinite loops
- better UX

---

# 🟠 IMPORTANT CHANGES (Next Priority)

---

## 5. Improve Teacher Context Further

### 📁 File: `course_repo.py`

---

### ✅ Add:

```python
{
  "current_section": ...,
  "previous_summary": ...,
  "next_titles": ...,
  "position": f"{index+1}/{total_sections}",
  "completed_sections": index
}
```

---

### 🎯 Goal

- teacher becomes **progress-aware**

---

## 6. Strengthen JSON Validation

### 📁 File: `chapter_planner.py`

---

### ✅ Update validator:

```python
def validate_sections(data):
    if "sections" not in data:
        return False

    if not (3 <= len(data["sections"]) <= 4):
        return False

    for sec in data["sections"]:
        if not sec.get("title") or not sec.get("content"):
            return False

        word_count = len(sec["content"].split())
        if word_count < 400:
            return False

    return True
```

---

### 🎯 Goal

- no weak / broken outputs

---

## 7. Add Retry Limit Protection

### 📁 File: `chapter_planner.py`

---

### ✅ Add:

```python
MAX_RETRIES = 2
```

Log:

```python
logger.warning("Retry %d failed", attempt)
```

---

### 🎯 Goal

- control cost
- avoid infinite loops

---

## 8. Add Logging (Observability)

### 📁 File: `planner_service.py`

---

### ✅ Add logs:

```python
logger.info("Generating chapter: %s", chapter_id)
logger.info("Generation completed in %s sec", time_taken)
logger.warning("Retries used: %d", retries)
logger.error("Generation failed: %s", error)
```

---

### 🎯 Goal

- debug easily
- monitor system

---

# 🟡 OPTIONAL BUT HIGH VALUE

---

## 9. Add Generation Timeout

### 📁 File: `planner_service.py`

---

### ✅ Wrap LLM call:

```python
await asyncio.wait_for(
    planner.generate_chapter_sections(...),
    timeout=30
)
```

---

### 🎯 Goal

- prevent stuck requests

---

## 10. Add Section-Level Streaming (UX Upgrade)

### Idea:

- insert section 1 → show
- insert section 2 → append

---

### 🎯 Goal

- premium experience

---

## 11. Prepare for Image Support (Future-Proofing)

### 📁 File: `chapter_planner.py`

---

### ✅ Update schema (optional now):

```python
section = {
  "title": ...,
  "content": ...,
  "images": []
}
```

---

### 🎯 Goal

- easy upgrade later

---

# 🟢 NICE TO HAVE (Later)

---

## 12. Add Caching Layer

- Redis / DB cache

---

## 13. Add Versioning

- regenerate without overwrite

---

## 14. Add Metrics Dashboard

- success rate
- avg generation time

---

# 🏁 FINAL CHECKLIST

## 🔴 Must Do

- [ ] Fix background task failure handling
- [ ] Fix locking scope (chapter-level lock)
- [ ] Ensure status always resolves (READY / FAILED)
- [ ] Add polling limits

---

## 🟠 Should Do

- [ ] Improve teacher context (position + progress)
- [ ] Strengthen validation
- [ ] Limit retries
- [ ] Add logging

---

## 🟡 Good to Do

- [ ] Add timeout
- [ ] Prepare image support
- [ ] Improve UX streaming

---

# 🔥 FINAL TAKE

👉 Your system is already **architecturally strong**
👉 These changes will make it **production-safe + scalable**

---

If you want next, I can:

- ✅ Write **exact patched code for planner_service**
- ✅ Or review your **actual implementation diff**
- ✅ Or design **Celery integration (step-by-step)**
