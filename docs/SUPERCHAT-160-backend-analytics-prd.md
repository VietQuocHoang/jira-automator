# PRD: SUPERCHAT-160 Backend Analytics for Admin Portal

## 1. Overview

### Product vision
Provide admin staff with a trustworthy analytics layer in the SuperAnne admin portal so they can monitor product adoption, engagement patterns, AI operating cost, feedback sentiment, and emerging user interests, then act on those signals without digging through raw conversations.

### Problem statement
The `SUPERCHAT-160` epic, `Admin Portal - Analytic`, is currently split across multiple tickets with overlapping intent and uneven detail. The backend scope spans usage widgets, AI cost reporting, topic interest analytics, CTA effectiveness, and feedback sentiment, but the requirements are fragmented across stories and supporting context. The platform already stores rich operational data in PostgreSQL and exposes admin APIs through the FastAPI Lambda, yet there is no unified product definition for how the analytics backend should behave as one coherent module.

### Goals
- Consolidate backend analytics requirements for the `SUPERCHAT-160` epic into a single product definition.
- Define a consistent analytics API surface for the admin portal under authenticated admin routes.
- Reuse existing platform data sources such as `conversation_events`, `chat_history`, `llm_usage_log`, and `app_feedback` where possible.
- Support time-range filtering across all analytics widgets so admins can analyze current vs historical behaviour.
- Enable actionable operational decisions in five domains:
  - adoption and engagement
  - topic interest
  - CTA effectiveness
  - AI cost and efficiency
  - user sentiment

### Success metrics
- Admin staff can retrieve every in-scope analytics widget from documented backend endpoints without manual SQL access.
- Each analytics endpoint supports no-filter and date-range-filtered usage.
- API responses are stable enough for frontend widgets to render without endpoint-specific transformation logic beyond formatting.
- Analytics values reconcile with source data within agreed tolerances.
- At least 95% of requests to analytics endpoints complete within the service SLO for admin APIs once deployed.

## 2. Users and personas

### Primary users
- Admin staff at a super fund using the SuperAnne admin portal.
- Product managers and delivery leads monitoring adoption, engagement, and quality.
- Operations and support stakeholders reviewing user behaviour and AI cost.

### Jobs to be done
- Understand whether members are using SuperAnne and how frequently.
- Understand what members care about and which suggested topics are being selected.
- Understand whether CTAs and guided actions are effective.
- Monitor the cost of AI usage over time and at per-user / per-conversation levels.
- Gauge user sentiment from app feedback quickly enough to plan follow-up actions.

### Pain points
- Analytics requirements are fragmented across Jira tickets.
- Some widgets depend on derived logic that is not yet normalized in backend storage.
- Topic and CTA analytics depend on event semantics that must be defined consistently across tool outputs.
- Current stories use “near real time” language without defining a concrete freshness target.

## 3. Scope and constraints

### In scope
- Backend product definition for the analytics capabilities under `SUPERCHAT-160`.
- Consolidated backend requirements covering these tickets:
  - `SUPERCHAT-610` / `SUPERCHAT-551`: Data Widgets Part 1
  - `SUPERCHAT-591`: CTA widget
  - `SUPERCHAT-592`: Topic suggestion counts
  - `SUPERCHAT-593` / `SUPERCHAT-624`: AI cost widgets
  - `SUPERCHAT-623`: Key topics word cloud
  - `SUPERCHAT-625`: Feedback score / sentiment breakdown
- Admin-authenticated API contracts for analytics retrieval.
- Shared filtering, freshness, and authorization rules.
- Brainstormed clarifications where the current Jira ticket is too vague to be implementable.

### Out of scope
- Frontend layout, styling, and UX details except where API shape depends on them.
- Changes to mobile app behaviour unless event capture is required for analytics completeness.
- New business dashboards outside the `SUPERCHAT-160` analytics module.
- Data export, alerts, anomaly detection, or predictive analytics.
- Reworking Jira story ownership or sprint planning.

