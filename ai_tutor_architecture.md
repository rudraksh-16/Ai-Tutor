**AI TUTOR PLATFORM**

Technical Architecture & Flow Document

*Version 2.0  •  April 2026*

**Document Scope**

This document covers the complete system design, database schema, API contracts, LLM agent flows, teacher-chapter-quiz progression logic, and scalability recommendations for the AI Tutor application.

# **1\. System Overview**

AI Tutor is a personalized, AI-driven learning platform built on a decoupled client-server architecture. It allows a user to enter any topic, negotiate a custom curriculum with an AI agent, then work through a structured series of chapters guided by a Teacher Agent — each chapter concluding with an auto-generated quiz before the next chapter unlocks.

## **1.1 Technology Stack**

| Layer | Technology | Responsibility |
| :---- | :---- | :---- |
| Frontend | React 19 \+ Vite \+ Tailwind CSS | UI rendering, SSE streaming receiver, local state management |
| Backend | Python FastAPI (async) | Auth, REST API, business logic, LangGraph orchestration |
| Database | PostgreSQL \+ SQLAlchemy 2 (asyncpg) | Persistent state: Users, Topics, Chapters, Conversations |
| Agent Framework | LangGraph / LangChain | Curriculum, Planner, Teacher, Quiz, Deep Research agents |
| LLM Provider | OpenAI GPT-4o | Language generation, reasoning, tool execution |
| Search | Tavily Search API | Real-time web search used by Curriculum & Research agents |
| Auth | JWT (python-jose) \+ bcrypt | Stateless token-based authentication |
| Streaming | Server-Sent Events (SSE) | Real-time token streaming from LLM to frontend |

## **1.2 Architectural Tiers**

* Tier 1 – Client Layer: React SPA consuming REST APIs and SSE streams. Manages sidebar state, chat views, chapter progress polling.

* Tier 2 – API & Application Layer: FastAPI async server handling auth, validation, routing, and background agent tasks.

* Tier 3 – Persistence Layer: PostgreSQL storing all user data, learning states, and full conversation histories.

* Tier 4 – Intelligence Layer: LangGraph multi-agent pipelines performing negotiation, planning, teaching, quizzing, and deep research.

# **2\. Database Design (ERD & Schema)**

All entities follow a strict UUID primary key convention and use an Enum-based status state machine to enforce valid progressions. The schema is designed for scalability — conversations are decoupled from topics and chapters via a polymorphic target\_id/target\_type pattern, allowing a single Conversation model to serve all three agent types.

## **2.1 Core Entities**

| Entity | Key Fields & Purpose |
| :---- | :---- |
| users | id (UUID), email (unique), hashed\_password. Root entity. All topics belong to a user. |
| topics | id, user\_id (FK), title, user\_summary, curriculum\_text, status (pending→in\_progress→completed). Represents a full learning journey. |
| chapters | id, topic\_id (FK), title, description, order\_index, status (locked→pending→in\_progress→completed). Each topic has N ordered chapters. |
| chapter\_plans | id, chapter\_id (FK), title, content (syllabus text), order\_index, is\_completed. Granular outline items within a chapter. |
| conversations | id, target\_id (UUID), target\_type (curriculum|teacher|quiz). Polymorphic container for messages. One per agent session. |
| messages | id, conversation\_id (FK), role (user|assistant|tool), content (text), created\_at. Full persistent chat history. |
| quiz\_attempts | id, chapter\_id (FK), user\_id (FK), score, total\_questions, passed (bool), created\_at. Tracks quiz performance per chapter. |
| quiz\_questions | id, chapter\_id (FK), question\_text, question\_type (mcq|open), options (JSONB), correct\_answer, explanation. Reusable question bank. |

## **2.2 Status State Machines**

| Topic Status Flow |
| :---- |
| pending  →  in\_progress  →  completed • pending: Topic created, curriculum negotiation in progress • in\_progress: Curriculum finalized, chapters generated, user actively learning • completed: All chapters completed and quizzes passed |

