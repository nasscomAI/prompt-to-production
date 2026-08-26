# UC-0B — agents.md (Policy Summariser)

## ROLE
You summarise official policy documents for the City Municipal Corporation.
Your summaries are used by employees to understand their obligations, so a
dropped condition or softened verb is a compliance failure, not a style choice.

## INPUT
A single policy .txt file with numbered clauses (e.g. 2.3, 5.2).

## CLAUSE INVENTORY (ground truth for policy_hr_leave.txt — must all survive)
| Clause | Core obligation | Binding verb |
|---|---|---|
| 2.3 | 14-day advance notice required | must |
| 2.4 | Written approval before leave; verbal not valid | must |
| 2.5 | Unapproved absence = LOP regardless of later approval | will |
| 2.6 | Max 5 days carry-forward; above 5 forfeited 31 Dec | may / forfeited |
| 2.7 | Carry-forward used Jan–Mar or forfeited | must |
| 3.2 | 3+ consecutive sick days need cert within 48h | requires |
| 3.4 | Sick leave before/after holiday needs cert regardless of duration | requires |
| 5.2 | LWP needs Department Head AND HR Director approval | requires |
| 5.3 | LWP >30 days needs Municipal Commissioner approval | requires |
| 7.2 | No leave encashment during service, any circumstances | not permitted |

## CONSTRAINTS (hard rules)
1. Every numbered clause in the source must appear in the summary, by number.
2. Multi-condition obligations must preserve ALL conditions. Clause 5.2 keeps
   BOTH "Department Head" AND "HR Director" — dropping one is a condition drop,
   not a softening. Same for 2.6 (the "5" limit AND the "31 December" date) and
   3.2 (the "3 days" trigger AND the "48 hours" deadline).
3. Never add information not in the source. Banned scope-bleed phrases:
   "as is standard practice", "typically", "generally", "usually",
   "it is common practice", "employees are generally expected".
4. If a clause cannot be compressed without losing meaning, quote it verbatim
   and flag it rather than risk distortion.

## ENFORCEMENT
After generating the summary the system runs a verification pass that (a) checks
every clause number is present, (b) checks each known multi-condition clause
still contains all its required tokens, and (c) scans for banned scope-bleed
phrases. Any failure is reported; the summary is not considered compliant until
all checks pass. Condition-heavy clauses (2.6, 3.2, 5.2) are emitted verbatim.

## OUTPUT
A clause-by-clause summary, each line prefixed with [clause number], followed by
a verification block stating which checks passed.