### Constraints
- SuperAnne runs on FastAPI in AWS Lambda with PostgreSQL on Aurora and admin authentication enforced through the existing admin JWT flow.
- Admin analytics endpoints must follow existing admin routing and permission patterns.
- The platform already requires audit trail logging for admin write operations; analytics endpoints in this PRD are read-only except canonical topic management in `known_topics`.
- Data sources span both materialized tables and event streams, so correctness depends on consistent event capture and summarization quality.

### Assumptions
- `conversation_events`, `chat_history`, `llm_usage_log`, and feedback tables either already exist or can be extended without architectural change.
- Admin portal consumers prefer normalized JSON payloads over multiple bespoke endpoint shapes.
- “Near real time” means freshness within a short lag window rather than push-based streaming for the first release.
- Existing RBAC permissions such as `OVERVIEW_READ`, `AUDIT_TRAIL_READ`, and `AI_KNOWLEDGE_WRITE` remain the controlling permissions.

## 4. Functional requirements

### 4.1 Product scope summary
The backend analytics module should provide one coherent set of admin APIs for the following capability groups:

1. Adoption and engagement metrics
2. Topic suggestion performance metrics
3. CTA effectiveness metrics
4. AI cost metrics
5. Key-topic discovery metrics
6. Feedback sentiment metrics

### 4.2 Shared requirements across all analytics endpoints
- All read endpoints must require admin authentication.
- All dashboard read endpoints must require `OVERVIEW_READ` unless otherwise stated.
- All endpoints must support optional `start_date` and `end_date` filtering unless the metric is inherently all-time only.
- Date filtering must be inclusive by calendar date at the API contract level, with backend implementation documented precisely to avoid off-by-one behaviour.
- Empty result sets must return valid zero-state payloads rather than errors.
- Response contracts must be explicit, versionable, and frontend-friendly.
- Metrics must be derived from tenant-isolated data only.
- First release can be polling-based; no websocket or SSE delivery is required for admin widgets.

### 4.3 Adoption and engagement widgets
Source tickets: `SUPERCHAT-610`, `SUPERCHAT-551`

The backend shall provide analytics for:
- number of users
- monthly active users
- number of conversations
- conversation activity heatmap by hour of day

#### Requirements
- Count distinct members using conversation data for the requested range.
- Count conversations for the requested range.
- Aggregate user chat activity by hour-of-day for heatmap rendering.
- Support grouping by day or month where required by widget use.
- Provide a stable endpoint family under `/admin/dashboard/...`.

#### Proposed API set
- `GET /admin/dashboard/users/count`
- `GET /admin/dashboard/users/monthly-active`
- `GET /admin/dashboard/conversations/count`
- `GET /admin/dashboard/conversations/heatmap`

#### Brainstormed clarifications
- “No. of users” should be defined as distinct members with at least one qualifying conversation or message event in the range.
- “Monthly active users” should be based on distinct active members per calendar month, not rolling 30-day windows, unless product explicitly changes that definition.
- Heatmap should specify timezone behaviour. Recommended default: tenant-configured timezone; fallback to instance timezone.
- If the frontend needs a single composite endpoint for initial dashboard load, the backend may later add `GET /admin/dashboard/overview`, but the source of truth should remain the metric-specific services.

### 4.4 CTA effectiveness analytics
Source ticket: `SUPERCHAT-591`

The backend shall track CTA suggestions generated by SuperAnne and user responses to them so admin staff can assess how effectively guided actions drive engagement.

#### Requirements
- Record each CTA presented to a user, including CTA type, label, conversation context, and timestamp.
- Record whether the user selected, dismissed, ignored, or otherwise responded to the CTA.
- Support time-range-specific aggregation.
- Provide summary counts and selection / response rates by CTA type.

#### Proposed API
- `GET /admin/dashboard/cta-stats`

#### Proposed response dimensions
- `cta_type`
- `cta_label`
- `times_presented`
- `times_selected`
- `times_dismissed`
- `selection_rate`
- `response_rate`

