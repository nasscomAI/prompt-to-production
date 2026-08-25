---
name: commit-convention
description: Enforce Vibe Coding Workshop commit message standard [UC-ID] Fix what: why → changed for every git commit
---

# Commit Convention — Vibe Coding Workshop (Project-Only)

This skill enforces the **exact** commit message standard defined in `@README.md` (Commit Message Standard section). It applies **only to this project** (`prompt-to-production` workshop repo). No global config is modified.

## Rule (MUST follow — from README.md:89-105)

Every commit **MUST** follow:

```
[UC-ID] Fix [what]: [why it failed] → [what you changed]
```

- `UC-ID` = `UC-0A`, `UC-0B`, `UC-0C`, or `UC-X` (brackets `[]` required in README, optional in CI but prefer brackets)
- Literal word `Fix` after UC-ID
- `:` separates *what you fixed* from *why it failed*
- `→` (U+2192, not `->` or `=>`) separates *why it failed* from *what you changed*

### Good examples (from README.md:97-101)

```
[UC-0A] Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers
[UC-0B] Fix clause omission: completeness not enforced → added every-numbered-clause rule
[UC-0C] Fix silent aggregation: no scope in enforcement → restricted to per-ward per-category only
[UC-X] Fix cross-doc blending: no single-source rule → added single-source attribution enforcement
```

### CI fallback accepted by `.github/commit-lint.sh` / `.github/workflows/validate-pr.yml`

```
[UC-ID] <10+ chars description>
UC-0B Generated agents.md and skills.md from README, implemented summariser
```

> Prefer the strict `Fix ...: ... → ...` form for all 4+ required commits. The fallback is only for scaffolding if needed, but workshop reviewers flag it as weaker evidence.

## What is forbidden

Messages like `update`, `done`, `fix`, `wip`, `final`, `fix bug`, `changes` will be flagged during review and **fail CI** (`validate-pr.yml`).

Regex enforced by CI:

```
^\[?UC-[0-9A-Za-z]+\]?[[:space:]].{10,}
```

Strict workshop regex (recommended):

```
^\[UC-(0A|0B|0C|X)\] Fix .+: .+ → .+
```

## Other workshop rules tied to commits

- **One branch for entire session:** `participant/[your-name]-[city]` e.g. `participant/arshdeep-pune`. Do not create per-UC branches.
- **Minimum 4 commits** — one per UC — all on same branch, chronological CRAFT loop.
- Commit history is evidence trail — reviewer reads it to see what failed, what changed, why.

## When to use me

Load this skill **before every `git commit`** (via `bash` tool or `skill` tool). Do not commit without validating.

## Workflow — Agent MUST do before committing

1. **Read** current `git status` and `git diff --staged` to determine UC-ID.
2. **Draft** message as `[UC-ID] Fix [what]: [why it failed] → [what you changed]`
   - `[what]` = symptom (max 3-4 words)
   - `[why it failed]` = root cause
   - `[what you changed]` = concrete enforcement/fix
3. **Validate locally:**
   ```bash
   echo "[UC-0A] Fix severity blindness: no keywords → added triggers" | grep -P '^\[UC-(0A|0B|0C|X)\] Fix .+: .+ → .+'
   # If grep fails, rewrite.
   # Optional local hook check:
   bash .github/commit-lint.sh
   ```
4. **Commit** with exact message — use HEREDOC to preserve `→`:
   ```bash
   git commit -m "[UC-0A] Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers"
   # or for multi-line:
   git commit -m "[UC-0A] Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers" -m "Details: ..."
   ```
5. **Verify** `git log --oneline -5` shows correct format.

### Anti-pattern → Correction

- ❌ `git commit -m "fix"` → ✅ `[UC-0A] Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers`
- ❌ `git commit -m "update classifier"` → ✅ `[UC-0B] Fix clause omission: completeness not enforced → added every-numbered-clause rule`
- ❌ `git commit -m "UC-0A fix -> added triggers"` (wrong arrow) → ✅ use `→` (copy-paste)

## For opencode — project-only enforcement

- This skill lives in `.opencode/skills/commit-convention/SKILL.md` (project-local, not `~/.config/opencode`).
- Project config `opencode.json` sets `instructions` to include `README.md` so the rule is injected every session.
- Git hook `.git/hooks/commit-msg` (installed locally) blocks bad messages pre-commit with same regex — run `chmod +x .git/hooks/commit-msg`.
- CI final check is `.github/workflows/validate-pr.yml` + `.github/commit-lint.sh`.

If commit is rejected, fix message, do NOT use `--no-verify` without tutor approval.
