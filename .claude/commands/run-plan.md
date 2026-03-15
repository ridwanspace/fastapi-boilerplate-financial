---
description: Execute a specific task from a plan file, then update plan progress. Usage: /run-plan <plan-file> <task-id>
argument-hint: "<plan-file-name-or-number> <task-id>"
allowed-tools: Read, Glob, Grep, Bash, Edit, Write
---

You are a senior engineer executing a specific task from a development plan.

**Arguments received**: $ARGUMENTS

---

## Step 1 — Parse arguments

`$ARGUMENTS` contains two tokens: `<plan-file> <task-id>`

Examples of valid calls:
```
/run-plan 00-wallet-refund.md B1.1
/run-plan 00-wallet-refund.md B1.1
/run-plan 03 Task-2.3
/run-plan docs/plan/02-billing.md 2.3
```

Parsing rules:
- **First token** (`<plan-file>`): may be a full path, just the filename, or just the number prefix (e.g., `03`).
  - If only a number given (e.g., `03`), glob `docs/plan/03-*.md` to find the file.
  - If no extension, assume `.md` and search `docs/plan/`.
  - Resolve to a full path before reading.
- **Second token** (`<task-id>`): the task section to execute (e.g., `B1.1`, `2.3`, `Task-3`).
  - Match case-insensitively against section headers in the plan file.

If `$ARGUMENTS` is missing or malformed, stop and tell the user:
```
Usage: /run-plan <plan-file> <task-id>

Examples:
  /run-plan 00-wallet-refund.md B1.1
  /run-plan 03 2.3
  /run-plan docs/plan/02-billing.md Task-2.1
```

---

## Step 2 — Load and parse the plan file

Read the full plan file. Extract:

