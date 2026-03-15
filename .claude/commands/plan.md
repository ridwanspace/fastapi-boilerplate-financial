---
description: Research a feature or query, then generate a structured development plan saved to docs/plan/. Usage: /plan <feature description or question>
argument-hint: "<feature description, question, or filename>"
allowed-tools: Read, Glob, Grep, Bash
---

You are a senior software architect for this FastAPI DDD project. Your job is to produce a thorough, implementation-ready development plan for the topic below.

**User query / topic**: $ARGUMENTS

---

## Step 1 — Understand the request

Parse `$ARGUMENTS`:
- If it looks like a filename (ends in `.md`, `.py`, etc.), read that file first for context.
- Otherwise treat it as a feature description or question.

Clarify the scope internally — you do not need to ask the user unless the request is genuinely ambiguous.

---

## Step 2 — Explore the codebase

Before writing anything, explore what already exists relevant to this topic.

Use Glob and Grep to find:
- Existing domain entities, value objects, exceptions related to the topic
- Existing application services, commands, queries, handlers
- Existing infrastructure models, repositories
- Existing API routes and schemas
- Existing tests covering related areas
- Related config (e.g., `src/container.py`, `src/api/router.py`, `src/infrastructure/database/base.py`)

Read key files to understand current patterns and avoid re-inventing existing solutions.

---

## Step 3 — Determine the output file path

Find the next sequential plan file number:

```bash
ls docs/plan/ | sort | tail -1
```

- If the directory is empty → use `00`
- If the last file starts with `08` → use `09`
- File name format: `{NN}-{kebab-case-topic}.md` (e.g., `03-wallet-refund-flow.md`)

---

## Step 4 — Write the plan

Save the plan to `docs/plan/{NN}-{topic}.md` using this exact structure:

```markdown
# {Descriptive Title}

**Created**: {today's date YYYY-MM-DD}
**Updated**: {today's date YYYY-MM-DD}
**Priority**: ⭐⭐⭐ (adjust 1–5 stars based on criticality)
**Status**: 📋 Planning
**Depends On**: {list any prerequisite bounded contexts or tasks, or "None"}
**Module**: {relevant bounded context, e.g., "Transaction", "Auth", "Wallet"}

---

## Overview

{2–4 sentences describing what this plan covers and why it is needed.}

---

## Prerequisites

> **CRITICAL**: These must be complete before starting

**Required Infrastructure (All Ready)**:
- [x] {prerequisite 1 — e.g., Gemini AI Provider (`src/core/ai/providers/gemini_provider.py`)}
- [x] {prerequisite 2}

**Environment**:
- [x] {required env var — e.g., `GEMINI_API_KEY` configured in `.env`}

---

## Overall Progress

| Phase | Section | Total | Done | Status |
|-------|---------|-------|------|--------|
| P0 | {section name} | {N} | 0 | Not Started |
| **Total** | | **{N}** | **0** | **0%** |

---

## Legend

- `[ ]` - Not started
- `[~]` - In progress / partial
- `[x]` - Completed
- `[!]` - Blocked

---

## What Already Exists

| Entity / File | Location | Status |
|---------------|----------|--------|
| {name} | `{path}` | ✅ Exists / 🚧 Partial / ❌ Missing |

---

## Module Structure

{Show the directory tree of files to create or modify, using a fenced code block.}

---

## Phase {N}: {Phase Name}

### Task {N}.{M}: {Task Name}

**File**: `{path/to/file.py}` (create / modify)

**Purpose**: {one sentence}

#### Implementation

{Key implementation details, patterns to follow, code snippets where helpful.}

#### Acceptance Criteria

- [ ] {Functional requirement}
- [ ] {Another requirement}

#### Unit Tests (`{test file path}`)

- [ ] `test_{what}_{expected}`: {one-line description}
- [ ] `test_{what}_{expected}`: {one-line description}

#### Integration Tests (`{test file path}`)

- [ ] `test_{what}_{expected}`: {one-line description}

---

## Financial Safety Checklist

> Only include this section if the feature touches money, billing, or transactions.

- [ ] All monetary values use `Decimal`, `ROUND_HALF_EVEN`
- [ ] Monetary columns stored as `Numeric(19,4)` in PostgreSQL
- [ ] `SETTLED` / `REVERSED` records never mutated
- [ ] Optimistic locking (`version` column) on every aggregate
- [ ] Idempotency key checked before every INSERT
- [ ] Audit trail: `created_by_id` / `updated_by_id` populated
- [ ] API responses serialise amounts as `str`, never `float`

---

## Architecture Compliance Checklist

- [ ] Domain layer has zero framework imports (no FastAPI, SQLAlchemy, Pydantic)
- [ ] `HTTPException` raised only in the API layer
- [ ] Handlers return `Ok(value) | Err(exception)` — no exceptions cross layer boundaries
- [ ] New model registered in `src/infrastructure/database/base.py → import_all_models()`
- [ ] New dependencies wired in `src/container.py`
- [ ] New router included in `src/api/router.py`
- [ ] No context imports another context directly (shared kernel only)

---

## Testing Requirements Summary

- [ ] Unit tests: `pytest -m unit tests/unit/... -v`
- [ ] Integration tests: `pytest -m integration tests/integration/... -v`
- [ ] Coverage target: domain entities 100%, overall ≥ 80%

---

## Open Questions

{List any unresolved decisions, edge cases, or dependencies that need clarification before implementation starts. Delete this section if none.}
```

---

## Step 5 — Rules for writing a good plan

Follow these when drafting:

**Content rules**:
- "What Already Exists" must reflect actual codebase state — do not guess. Read files.
- Every task must have clear acceptance criteria and at least 2 unit test cases.
- Test names must follow `test_{what}_{expected_outcome}` convention.
- Integration tests must note what fixture or seed data they require.
- Code snippets should match the actual patterns used in this codebase (e.g., `BaseEntity`, `AggregateRoot`, `Result[DTO, Exception]`, `async with self._uow as uow:`).
- Financial safety and architecture compliance checklists are mandatory for any bounded context touching money or state mutations.

**Style rules**:
- Use tables for "What Already Exists" and any comparative data.
- Use fenced code blocks for all code and directory trees.
- Use `[ ]` checkboxes for all acceptance criteria and test cases.
- Use `✅`, `🚧`, `❌` status indicators in the "What Already Exists" table.
- Priority stars: ⭐ = nice to have, ⭐⭐⭐ = standard, ⭐⭐⭐⭐⭐ = critical/blocking.

**Scope rules**:
- Do not implement code — this is a plan only.
- Do not modify any existing source files.
- Only create the plan file in `docs/plan/`.

---

## Step 6 — Confirm to the user

After saving the file, report:
1. The file path created (e.g., `docs/plan/03-wallet-refund-flow.md`)
2. A one-paragraph summary of what the plan covers
3. The number of tasks, unit tests, and integration tests defined
4. Any open questions that should be resolved before implementation
