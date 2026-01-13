# Development Phases — Hotello WhatsApp Bot

This document breaks the Technical Architecture into actionable development phases, with goals, key tasks, deliverables, acceptance criteria, owners, and risks.

**Usage**: follow phases sequentially where indicated; many tasks are iterative and can run in parallel once scaffolding and security are in place.

---

## Phase 0 — Preparation
- Goal: Ready the repo, clarify contracts, and align stakeholders.
- Tasks:
  - Create repository scaffold and branch strategy.
  - Confirm AI provider credentials, backend API owners, and deployment target.
  - Define API contracts for `/api/ai/*` endpoints with example payloads.
  - Create `.env.example` and secret storage plan.
- Deliverables: repo skeleton, API contract doc, env template.
- Acceptance: developer can run a simple Flask app and call mocked backend endpoints.
- Owner: Tech lead / integrator.
- Risk: Unclear API contracts → mitigate by scheduling contract review with backend team.

---

## Phase 1 — Scaffold & Configuration
- Goal: Build minimal, runnable bot project.
- Tasks:
  - Create `app/run.py`, `config.py`, and package manifest (`pyproject.toml` or `requirements.txt`).
  - Add `docs/TechnicalArchitecture.md` link and a README with quickstart.
  - Add basic logging and environment loading.
- Deliverables: runnable app (starts Flask server), dependency file, README.
- Acceptance: `python -m app.run` starts and serves a health route.
- Owner: Developer.
- Risk: Dependency mismatches — pin sensible versions.

---

## Phase 2 — Webhook Receiver & Security
- Goal: Receive, verify and authenticate WhatsApp webhook events.
- Tasks:
  - Implement `webhook.py` with GET `hub.verify_token` and POST event handler.
  - Implement `security.py` for SHA256 signature validation of webhook payloads.
  - Add service-to-service auth: support static API key and JWT flow.
- Deliverables: webhook route, security module, integration tests for verification.
- Acceptance: webhook rejects tampered payloads and validates `hub.verify_token` correctly.
- Owner: Backend & security engineer.
- Risk: Broken verification — add unit tests and example signed payloads.

---

## Phase 3 — WhatsApp Message I/O
- Goal: Parse incoming messages and send responses via WhatsApp Cloud API.
- Tasks:
  - Implement `whatsapp_utils.py`: normalize messages, handle text, templates, quick replies.
  - Implement send helpers with retry/backoff and idempotency keys.
  - Support message formatting (lists, vanity text, templates).
- Deliverables: I/O helpers, unit tests, sample templates.
- Acceptance: Can receive a text message and send a formatted reply via WhatsApp API.
- Owner: Developer.
- Risk: Rate limits / template restrictions — detect 24-hour window; fall back to templates.

---

## Phase 4 — Gemini AI Integration
- Goal: Provide NLU / response generation with safe prompts and guardrails.
- Tasks:
  - Implement `gemini_service.py` to call `google-generativeai` (configurable model).
  - Create reusable prompt templates: intent classification, parameter extraction, conversational reply.
  - Add error handling, model timeouts, and usage quotas.
  - Implement minimal caching for repeated identical queries.
- Deliverables: AI client, prompt library, unit tests and mock harness.
- Acceptance: Given sample utterances, system reliably classifies top intents and extracts entities.
- Owner: ML/AI engineer + dev.
- Risk: Unexpected hallucinations — add guardrails and post-processing filters.

---

## Phase 5 — Intent Router & Backend Orchestration
- Goal: Map intents to backend actions and orchestrate flows (search, booking, profile retrieval).
- Tasks:
  - Implement `intent_router.py` with routing table to backend endpoints.
  - Add conversation state tracker (ephemeral, in-memory) for confirmation flows.
  - Implement client wrappers to call Hotello backend AI endpoints: `search-hotels`, `create-booking`, `my-bookings`, `cancel-booking`.
  - Add idempotency and retry policies for booking calls.