1. **Plan metadata** from the header: title, module, depends-on, status.
2. **The target task section** matching `<task-id>`:
   - Find the heading containing the task ID (e.g., `### Task B1.1:`, `## Task 2.3 —`)
   - Read until the next same-level heading (that's the full task scope)
   - Extract: purpose, files to create/modify, implementation details, acceptance criteria, unit test list, integration test list
3. **Any "What Already Exists" table** — to know baseline state.
4. **Any prerequisite context sections** at the top of the plan (e.g., "What was built in Part X").

If the task ID is not found in the plan, stop and list all available task IDs found in the file.

---

## Step 3 — Pre-flight: explore the codebase

Before writing any code, search for what already exists relevant to this specific task.

Use Glob and Grep to find:
- The exact files the task says to create (do they already exist?)
- Files the task says to modify (read them fully before editing)
- Related entities, base classes, patterns to follow (e.g., existing `BaseEntity` subclasses, existing handlers, existing router files)
- Existing tests in the same test module

Read every file you will touch. Never modify a file you haven't read.

---

## Step 4 — Status report

Print a concise status block before starting:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLAN : {plan filename}
TASK : {task-id} — {task title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Files to create  : {list or "none"}
Files to modify  : {list or "none"}
Already exists   : {relevant existing files found}
Conflicts        : {detected / none}
Recommendation   : CONTINUE | SKIP (already done) | BLOCKED (missing prereq)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

- If **SKIP**: the task appears already implemented. Show evidence and ask the user if they want to re-run or mark it complete.
- If **BLOCKED**: a prerequisite task has not been completed. Name the blocking task and stop.
- If **CONTINUE**: proceed to Step 5.

---

## Step 5 — Implement

Implement exactly what the plan task describes. Nothing more, nothing less.

### Code standards (from `.claude/CLAUDE.md` and rule files)

**General**:
- Python 3.12+, async-first throughout
- Type hints on every function and method — no exceptions
- Pydantic v2 for all schemas: `model_config = ConfigDict(strict=True)`
- `Decimal` for all monetary values — never `float`
- Domain exceptions only in domain/application layers — never `HTTPException`
- Result type: handlers return `Ok(value) | Err(exception)` — no exceptions cross layer boundaries

**Domain layer** (`src/contexts/*/domain/`):
- Zero framework imports — no FastAPI, SQLAlchemy, Pydantic, Redis
- Entities extend `AggregateRoot` or `Entity` from `src/shared/domain/`
- Value objects extend `ValueObject` (frozen dataclass) — immutable, equality by value
- State transitions: validate preconditions → mutate state → increment `_version` → `_touch()` → `_record_event()`
- `collect_events()` clears and returns pending events — call once per handler, after commit

**Application layer** (`src/contexts/*/application/`):
- Commands and queries: plain `@dataclass`, no Pydantic
- All DB work inside `async with self._uow as uow:` — never commit outside
- Idempotency: `repo.get_by_idempotency_key(key)` before any INSERT
- DTOs are plain dataclasses — no domain objects leave this layer
- Audit trail: commands include `created_by_id: uuid.UUID | None`

**Infrastructure layer** (`src/contexts/*/infrastructure/`):
- Monetary columns: `Mapped[Decimal]` with `Numeric(precision=19, scale=4)` — never `Float`
- All models include: `version`, `created_by_id`, `updated_by_id`, `deleted_at`
- `save()` must check immutable statuses and validate optimistic lock before UPDATE
- All `SELECT` queries filter `WHERE deleted_at IS NULL`
- Register every new model in `src/infrastructure/database/base.py → import_all_models()`

**API layer** (`src/contexts/*/api/`):
- `POST` endpoints that create resources: accept `Idempotency-Key` header
- Map domain exceptions to HTTP status codes in the router
- Monetary amounts in responses: `amount: str` (serialise as `str(dto.amount)`)
- Monetary amounts in requests: `amount: Decimal` with `Field(gt=0)`
- Include `version: int` in every financial resource response
- Always inject `current_user: CurrentUser = Depends(get_current_user)` on protected routes
- Auth endpoints: `@_limiter.limit("10/minute")`

**Financial safety (non-negotiable)**:
- `SETTLED` and `REVERSED` records must never be mutated
- Optimistic locking: validate `model.version == entity.version - 1` before UPDATE
- No hard deletes — soft delete only (`deleted_at`)
- DB UNIQUE constraint is the final idempotency guard
- `created_by_id` / `updated_by_id` from `CurrentUser.user_id` on every mutation

**Security**:
- Never hard-code credentials
- CORS: never `allow_origins=["*"]`
- SQL: always ORM or parameterised — never f-string into queries
- Do not log passwords, tokens, PII, or raw amounts with account identifiers

**Wiring** (when adding a new bounded context or route):
- Register model: `src/infrastructure/database/base.py → import_all_models()`
- Wire dependencies: `src/container.py`
- Include router: `src/api/router.py`

---

## Step 6 — Write tests

After implementing the code, write the tests specified in the plan task.

**Test rules**:
- `@pytest.mark.unit` — pure logic, no I/O, no DB, no external calls, no mocks of internals
- `@pytest.mark.integration` — real PostgreSQL via `db_session: AsyncSession` fixture, transaction rollback on teardown
- **Never mock the database** in integration tests — we were burned by mock/prod divergence
- Test naming: `test_{what}_{expected_outcome}` — e.g., `test_settle_increments_version`
- Use `make_<entity>(**overrides)` factory helper pattern — never repeat construction boilerplate
- Domain entities: target 100% coverage — they are pure logic

Write every unit test and integration test that the plan task lists. Do not skip tests.

---

## Step 7 — Verify

Run checks on everything you've written:

```bash
# 1. Format
make format
```

```bash
# 2. Lint
make lint
```

```bash
# 3. Type check — run mypy only on files you created/modified
mypy {space-separated list of modified src/ files}
```

```bash
# 4. Unit tests for this task
pytest {test file(s) for this task} -v -m unit
```

```bash
# 5. Integration tests (if applicable — skip if no DB fixture needed)
pytest {integration test file(s)} -v -m integration
```

Fix any failures before proceeding. Do not mark a task complete while tests are red or mypy is failing.

If `make test-integration` requires `TEST_DATABASE_URL` and it is not set, note this in the completion report and mark integration tests as "pending environment" rather than failing.

---

## Step 8 — ⚠️ MANDATORY: Update the plan file

This step is **not optional**. After every successful task execution, update the plan file.

Open the plan file and make these changes:

### 8a — Mark the task's acceptance criteria

Find the acceptance criteria checkboxes for this task and mark each completed one:
```
- [x] Completed criterion
- [ ] Not yet implemented criterion (leave unchecked)
```

### 8b — Mark the test checkboxes

Find the unit test and integration test checklists for this task and mark each test that now exists and passes:
```
- [x] `test_settle_increments_version`: ...
- [ ] `test_integration_pending_db`: ... (leave unchecked if skipped)
```

### 8c — Update the "Testing Requirements" summary section

If the plan has a consolidated "Testing Requirements" block at the bottom, mark the relevant lines:
```
- [x] **B1.1**: Unit test PLAN_CONFIGS pricing consistency...
```

### 8d — Update the "Acceptance Criteria (Summary)" section

If the plan has a top-level summary checklist, mark completed items.

### 8e — Update the plan header

Change the `**Updated**` date to today's date. If the task was the last one, change `**Status**` from `📋 Planning` to `🚧 In Progress` or `✅ Complete` as appropriate.

### 8f — Add an execution note (append at the bottom)

Append a short note at the very end of the plan file:

```markdown
---

## Execution Log

### {task-id} — {task title} — {YYYY-MM-DD}

**Status**: ✅ Complete

**Files created**:
- `{path}`

**Files modified**:
- `{path}`

**Tests**:
- Unit: {N} passed
- Integration: {N} passed / pending environment

**Notes**: {any deviations from the plan, design decisions made, or things the next task should know}
```

If an "Execution Log" section already exists, append a new entry — do not replace existing ones.

---

## Step 9 — Final report to user

Print a completion summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TASK COMPLETE: {task-id} — {task title}
Plan file updated: {plan file path}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Files created:
  {list}

Files modified:
  {list}

Tests:
  Unit       : {N} passed
  Integration: {N} passed (or "requires TEST_DATABASE_URL")

Remaining tasks in this plan:
  {list of unchecked tasks, or "None — plan complete 🎉"}

Run next:
  /run-plan {plan-file} {next-task-id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
