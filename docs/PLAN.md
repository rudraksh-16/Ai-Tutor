# Master Implementation Plan: Mastery-Based JIT Tutor (v3)

## 🎯 Goal

Modernize the AI Tutor into a secure, mastery-based learning platform. We are shifting from background "mass-generation" to a **Just-In-Time (JIT) Sectional** approach, where every step is validated by a secure, backend-only quiz system.

---

## 🧱 Component Breakdown

### 1. The Planning Layer (JIT Sectional)

- **[Service] `PlannerService`**: Refactor to support single-chapter generation triggered by user interaction (JIT).
- **[LLM] `ChapterPlanner`**: Update to output a JSON list of 3-4 structured sub-topics (sections) per chapter.
- **[Repo] `PlannerRepository`**: Handle batch-insertion of multiple `ChapterPlan` records per chapter.

### 2. The Learning Layer (Sub-topic Focused Chat)

- **[LLM] `TeacherAgent`**: Update its context tool to load only the specific content for the _current sub-topic_ the user is studying.
- **[API] `chat_teacher`**: Update to accept an optional `section_id` to strictly lock the Agent's accuracy to the current section.

### 3. The Validation Layer (Secure Backend Quiz)

- **[Repo] `QuizRepository`**: NEW repository to manage:
  - `save_quiz()`: Securely storing questions and correct answers on the backend.
  - `validate_submission()`: Comparing user choices against stored answers and calculating a score.
  - **Side Effect**: Chapters are marked `DONE` and next chapters UNLOCKED only after the backend validates a passing score.

### 4. Simple Account View

- **[API] `GET /auth/me`**: Utilize existing endpoints to display the user's name and email in the profile view.

---

## 🔄 The New User Flow

1.  **Select Topic**: Curriculum is generated quickly (without plans).
2.  **Start Chapter (JIT)**: LLM generates 3-4 high-accuracy sub-topics on-demand.
3.  **Read (Reading Mode)**: User reads theory sections. Sections can be marked `is_completed: true` for progress tracking.
4.  **Mentor (Chat Mode)**: User interacts with the AI Teacher, who is focused strictly on the current sub-topic's plan.
5.  **Validate (Quiz)**: Once taught, the AI Teacher delivers a quiz. Correct answers are hidden from the user's browser.
6.  **Complete**: User submits answers to `/quiz/submit`. If passed, the backend marks the chapter as `DONE` and unlocks the next one.

---

## 🚦 Final Review

> [!IMPORTANT]
> **Plan Migration**: This change will make existing monolithic plans obsolete. We will purge `chapter_plans` to start fresh with the sectional structure.

> [!CAUTION]
> **Accuracy Lock**: The AI Teacher will purposefully deny answering questions about future sections to ensure mastery of the current topic.