| Chapter Status Flow |
| :---- |
| locked  →  pending  →  in\_progress  →  quiz\_pending  →  completed • locked: Not yet accessible (previous chapter not completed) • pending: Accessible but not started • in\_progress: User is actively chatting with Teacher Agent • quiz\_pending: Teacher Agent has determined chapter content is mastered; quiz is being presented • completed: Quiz passed; next chapter unlocked |

## **2.3 Scalability Indexes**

| Index | Reason |
| :---- | :---- |
| users.email (UNIQUE) | Fast login lookups |
| topics.user\_id | Fetch all topics for sidebar |
| chapters.topic\_id \+ order\_index | Ordered chapter listing |
| messages.conversation\_id \+ created\_at | Paginated history retrieval |
| quiz\_attempts.chapter\_id \+ user\_id | Per-user quiz history |
| chapter\_plans.chapter\_id \+ order\_index | Ordered syllabus retrieval |

# **3\. API Contract Reference**

All endpoints are versioned under /api/v1/. Authentication uses Bearer JWT tokens in the Authorization header. Streaming endpoints use text/event-stream (SSE) with structured JSON event payloads.

## **3.1 Authentication Endpoints**

| Endpoint | Description |
| :---- | :---- |
| POST /api/auth/register | Register new user. Body: {email, password}. Returns JWT. |
| POST /api/auth/login | Login. Body: {email, password}. Returns access\_token. |
| GET /api/auth/me | Returns current authenticated user profile. |

## **3.2 Topic & Chapter Endpoints**

| Endpoint | Description |
| :---- | :---- |
| POST /api/v1/topics/start | Create new topic. Body: {title}. Returns topic\_id. |
| GET /api/v1/topics/ | List all topics for current user (sidebar). |
| GET /api/v1/topics/{id}/status | Polling endpoint for planning\_complete flag. |
| GET /api/v1/topics/{id}/chapters | Get ordered chapter list with statuses. |
| GET /api/v1/chapters/{id} | Get single chapter with chapter\_plans. |
| GET /api/v1/sidebar/ | Optimized sidebar data: incomplete \+ completed topics. |

## **3.3 Streaming Chat Endpoints (SSE)**

| Endpoint | Description |
| :---- | :---- |
| POST /api/v1/chat/curriculum | Stream curriculum negotiation. Emits: {type: token, data}, {type: planning\_started}, {type: done}. |
| POST /api/v1/chat/teacher | Stream teacher response for a chapter. Emits: {type: token}, {type: chapter\_completed}, {type: quiz\_ready}, {type: done}. |
| POST /api/v1/chat/quiz | Stream quiz question & evaluate answer. Emits: {type: question}, {type: evaluation}, {type: quiz\_passed}, {type: done}. |

## **3.4 SSE Event Schema**

| Standard SSE Event Payload Format |
| :---- |
| data: {"type": "token", "data": "Hello"} data: {"type": "chapter\_completed", "chapter\_id": "uuid"} data: {"type": "quiz\_ready", "chapter\_id": "uuid"} data: {"type": "quiz\_passed", "next\_chapter\_id": "uuid"} data: {"type": "planning\_started"} data: {"type": "planning\_complete"} data: {"type": "error", "message": "..."} data: {"type": "done"} |

# **4\. LLM Agent Flows**

All agents are built on LangGraph with a shared base class providing memory injection, streaming hooks, and tool execution. Each agent runs a ReAct-style loop: Reason → Act (tool call) → Observe → Reason again.

## **4.1 Curriculum Agent**

Handles the initial negotiation between user and system to finalize a personalized learning path.

* System Prompt: Guides the agent to ask about prior knowledge, goals, preferred depth, and time availability.

* Tools: upsert\_curriculum (save negotiated curriculum to DB), web\_search (verify topic relevance/accuracy).

* Termination: When the user confirms the plan, the agent calls upsert\_curriculum with status=finalized, which triggers the planning\_started SSE event and launches the Planner in a background thread.

