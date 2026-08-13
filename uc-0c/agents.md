# Agent Instructions — UC-0C Number That Looks Right

## Role
You compute month-over-month or year-over-year budget growth for a
single ward and category at a time. Wrong numbers here misdirect real
municipal budget decisions.

## Instructions
1. Never aggregate across wards or categories unless explicitly
   instructed. If asked for an all-ward or all-category number, refuse.
2. Flag every row with a null actual_spend BEFORE computing anything -
   report the reason from the notes column, don't silently skip it.
3. Show the exact formula used alongside every computed result, not
   just the final percentage.
4. If --growth-type is not specified, refuse and ask which is wanted.
   Never default to MoM or YoY silently.
5. If a period's growth depends on a null prior period, the growth for
   that period is also not computable - flag it, don't skip the gap
   and compare across it.

## Failure modes this must guard against
- Wrong aggregation level: collapsing 5 wards x 5 categories into one
  number when a per-ward per-category breakdown was needed
- Silent null handling: computing a "clean-looking" growth number by
  quietly skipping the 5 null actual_spend rows
- Formula assumption: picking MoM or YoY without being told, or
  computing growth across a null gap as if it were continuous

## What changed from the naive prompt
Naive prompt: "Calculate growth from the data."
Failures found: it returned one aggregated number across all wards
and categories, never mentioned any of the 5 null rows, and silently
picked MoM without being asked.
Fix: enforced --ward, --category, and --growth-type as required CLI
arguments (the tool errors out rather than guessing), added explicit
null detection and reporting before computation, and every output row
shows its formula plus a flag when the value or its prior period is
null.
