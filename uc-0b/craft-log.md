# UC-0B — CRAFT log

## C — Clause inventory built first, before any prompt

The README's instruction to inventory the 10 clauses *before* opening an AI tool is the
whole exercise. Without the inventory there is no way to detect a dropped clause,
because a summary missing clause 5.3 reads exactly as fluent as one containing it.
Those 10 refs are encoded as `GROUND_TRUTH_CLAUSES` in `app.py` so the check is run by
the program, not by my eyes.

## R — Run: what the naive prompt loses

Naive prompt: `"Summarize the policy document."`

| Failure mode | Concrete loss in `policy_hr_leave.txt` |
|---|---|
| Clause omission | 29 numbered clauses in the source. A fluent prose summary keeps roughly the section level — 8 headings — and silently drops the low-signal-looking ones: 2.7 (carry-forward expires Jan–Mar), 3.4 (cert required around holidays regardless of duration), 5.3 (>30 days needs the Commissioner) |
| Condition dropping | 5.2 becomes "LWP requires approval". Both named approvers vanish. The summary is still *true*; it is just no longer *sufficient to act on* |
| Obligation softening | 2.4 "must receive written approval" → "should be approved"; 7.2 "is not permitted under any circumstances" → "is generally not allowed" |
| Scope bleed | "as is standard practice", "employees are generally expected to" — phrases with no counterpart anywhere in the source |

## A — The architectural decision that makes two of these impossible

Rather than instruct the summariser not to soften and not to invent, the compressor is
**deletion-only**. It has no substitution path at all.

- Softening `must` → `should` requires **substitution**. Not implemented ⇒ cannot happen.
- Inventing "as is standard practice" requires **insertion**. Not implemented ⇒ cannot happen.

Both failures are then *also* verified after the fact, because an architectural argument
is not evidence:

| Check in `summarize_policy` | What it proves |
|---|---|
| every source clause ref present in output | no clause omission |
| every binding verb in a source clause still present in its entry | no softening |
| token set of each entry ⊆ token set of its source clause | no scope bleed, per clause |
| banned-phrase scan over the whole output | no scope bleed, globally |

All four raise **before** the file is written, so a defective summary never lands on disk.

## F — Two real bugs found by reading my own output

Both were introduced by me, caught by inspecting the first run, and are the reason this
log exists.

**Bug 1 — an inverted obligation.** First run rendered 5.2 as:

```
    conditions that must ALL hold:
      - approver: Department Head
      - approver: HR Director
      - approver: Manager          <-- WRONG
```

The clause says *"Manager approval alone is **not sufficient**."* Listing Manager as a
required approver under a heading reading "must ALL hold" **inverts the clause** — it
turns an exclusion into a requirement. This is the UC-0B failure mode reproduced by my
own code, one layer down: I preserved every word of the clause and still changed its
meaning through structure.

Fix: role extraction is now sentence-scoped and negation-aware (`INSUFFICIENCY_MARKERS`).
A role named in a sentence containing "not sufficient" / "alone is not" / "not valid" is
emitted as an exclusion:

```
      - required approver: Department Head
      - required approver: HR Director
      - NOT sufficient alone: Manager
```

The heading was also corrected — "conditions that must ALL hold" was itself the lie.

**Bug 2 — a truncated condition is a dropped condition.** Clause 2.6's qualifier was
cut by an arbitrary word cap:

```
      - qualifier: maximum of 5 unused annual leave days to the        <-- clipped
```

"following calendar year" — the part that says *which* year — was gone. The cap was
removed; the regex already terminates at the clause boundary.

```
      - qualifier: maximum of 5 unused annual leave days to the following calendar year
```

## T — Tested

```
$ python3 app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
Wrote summary_hr_leave.txt
  clauses in source / represented : 29 / 29
  quoted verbatim                 : 27
  multi-condition enumerated      : 12
  README ground-truth clauses     : 10/10
  scope-bleed phrases             : none
  softened binding verbs          : none
```

Negative test — the scope-bleed gate must actually block a write, not just report:

```
$ cp ../data/policy-documents/policy_hr_leave.txt tampered.txt
$ echo "9.1 Employees are generally expected to plan leave as is standard practice." >> tampered.txt
$ python3 app.py --input tampered.txt --output should_not_exist.txt
REFUSED to write summary — scope-bleed phrase present in output:
  ['as is standard practice', 'standard practice', 'generally expected']
$ echo $?
1
$ ls should_not_exist.txt
ls: should_not_exist.txt: No such file or directory
```

Non-zero exit, no file on disk. A check that logs a warning and writes the file anyway
is not a check.

## The finding worth carrying out of this UC

27 of 29 clauses are meaning-critical — they carry a number, a deadline, an approver or
an absolute prohibition. **This document is not compressible.** Any summary of it that
is meaningfully shorter has dropped something that changes a decision. The correct
output is therefore a *restructured, verified, fully-cited* rendering, not a shorter one
— and "make it shorter" was the wrong goal to accept from the naive prompt in the first
place.