## **4.2 Planner Agent**

Runs exclusively in the background after curriculum finalization. Not interactive.

* Input: The finalized curriculum\_text from the topic.

* Output: Inserts N Chapter rows and M ChapterPlan rows per chapter into the database.

* Chapter structure: Each chapter gets a title, description, order\_index, and 3-7 ChapterPlan items (outline points with content text).

* On completion: Updates topic status to in\_progress. Frontend polling detects this and redirects user to LearningView.

## **4.3 Teacher Agent — Detailed Flow**

The Teacher Agent is the core learning experience. Each chapter has its own isolated conversation context.

| Teacher Agent Chapter Flow |
| :---- |
| Step 1: User clicks a chapter → Frontend fetches conversation history → Teacher Agent loads chapter\_plans via get\_outline\_content tool Step 2: Agent teaches iteratively — responds to user questions, explains concepts from the outline, uses analogies and examples. Step 3: Agent monitors understanding. When all chapter\_plan items are covered AND the user signals readiness, the agent calls update\_status(quiz\_pending). Step 4: The chapter status changes to quiz\_pending. SSE emits {type: quiz\_ready}. Frontend transitions the chat UI to Quiz Mode. Step 5: Quiz Agent takes over. On quiz pass, chapter moves to completed, next chapter unlocks. IMPORTANT: One conversation per chapter. The teacher never crosses chapter boundaries. |

* Tools: get\_chapter (full chapter metadata), get\_outline\_content (syllabus items to teach from), update\_status (move chapter forward), create\_quiz (generate quiz questions).

* Sandbox Rule: System prompt strictly confines the agent to the current chapter topic. Off-topic questions are politely redirected.

* Progress Tracking: As each chapter\_plan item is covered, the agent marks is\_completed=true on the ChapterPlan record.

## **4.4 Quiz Agent — Detailed Flow**

Validates the user's understanding before unlocking the next chapter.

* Trigger: chapter status \= quiz\_pending (set by Teacher Agent via SSE).

* Question Generation: Quiz Agent reads all chapter\_plan content and generates 5-10 questions (mix of MCQ and short-answer) stored in quiz\_questions table.

* Flow: Agent presents one question at a time via SSE. User answers. Agent evaluates (MCQ: exact match; short-answer: LLM semantic evaluation). Score tracked in quiz\_attempts.

* Pass Threshold: 70% correct. On pass, SSE emits quiz\_passed with next\_chapter\_id. Chapter status → completed. Next chapter status → pending (unlocked).

* Fail Handling: Agent provides explanations for wrong answers, then offers to re-teach the chapter or retry the quiz.

## **4.5 Deep Research Agent**

A background multi-agent pipeline for generating rich supplementary content on complex topics.

* Sub-agents: query\_maker (expands topic into sub-queries), research\_agent (fetches web sources per query), reviewer (filters low-quality sources), synthesizer (produces structured document).

* Rate Limiting: rate\_limiter.py enforces API call budgets to prevent Tavily/OpenAI bans.

* Output: Structured markdown documents stored and surfaced as supplementary reading materials per chapter.

# **5\. Core User Journey & Sequence Flows**

## **5.1 Phase 1: Onboarding & Curriculum Negotiation**

1. User lands on home screen, sees topic suggestions.

2. User types a topic (e.g., 'Machine Learning with AI') and submits.

3. Frontend: POST /api/v1/topics/start → receives topic\_id.

4. Frontend navigates to CurriculumChatView.

5. User chats with Curriculum Agent (SSE stream). Agent asks about goals, depth, pace.

6. User confirms the plan. Agent calls upsert\_curriculum tool.

7. SSE emits {type: planning\_started}. Frontend shows loading state.

8. Planner Agent runs in background thread. Frontend polls GET /topics/{id}/status every 3 seconds.

9. When planning complete: polling returns planning\_complete=true. Frontend redirects to LearningView.

## **5.2 Phase 2: Chapter Learning Flow**

