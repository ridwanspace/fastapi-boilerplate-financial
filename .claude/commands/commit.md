---
description: Run format → lint → typecheck → unit tests, then commit staged changes with a conventional commit message. Usage: /commit [optional message hint]
argument-hint: "[optional message hint]"
allowed-tools: Bash, Read, Glob, Grep
---

You are performing a safe, pre-validated git commit for the FastAPI boilerplate project.
Work through the steps below **in order**. Stop and report to the user if any step fails — do not skip failures.

## Project context

- Language: Python 3.12+, async-first
- Architecture: DDD + Clean Architecture (`api → application → domain ← infrastructure`)
- Financial rules: `Decimal` for money, immutable `SETTLED`/`REVERSED` statuses, optimistic locking via `version`
- Test markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`
- No hard-coded credentials; no `HTTPException` in domain/application layers

Optional message hint from user: $ARGUMENTS

---

## Step 1 — Check working tree

Run `git status` and `git diff --stat HEAD` to understand what is staged and what is not.

- If **nothing is staged**, tell the user and stop. Do not auto-stage everything.
- Show the user a summary of staged vs unstaged files before proceeding.

```bash
git status
git diff --stat HEAD
```

---

## Step 2 — Format

Run the ruff formatter and auto-fixer on staged Python files only (to avoid touching unrelated files).

```bash
make format
```

If ruff modifies any files that were already staged, re-stage them automatically:

```bash
git diff --name-only | xargs -r git add
```

Report any files that were reformatted.

---

## Step 3 — Lint

```bash
make lint
```

- If lint fails, **show the errors** and stop. Do not commit over lint failures.
- The user must fix lint issues before committing.

---

## Step 4 — Type check

```bash
make typecheck
```

- If mypy reports errors, **show the errors** and stop.
- Do not commit over type errors.

---

## Step 5 — Unit tests

Run only unit tests (fast, no DB required):

```bash
make test-unit
```

- If any unit test fails, **show the failure output** and stop.
- Integration/e2e tests are not run here (they require a live DB); remind the user to run `make test-integration` separately if they changed infrastructure or repository code.

---

## Step 6 — Review staged diff

Read the staged diff to understand the change:

```bash
git diff --cached
```

Check for these project-specific issues:
- Any `float` used for monetary values (must be `Decimal`)
- Any `HTTPException` raised inside `src/contexts/*/domain/` or `src/contexts/*/application/`
- Any hard-coded secrets or credentials
- Any missing `version` field in new SQLAlchemy models
- Any `allow_origins=["*"]` or `allow_methods=["*"]` in CORS config
- Any raw f-string SQL queries

If any of the above are found, **report them and stop** — do not commit.

---

## Step 7 — Inspect recent commits for style

```bash
git log --oneline -10
```

Use this to match the project's existing commit message style.

---

## Step 8 — Draft commit message

Write a conventional commit message based on the staged diff and the optional hint: `$ARGUMENTS`

Format:
```
<type>(<scope>): <short summary>

<optional body: what changed and why, max 72 chars per line>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `ci`

Scope examples: `transaction`, `auth`, `wallet`, `infra`, `api`, `domain`, `migrations`

Rules:
- Summary line ≤ 72 characters
- Use imperative mood ("add", "fix", "remove" — not "added", "fixes")
- If a financial safety rule was enforced (e.g., added `version` column, used `Decimal`), mention it in the body
- Reference issue/ticket numbers if the user provided one in `$ARGUMENTS`

Show the drafted message to the user and ask for confirmation before committing.

---

## Step 9 — Commit

After the user confirms (or if the message is unambiguous and clearly correct):

```bash
git commit -m "$(cat <<'EOF'
<your drafted message here>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Step 10 — Post-commit summary

After a successful commit, output:

1. The commit hash and message (`git log -1 --oneline`)
2. A reminder if any of these apply:
   - Changed `src/contexts/*/infrastructure/` → run `make test-integration` before pushing
   - Changed `alembic/` → run `make migrate` on target environment
   - Changed `src/api/` or `src/container.py` → smoke-test the endpoint manually
3. Do **not** push unless the user explicitly asks
