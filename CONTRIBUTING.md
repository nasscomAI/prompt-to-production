# Contributing to civic-vibe-coding

This file explains how to work in this repo during the workshop.
Read it once before starting. It answers the questions participants ask most.

---

## The Mental Model

This repo is not a collaborative codebase. It is a portfolio of engineering evidence.

You are not contributing features to a shared product.
You are building four systems — one per UC — and leaving a trail that proves
you understood what failed and why, and what you did to fix it.

The trail is: your `agents.md` files, your `skills.md` files, your code, and your commit history.
The PR is the submission. The commit history is the argument.

---

## Branching

**Create one branch at the start of the session. Use it for all four UCs.**

```bash
git checkout -b participant/[your-name]-[city]
```

| ✅ Correct | ❌ Wrong |
|---|---|
| `participant/arshdeep-pune` | `uc-0a-arshdeep` |
| `participant/priya-hyderabad` | `arshdeep/uc-0a` |
| `participant/rahul-kolkata` | `main` |
| `participant/deepa-ahmedabad` | `feature/classifier` |

**Why one branch for all UCs?**

Your commit history is your CRAFT evidence trail.
A reviewer reading `git log` on your branch should see:

```
UC-0A Fix severity blindness: no keywords → added injury/child/school triggers
UC-0B Fix clause omission: completeness unenforced → added every-clause rule
UC-0C Fix silent aggregation: no scope → enforced per-ward per-category
UC-X  Fix cross-doc blending: no single-source rule → added attribution enforcement
```

That sequence — in order, on one branch — is readable as a learning journey.
Four separate branches would break that narrative.

---

## Folder Structure

Work only inside your UC's folder. Do not modify files in other UC folders or in `data/`.

```
uc-0a/          Your UC-0A work lives here
uc-0b/          Your UC-0B work lives here
uc-0c/          Your UC-0C work lives here
uc-x/           Your UC-X work lives here
data/           Read-only — do not modify
tutor-only/     Not for participants — do not open or modify
```

For each UC, you create or modify exactly three files:

| File | How |
|---|---|
| `agents.md` | Generate from your RICE prompt using AI, then manually refine |
| `skills.md` | Generate using AI, then manually refine |
| `classifier.py` (UC-0A) or `app.py` (UC-0B/C/X) | Vibe-coded using AI, CRAFT-tested by you |

You may also create output files in the UC folder:
- `uc-0a/results_[city].csv`
- `uc-0b/summary_hr_leave.txt`
- `uc-0c/growth_output.csv`

---

## Commit Discipline

### The formula
```
[UC-ID] Fix [what]: [why it failed] → [what you changed]
```

### Why this formula matters
The commit message is not for Git housekeeping.
It is the answer to the question: **"What did you learn from this failure?"**

A reviewer reading your commit message should be able to reconstruct:
- What the AI produced that was wrong
- Why it was wrong (which failure mode)
- What enforcement rule or code change you made to fix it

### Good commits
```
UC-0A Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers
UC-0A Fix taxonomy drift: AI invented categories → restricted to fixed enum of 9 values
UC-0B Fix clause omission: completeness not enforced → added every-numbered-clause rule
UC-0B Fix condition drop: clause 5.2 lost second approver → added multi-condition preservation rule
UC-0C Fix silent aggregation: no ward/category scope → enforced per-ward per-category only
UC-0C Fix null skipping: nulls not flagged → added load_dataset null report before compute
UC-X  Fix cross-doc blending: no single-source rule → added single-source attribution enforcement
UC-X  Fix hedged hallucination: no refusal template → added exact refusal wording to enforcement
```

### Bad commits — these will be flagged in review
```
update
fix
done
UC-0A done
final version
working now
test
wip
```

### When to commit
After each UC — after your Fix step and before moving to the next UC.
You may commit more than once per UC if you made multiple distinct fixes.
You must commit at least once per UC — minimum 4 commits total.

---

## The Workflow Per UC

Every UC follows this sequence. Do not skip steps.

```
1. Read the UC README                 (before touching the AI tool)
2. Read the input file(s)             (before writing any prompt)
3. Run the naive prompt               (this IS the Control step — see the failure)
4. Write your RICE prompt
5. Generate agents.md from RICE prompt using AI
6. Manually refine agents.md
7. Generate skills.md using AI
8. Manually refine skills.md
9. Generate code using AI
10. Run from CLI (python classifier.py / python app.py)
11. Analyze output — name the failure mode
12. Fix — change one thing, re-run, compare
13. git add → git commit → continue
```

The naive prompt run (step 3) is not optional.
You cannot write a good Enforcement rule for a failure you haven't seen.

---

## Submitting Your PR

When all four UCs are done:

```bash
git add .
git commit -m "UC-X Fix [whatever your last fix was]"
git push origin participant/[your-name]-[city]
```

Then open a Pull Request against `main` on the upstream repo.

- Use the PR template — every section must be filled
- PR title: `[City] [Name] — Vibe Coding Submission`
- Do not open the PR until all 4 UCs are done and committed

### What the PR template asks for
For each UC: which failure mode you found, which enforcement rule fixed it,
your commit message, and specific output verification (e.g. "all severity rows return Urgent").

Plus a CRAFT reflection and one forward-looking application of the framework.

---

## Things That Will Be Flagged in Review

| Issue | Why it matters |
|---|---|
| `agents.md` unchanged from AI draft | The AI's first draft is a starting point. Accepting it without refinement means you didn't find its gaps. |
| Generic enforcement: "be accurate" | Not testable. Not a rule. A wish. |
| Commit message: "update" or "done" | Tells the reviewer nothing. The message must name the failure. |
| UC-0A: severity rows not Urgent | The most consequential failure in the workshop. Must be fixed. |
| UC-0C: one aggregated number | Operationally useless. Must be per-ward per-category. |
| UC-X: personal-phone question blended | The answer must come from one document. Not two. |
| PR template sections blank or one word | The PR is the submission. Blank sections = no evidence. |

---

## What Not to Do

- **Do not modify files in `data/`** — these are shared input files
- **Do not push to `main`** — your work goes on your `participant/` branch
- **Do not open more than one PR** — one branch, one PR, all four UCs
- **Do not create branches per UC** — see Branching section above
- **Do not accept AI output without reading it** — agents.md must be manually reviewed and refined
- **Do not fix everything at once** — change one thing per CRAFT cycle, re-run, then fix the next thing

---

## Getting Help

Blocked for more than 5 minutes → flag your tutor. Do not debug alone.

Git confusion → ask your assistant tutor or check the [Git Cheat Sheet](https://git-scm.com/cheat-sheet).

AI tool not working → switch to any other available tool.
The workflow is tool-agnostic. Your RICE prompt, agents.md, and skills.md are identical
regardless of whether you use Claude, Gemini, Copilot, or Cursor.