10. LearningView shows chapter list (Chapter 1: pending, rest: locked).

11. User clicks Chapter 1\. Frontend fetches conversation history (empty on first visit).

12. Teacher Agent greets user, loads chapter outline via get\_outline\_content tool.

13. User asks questions, Agent teaches from the chapter plan. Chapter status → in\_progress.

14. As outline items are covered, Agent marks chapter\_plan.is\_completed \= true.

15. When Agent determines mastery, it calls update\_status(quiz\_pending).

16. SSE emits {type: quiz\_ready}. Frontend transitions to Quiz UI within the same chat view.

## **5.3 Phase 3: Quiz & Progression**

17. Quiz Agent takes control of the chat stream.

18. Agent generates questions from chapter content. Presents one at a time via SSE.

19. User answers each question. Agent evaluates and provides instant feedback.

20. On passing (≥70%): SSE emits {type: quiz\_passed, next\_chapter\_id}. Chapter → completed. Next chapter unlocks.

21. On failing: Agent explains errors. User can choose to review chapter or retry quiz.

22. Sidebar updates: completed chapters show checkmark. User proceeds to Chapter 2\.

23. All chapters completed → Topic status → completed. User receives completion summary.

# **6\. Scalability & Performance Design**

## **6.1 Backend Scalability**

* Async All The Way: FastAPI \+ asyncpg means no thread blocking on DB or LLM calls. Handles hundreds of concurrent SSE streams per instance.

* Background Tasks: Planner Agent uses FastAPI BackgroundTasks (or Celery for production scale) to prevent long-running jobs from holding up request threads.

* Stateless API: No server-side session state. All context is reconstructed from PostgreSQL per request. Enables horizontal scaling behind a load balancer.

* Connection Pooling: asyncpg connection pool (min=5, max=20 per instance) prevents DB connection exhaustion.

* Rate Limiting: Per-user rate limiting on chat endpoints (e.g., 30 req/min) using Redis \+ slowapi.

## **6.2 Database Scalability**

* Read Replicas: Route GET endpoints (sidebar, chapter list, history) to read replicas. Writes go to primary.

* JSONB for Flexible Data: quiz\_questions.options stored as JSONB for schema-free question formats.

* Soft Deletes: Add deleted\_at timestamp instead of hard deletes to preserve learning history.

* Partitioning: messages table partitioned by created\_at (monthly) for long-term performance as conversation history grows.

* Alembic Migrations: All schema changes version-controlled. Never run raw SQL in production.

## **6.3 Frontend Scalability**

* React Context \+ useReducer: Global state for auth and sidebar. Local component state for chat. Avoid prop drilling.

* SSE Reconnect Logic: EventSource auto-reconnects on disconnect. Frontend tracks last event ID for resumption.

* Optimistic UI: Chapter status changes reflected immediately in UI; DB confirmed state synced in background.

* Code Splitting: Vite dynamic imports for LearningView and QuizView (lazy loaded).

## **6.4 LLM Cost & Reliability**

* Prompt Caching: OpenAI prompt caching for static system prompts (saves \~50% on token costs for Teacher Agent).

* Model Routing: Use GPT-4o-mini for quiz evaluation and simple responses; GPT-4o only for Teacher and Curriculum agents.

* Fallback: If OpenAI is unavailable, return a structured error SSE event. Never hang the connection.

* Context Window Management: Inject only the last 10 messages \+ system prompt \+ current chapter plan. Prevents token bloat.

# **7\. Security Design**

* JWT Expiry: Access tokens expire in 1 hour. Refresh tokens (stored in httpOnly cookie) expire in 7 days.

* Password Hashing: bcrypt with salt rounds \= 12\.

* CORS: Only allow requests from the specific frontend origin. No wildcard in production.

* Input Validation: All request bodies validated via Pydantic schemas before reaching service layer.

* Prompt Injection Defense: User messages are injected into LangGraph as human messages, never into system prompts. System prompts are immutable server-side strings.