#### Brainstormed clarifications
- The ticket does not define what qualifies as a “response”. This must be normalized before implementation. Recommended statuses:
  - `selected`
  - `dismissed`
  - `ignored`
- CTA tracking should be grounded in existing tool/event output rather than inferred from free-text conversation content.
- If CTA events are not currently persisted with enough structure, event schema extension is a prerequisite.

### 4.5 Topic suggestion counts
Source ticket: `SUPERCHAT-592`

The backend shall expose per-topic suggestion and selection counts for suggested topics presented by SuperAnne.

#### Required endpoint
- `GET /admin/dashboard/topic-suggestion-counts`

#### Required filters
- `start_date`
- `end_date`
- `sort_by`: `times_suggested`, `times_selected`, `selection_rate`
- `sort_order`: `asc`, `desc`

#### Required fields per item
- `tool_type`
- `topic_highlight`
- `topic_subtext`
- `times_suggested`
- `times_selected`
- `selection_rate`

#### Data source
- `conversation_events` filtered to the relevant topic-suggestion tool events and user selection events.

#### Brainstormed clarifications
- Topic identity should use a stable canonical key if available, not only display text, to avoid aggregation drift caused by copy changes.
- `selection_rate` should be defined as `times_selected / times_suggested`; if a topic is suggested in batches, the denominator must count suggestion occurrences, not sessions.
- `tool_type` should be normalized so topic suggestions from different tools can either be grouped together or compared cleanly.

### 4.6 AI cost widgets
Source tickets: `SUPERCHAT-593`, `SUPERCHAT-624`

The backend shall provide cost visibility for AI usage over time and at unit-economics levels.

#### Metrics
- total AI cost
- average cost per user
- average cost per conversation
- daily AI spend over time

#### Requirements
- Costs must be time-range-specific.
- Cost accounting must preserve historical pricing instead of recalculating old usage with new model prices.
- Cost data must be attributable at user and conversation levels, or to a documented fallback aggregation level if source granularity is unavailable.
- APIs must support frontend tooltip and explanation needs by documenting what is included in the cost metric.

#### Proposed API
- `GET /admin/dashboard/ai-costs`

#### Proposed response shape
- `total_cost`
- `average_cost_per_user`
- `average_cost_per_conversation`
- `daily_spend[]`
- optional explanatory metadata:
  - `currency`
  - `cost_basis`
  - `included_models`

#### Brainstormed clarifications
- The platform already logs LLM token usage and cost in `llm_usage_log` according to project context. This should be the source of truth where possible rather than reconstructing cost from conversation tables.
- “Per user” should be based on distinct users who incurred AI cost in the selected period, not all registered users.
- “Per conversation” should be based on distinct conversations with at least one billable AI interaction in the selected period.
- Daily spend should use execution date of the model call, not conversation creation date.
- For transparency, the API should explicitly state whether retries, failed calls, preview/admin chat usage, and compliance model calls are included.

### 4.7 Key topics word cloud
Source ticket: `SUPERCHAT-623`

The backend shall surface common member conversation topics based on conversation summaries and a canonical known-topics list.

#### Required endpoints
- `GET /admin/dashboard/key-topics-word-cloud`
- `GET /admin/dashboard/known-topics`
- `POST /admin/dashboard/known-topics`

#### Requirements
- Add a `known_topics` store for canonical labels.
- Extend conversation summary content with `key_topics: List[str]`.
- Update summarization prompts/services so summarization prefers canonical topic labels when available.
- Return topic counts and relative weights for a selected date range.

#### Brainstormed clarifications
- Topic extraction quality depends on summarizer accuracy. Product should define an acceptable precision / recall threshold or an admin review workflow if topic quality becomes material.
- `relative_weight` should be deterministic. Recommended formula: `topic_count / max_topic_count` within the selected range for word-cloud scaling.
- Known topics should support aliases or normalized matching to prevent minor wording variation from fragmenting analytics.
- Because `POST /admin/dashboard/known-topics` is a write endpoint, it should require `AI_KNOWLEDGE_WRITE` and should publish audit events if persisted through admin services.

