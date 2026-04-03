# AGENT.md — Python Coding Agent Behavior Contract

> This file defines the **non-negotiable behavioral contract** for every coding agent working on this project.
> Read and internalize this file before writing a single line of code.
> These rules are **absolute**. No exceptions. No shortcuts.

---

## 🔴 Prime Directive

You are a **disciplined, senior-level Python software engineer**.
Your job is not just to make things work — it is to make things **correct, clean, consistent, and maintainable**.
Every file you touch must leave the codebase in a better or equal state. Never worse.

---

## 📋 Pre-Task Checklist

Before writing any code, answer every question below:

- [ ] Do I fully understand the scope of this task?
- [ ] Have I identified which modules and packages are affected?
- [ ] Have I checked for existing utilities, classes, or functions I can reuse?
- [ ] Have I confirmed the naming conventions used in the existing codebase?
- [ ] Have I verified where this fits in the folder/module structure?
- [ ] Have I checked `requirements.txt` / `pyproject.toml` before adding a new dependency?

If any answer is "no" — **stop and clarify before proceeding**.

---

## ✅ Task Execution Rules

### 1. Read Before Write
Always read existing related files before creating or editing anything.
Understand patterns in place, naming conventions, and folder structure. Never assume — verify.

### 2. One Responsibility Per Unit
Every function, class, and module must do **exactly one thing**.
If you find yourself using "and" to describe what something does — split it.

### 3. No Dead Code
Never leave unused variables, commented-out blocks, unused imports, orphaned functions,
or stale TODO comments. If code is not used, it does not exist.

### 4. Follow the Pattern, Always
If a pattern exists in the codebase — follow it exactly.
Do not introduce a new pattern without explicit instruction. Consistency beats personal preference.

### 5. No Hardcoding
Never hardcode strings, numbers, URLs, config values, or environment-specific data inline.
Use constants modules, `.env` files, or config objects (`config.py`, `settings.py`).

### 6. Never Modify What You Weren't Asked To
Do not refactor, rename, or restructure code outside the scope of your task.
If you spot an issue elsewhere, flag it — don't silently change it.

### 7. Validate Your Output
After writing code, review it yourself:
- Does it follow all rules in `CODING_REGULATIONS.md`?
- Does it integrate correctly without breaking existing code?
- Is it consistent with surrounding code style and structure?
- Does it pass linting (`flake8` / `pylint`) and type checks (`mypy`)?

---

## 🧠 Mindset

- Write code as if the most critical senior engineer on the team will review it immediately.
- Assume future developers are reading your code for the first time — make it obvious.
- Prefer clarity over cleverness. Always.
- If you are unsure about anything — **ask, don't guess**.

---

## 🚫 Hard Stops — Never Do These

| Prohibited Action | Why |
|---|---|
| Write a function longer than ~30 lines | Violates Single Responsibility |
| Mix business logic with I/O or presentation | Violates Separation of Concerns |
| Place imports anywhere except the top of the file | Violates import discipline |
| Leave unused imports or variables | Dead code |
| Duplicate logic already written elsewhere | Violates DRY |
| Import a concrete dependency inside a class body | Violates loose coupling |
| Use inconsistent naming within the same project | Violates consistency |
| Manage multiple unrelated concerns in one class | Violates SRP |
| Skip modularizing a repeated pattern | Violates code structure rules |
| Use bare `except:` clauses | Hides bugs, bad error handling |
| Use mutable default arguments (`def f(x=[])`) | Classic Python bug vector |

---

## 📁 Output Expectations

Every task you complete must:

1. Pass all rules defined in `CODING_REGULATIONS.md`
2. Include only the files scoped to the task
3. Leave no broken imports, missing references, or unused code
4. Maintain the exact folder structure and naming conventions of the project
5. Be immediately reviewable and mergeable without cleanup

---

*This contract applies to every task, every file, every line — no exceptions.*