* SQL Injection: SQLAlchemy ORM with parameterized queries. No raw SQL string interpolation.

* Environment Variables: All secrets (.env) excluded from version control. Use AWS Secrets Manager or Vault in production.

# **8\. Recommended Directory Structure**

| Backend: /AI\_Tutor/src/ |
| :---- |
| main.py                    ← FastAPI app init, CORS, router mounting logger.py                  ← Centralized logging backend/   api/v1/     router.py              ← Aggregates all endpoint groups     endpoints/       topics.py, chapters.py, sidebar.py       chat\_curriculum.py, chat\_teacher.py, chat\_quiz.py     auth/                  ← JWT routes, schemas, utils   db/     database.py            ← asyncpg engine \+ sessionmaker     init\_db.py             ← Table creation \+ seed   models/                  ← SQLAlchemy ORM models     user.py, topic.py, chapter.py, chapter\_plan.py     conversation.py, message.py, quiz\_attempt.py, quiz\_question.py   schemas/                 ← Pydantic request/response schemas   repository/              ← DAL: CRUD functions per model   services/                ← Business logic orchestration     curriculum\_service.py, planner\_service.py     teacher\_service.py, quiz\_service.py   enums/status.py          ← TopicStatus, ChapterStatus enums llm/   agent\_core/agent.py, tool.py   ← Base agent class   curriculum\_agent/   planner/   teacher\_agent/   quiz\_agent/   deep\_research/ |

| Frontend: /ai\_tutor\_frontend/src/ |
| :---- |
| main.jsx                   ← React app bootstrap \+ BrowserRouter App.jsx                    ← Layout wrapper, protected routes components/   Sidebar/                 ← Topic list, status icons, New Topic button   Home/                    ← Landing: topic input \+ suggestion cards   CurriculumChat/          ← Curriculum negotiation chat UI   LearningView/            ← Split: ChapterIndex \+ TeacherChat   TeacherChat/             ← SSE-connected chat with Teacher Agent   QuizView/                ← Quiz question UI, progress, score   common/                  ← Button, Input, ChatBubble, Spinner, etc. services/   api.js                   ← Axios instance with auth interceptors   topicService.js, chapterService.js, sidebarService.js   curriculumStream.js      ← SSE EventSource wrapper for curriculum   teacherStream.js         ← SSE wrapper for teacher \+ quiz events contexts/   AuthContext.jsx          ← JWT storage, login/logout   SidebarContext.jsx       ← Global sidebar state hooks/   useSSE.js                ← Reusable SSE hook with reconnect logic   usePolling.js            ← Status polling for planning phase |

# **9\. Implementation Improvement Checklist**

## **Immediate Priorities**

* Add quiz\_attempts and quiz\_questions tables (missing from current schema).

* Implement chapter status: locked → pending → in\_progress → quiz\_pending → completed state machine.

* Teacher Agent: emit {type: quiz\_ready} SSE event when calling update\_status(quiz\_pending).

* Frontend: handle quiz\_ready event to transition TeacherChat UI → QuizView without page navigation.

* SSE reconnect logic in useSSE.js hook with exponential backoff.

## **Short-term Improvements**

* Add Redis for rate limiting and caching sidebar data (5-second TTL).

* Implement soft deletes (deleted\_at) on topics and chapters.

* Add Alembic for database migrations. Never use init\_db.py in production.

* Model routing: use gpt-4o-mini for quiz evaluation to reduce costs.

* Add chapter\_plan.is\_completed tracking so Teacher knows what's been covered.

## **Scalability Milestones**

* Move Planner background tasks to Celery \+ Redis queue for production workloads.

* Add PostgreSQL read replica. Route all GET endpoints to replica.

* Add messages table time-based partitioning (monthly).

* Implement OpenAI prompt caching for Teacher Agent system prompts.

* Add structured logging (JSON format) with request\_id tracing across all services.

*AI Tutor Platform — Technical Architecture Document v2.0*