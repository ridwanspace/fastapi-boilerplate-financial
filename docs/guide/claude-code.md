# Developing with Claude Code

> **Navigation:** [README](../../README.md) · [Adding a Bounded Context](adding-a-bounded-context.md) · [Architecture](architecture.md)

This project ships with a `.claude/` configuration directory that makes Claude Code context-aware of the architecture, financial rules, and team conventions. When you open this project in Claude Code, it automatically enforces the right rules for the layer you are editing.

---

## Table of Contents

- [Slash Commands](#slash-commands)
- [Context-Aware Rule Files](#context-aware-rule-files)
- [Typical Development Workflow](#typical-development-workflow)

---

## Slash Commands

Three custom slash commands are available in Claude Code:

| Command | Usage | What it does |
|---|---|---|
| `/plan` | `/plan <feature description>` | Researches the codebase, then generates a structured implementation plan saved to `docs/plan/`. Includes tasks, acceptance criteria, unit/integration test lists, financial safety checklist, and architecture compliance checklist. |
| `/run-plan` | `/run-plan <plan-file> <task-id>` | Executes a single task from a plan file. Reads the plan, explores the codebase, implements the code, writes the specified tests, runs format/lint/typecheck/tests, and updates the plan file with progress. |
| `/commit` | `/commit [message hint]` | Runs `format → lint → typecheck → unit tests` in order, reviews the staged diff for financial safety violations, drafts a conventional commit message, and commits only after your confirmation. |

**Example workflow:**

```bash
# 1. Ask Claude to plan a new feature
/plan add wallet balance tracking with multi-currency support

# 2. Execute tasks one by one from the generated plan
/run-plan docs/plan/00-wallet-balance.md 1.1
/run-plan docs/plan/00-wallet-balance.md 1.2

# 3. Commit when ready
/commit
```

See [Adding a Bounded Context](adding-a-bounded-context.md) for the feature structure that `/plan` and `/run-plan` follow.

---

## Context-Aware Rule Files

The `.claude/rules/` directory contains layer-specific guidelines that Claude Code loads automatically based on which files you are editing:

| Rule File | Auto-loaded when editing | What it enforces |
|---|---|---|
| `rules/domain.md` | `src/contexts/*/domain/**/*.py` | Zero framework imports, state transition pattern, `Money` arithmetic, event collection |
| `rules/application.md` | `src/contexts/*/application/**/*.py` | `Result[T]` return type, UoW usage, idempotency check before INSERT, audit trail |
| `rules/infrastructure.md` | `src/contexts/*/infrastructure/**/*.py` | `Numeric(19,4)` for money, optimistic locking validation, soft-delete filter on all SELECTs |
| `rules/api.md` | `src/contexts/*/api/**/*.py` | `Idempotency-Key` header, domain exception → HTTP mapping, `amount` as `str` in responses |
| `rules/migrations.md` | `alembic/**/*.py` | Required financial columns, column rename strategy, autogenerate review checklist |
| `rules/security.md` | **All files** | No hard-coded credentials, CORS whitelist, no f-string SQL, signed URL expiry |
| `rules/testing.md` | `tests/**/*.py` | Test marker discipline, no DB mocks in integration tests, naming conventions |

These rules map directly to the [Layer Responsibilities](architecture.md#layer-responsibilities) in the architecture guide.

You do not need to reference these manually — Claude Code picks them up based on the file path.

---

## Typical Development Workflow

```
1. /plan <new feature>          → plan saved to docs/plan/NN-feature.md
2. /run-plan <plan> <task-1.1>  → domain entity created + unit tests passing
3. /run-plan <plan> <task-1.2>  → application handler created + tests passing
4. /run-plan <plan> <task-1.3>  → repository + integration tests passing
5. /run-plan <plan> <task-1.4>  → API router created + e2e tests passing
6. /commit                      → format, lint, typecheck, unit tests, then commit
```

The `/run-plan` command updates the plan file after each task, tracking progress with `[x]` checkboxes and an execution log at the bottom of the file.

---

## Related Guides

- [Adding a Bounded Context](adding-a-bounded-context.md) — what `/plan` and `/run-plan` implement
- [Architecture](architecture.md) — the layer structure that rule files enforce
- [Testing](testing.md) — test conventions enforced by `rules/testing.md`
- [Back to README](../../README.md)