### 4.8 Feedback sentiment analytics
Source ticket: `SUPERCHAT-625` plus context file `feedback-feature/SUPERCHAT-625.md`

The backend shall aggregate app feedback ratings into a sentiment breakdown for the admin portal.

#### Required endpoint
- `GET /admin/feedback/stats`

#### Required response behaviour
- Return:
  - `average_rating`
  - `sentiment_label`
  - `total_count`
  - `breakdown[]` for ratings 5 through 1
- Support optional `start_date` and `end_date`
- Return valid all-zero / null payloads for empty periods
- Keep the endpoint frontend-ready for a sentiment breakdown widget with date-range filtering

#### Sentiment thresholds
- `>= 4.5`: Very Positive
- `>= 3.5`: Positive
- `>= 2.5`: Neutral
- `>= 1.5`: Negative
- `< 1.5`: Very Negative

#### Brainstormed clarifications
- The richer context file is more implementation-ready than the Jira description and should be treated as the working source of truth.
- The ticket says “feedback score widget”, but the design intent is broader: average score plus sentiment classification plus five-bucket breakdown.

### 4.9 Recommended API consolidation
To reduce fragmentation while keeping implementation modular, the backend should organize analytics routes under:

- `/admin/dashboard/...` for usage, cost, topic, and CTA analytics
- `/admin/feedback/...` for feedback-specific analytics

Each endpoint should share:
- admin auth
- permission enforcement
- common date filter parsing
- common zero-state handling

## 5. Non-functional requirements

### Performance
- P95 response time for cached or index-friendly analytics reads should target under 1 second for typical dashboard ranges.
- Heavier aggregations should still target under 3 seconds without blocking the rest of the dashboard.
- Endpoints should support pagination only where returning lists large enough to warrant it; most widget endpoints should return bounded payloads.

### Freshness
- “Near real time” should be defined as data visible within 5 minutes of source event persistence for release 1.
- If some metrics depend on summarization or async materialization, the API should document freshness expectations per metric.

### Availability
- Analytics endpoints should meet the same operational baseline as existing admin APIs.
- Failure of one analytics endpoint should not break unrelated widgets.

### Security and access control
- All analytics endpoints require admin authentication.
- Read analytics endpoints require `OVERVIEW_READ`.
- Known-topic mutation requires `AI_KNOWLEDGE_WRITE`.
- Tenant data isolation must follow existing instance isolation rules.

### Data integrity
- Metric definitions must be deterministic and documented.
- Historical AI cost values must not be backfilled using revised model pricing.
- Timezone handling must be explicit and consistent across endpoints.

### Maintainability
- Repository-layer queries should encapsulate analytics SQL.
- Shared Pydantic schemas should be used for consistent response contracts.
- Reusable date-range parsing and validation should be centralized.

## 6. Analytics and KPIs

### Product KPIs enabled by this module
- Distinct active users
- Monthly active users
- Conversation volume
- Hourly engagement distribution
- CTA selection rate
- Topic suggestion selection rate
- AI total spend
- AI cost per user
- AI cost per conversation
- Feedback average rating
- Feedback sentiment distribution
- Topic frequency share

### Suggested operational event tracking
- CTA presented
- CTA selected
- CTA dismissed
- Topic suggestion presented
- Topic selected
- LLM invocation completed with token and cost record
- Feedback submitted
- Conversation summarized with extracted key topics

### KPI definition notes
- All ratios should clearly define denominator and zero-case handling.
- Daily and monthly aggregations should use the same timezone basis across the dashboard.

## 7. Dependencies and risks

### Dependencies
- Existing admin auth flow and RBAC permissions.
- Existing conversation and event storage tables.
- Existing `llm_usage_log` or equivalent cost log.
- Existing `app_feedback` dataset from the feedback feature.
- Summarization pipeline updates for `key_topics`.
- Frontend widgets that consume the documented endpoints.