- Deliverables: intent router, backend client, conversation flow tests.
- Acceptance: End-to-end intent -> backend -> user reply flow works with mocked backend.
- Owner: Developer / integrator.
- Risk: Long-running operations → return interim messages and use callbacks/webhooks for completion.

---

## Phase 6 — Booking Flows & Edge Cases
- Goal: Complete booking lifecycle and handle decline/cancel flows.
- Tasks:
  - Implement booking confirmation dialogs, payment-initiation handshake (if applicable), and cancellation confirmation.
  - Validate inputs (dates, guests, payment status) before calling backend.
  - Implement retry, compensation logic, and clear error messages for failures.
- Deliverables: booking flow code, conversation transcripts, integration tests.
- Acceptance: Booking can be created and cancelled reliably in staging against backend.
- Owner: Developer + QA.
- Risk: Partial booking failures — design compensation and clear user messaging.

---

## Phase 7 — Testing & Local Integration
- Goal: Verify functionality locally and in staging.
- Tasks:
  - Add unit tests for parsing, security, AI prompt handlers, router logic.
  - Create contract tests for backend endpoints (use Pact or simple schema mocks).
  - Run local webhook tests via `ngrok` or tunnel and validate end-to-end messaging.
- Deliverables: test suite, test coverage report, integration checklist.
- Acceptance: Critical test suite passes in CI; contract tests signed off by backend team.
- Owner: QA + Developer.
- Risk: Environment parity — use containerized environment for consistency.

---

## Phase 8 — Observability, Logging & Error Tracking
- Goal: Make the service observable and debuggable in production.
- Tasks:
  - Implement structured JSON logs, include correlation IDs across requests.
  - Integrate error tracking (Sentry/Platform native) and metrics (Prometheus/Platform metrics).
  - Add health/readiness endpoints and graceful shutdown handling.
- Deliverables: logging config, dashboards, runbooks for common failures.
- Acceptance: Errors are captured and traceable; health endpoints reflect real status.
- Owner: DevOps / SRE.
- Risk: Noise from AI errors — create filters and sampling on logs.

---

## Phase 9 — CI/CD & Deployment
- Goal: Automate builds, tests, and deployment to chosen host.
- Tasks:
  - Add `Dockerfile` and container build pipeline.
  - Create GitHub Actions (or platform CI) to run tests and build images.
  - Add Render/Railway deployment manifests or instructions for platform.
  - Configure secret injection and environment promotion (staging → prod).
- Deliverables: CI workflows, Docker image, deployment manifests.
- Acceptance: Successful deploy to staging with health checks and rollback path.
- Owner: DevOps.
- Risk: Secret leaks — use platform secret stores and restrict CI logs.

---

## Phase 10 — Launch, Monitoring & Runbooks
- Goal: Production launch with operational readiness.
- Tasks:
  - Execute staged rollout; monitor errors and user experience.
  - Run load tests for expected concurrency and scale horizontally.
  - Publish runbooks for incident response, license usage, and quota management.
- Deliverables: launch checklist, runbooks, scaling playbook.
- Acceptance: SLA targets met for availability and latency in production.
- Owner: Product + SRE.
- Risk: Unexpected scale or vendor rate limits — have graceful degradation.

---

## Phase 11 — Iteration & Enhancements
- Goal: Add value features and harden the system.
- Candidate items:
  - Multi-language support, vector semantic search, admin-controlled responses, payment via WhatsApp.
  - Analytics dashboards and usage-based cost controls.
- Deliverables: prioritized backlog and PoC artifacts.

---

## Appendix — Estimates & Suggested Milestones
- Quick pilot (MVP): Phases 0–5 — 2–4 weeks (1–2 engineers, part-time support from backend).
- Staging-ready: add Phases 6–8 — additional 2–3 weeks.
- Production-ready: add Phases 9–10 — additional 1–2 weeks.

Estimates depend on available backend contract clarity and AI quota/limits.

---

If you want, I can now:
- scaffold the repo files for Phase 1, or
- produce a one-page runbook for webhooks/security.