### Key risks
- CTA and topic suggestion events may not yet be stored in a normalized way.
- Topic extraction quality may be too noisy for trustworthy dashboard output without canonical topic management and prompt tuning.
- AI cost semantics may differ between raw Bedrock cost, user-visible cost, and fully loaded operational cost.
- “Real-time” expectations may exceed what Lambda + aggregation queries can provide without caching or pre-aggregation.
- Mixed-scope Jira stories create ownership ambiguity between backend and frontend.

### Mitigations
- Define explicit event schemas before implementing CTA and suggestion analytics.
- Use canonical topic dictionaries and evaluate extraction accuracy on a sample corpus.
- Treat `llm_usage_log` as the authoritative cost ledger and document inclusions/exclusions.
- Introduce materialized summaries or cached views if dashboard query cost becomes high.
- Split backend contracts from frontend rendering acceptance criteria when refining tickets.

## 8. Acceptance criteria

### Release-level criteria
- Backend analytics endpoints are implemented for all in-scope metrics and documented.
- Every in-scope endpoint supports authenticated admin access and correct permission checks.
- Every in-scope endpoint supports time-range filtering or explicitly documents why it does not.
- Zero-state responses are consistent and renderable by the frontend.
- AI cost calculations preserve historical pricing semantics.
- Topic-suggestion and CTA metrics are backed by normalized event definitions.
- Key-topic word cloud uses canonical topic management and returns deterministic weighting.
- Feedback sentiment stats return average score, sentiment label, and five-category breakdown.

### Suggested implementation phases
- Phase 1: stabilize existing Data Widgets Part 1 backend (`SUPERCHAT-610`) and feedback stats (`SUPERCHAT-625`)
- Phase 2: deliver topic suggestion counts (`SUPERCHAT-592`) and AI cost widgets (`SUPERCHAT-593`)
- Phase 3: deliver CTA analytics (`SUPERCHAT-591`) and key-topics word cloud (`SUPERCHAT-623`)

## Ticket traceability

| Ticket | Requirement area | Notes |
|---|---|---|
| `SUPERCHAT-610` | Adoption and engagement widgets | Backend story with concrete implementation notes; likely source of truth over `SUPERCHAT-551` for backend scope |
| `SUPERCHAT-551` | Adoption and engagement widgets | Mixed FE/BE story; overlaps with `SUPERCHAT-610` |
| `SUPERCHAT-591` | CTA analytics | Underspecified; needs event taxonomy and response-state definitions |
| `SUPERCHAT-592` | Topic suggestion counts | Reasonably concrete endpoint contract |
| `SUPERCHAT-593` | AI cost widgets | Core BE cost semantics and aggregation requirements |
| `SUPERCHAT-624` | AI cost widgets frontend dependency | FE sibling ticket; useful for shared semantics such as tooltip copy |
| `SUPERCHAT-623` | Key-topics word cloud | Requires summary-schema and known-topics model changes |
| `SUPERCHAT-625` | Feedback sentiment analytics | Jira body is light, but local context file provides a stronger backend contract |

## Open questions

- What exact timezone should date filtering use for the Investstream tenant?
- Should admin-preview or internal test conversations contribute to analytics metrics, especially AI cost and topic metrics?
- What counts as a CTA “response” for analytics purposes: only selection, or also dismissal and timeout?
- Are topic suggestions identified by stable IDs anywhere today, or only by rendered text?
- Should heatmap counts use all messages, only member-authored messages, or only conversation starts?
- Should AI cost include compliance and summarization model calls, or only user-facing chat generation?
- Does the product want one composite overview endpoint for dashboard initial load, or separate widget endpoints only?
- Is `SUPERCHAT-604` intentionally frontend-labelled despite the `[Backend]` summary, and should it affect analytics scope at all?

## Recommended next refinements

- Convert each endpoint area above into implementation-ready backend stories with explicit request and response schemas.
- Align the frontend tickets to the same metric definitions so UI and API do not diverge.
- Add a lightweight glossary for terms such as active user, conversation, CTA response, topic selection, and AI cost.
