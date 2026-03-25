# UC-0B — Summary That Changes Meaning

**Core failure modes:** Clause omission · Scope bleed · Obligation softening

---

## Your Input File
```
../data/policy-documents/policy_hr_leave.txt
```

## Your Output File
```
uc-0b/summary_hr_leave.txt
```

## Run Command
```bash
python app.py \
  --input ../data/policy-documents/policy_hr_leave.txt \
  --output summary_hr_leave.txt
```

---

## Do This Before Writing Any Prompt — Clause Inventory

Read `policy_hr_leave.txt` and map these 10 clauses. This is your ground truth.

| Clause | Core obligation | Binding verb |
|---|---|---|
| 2.3 | 14-day advance notice required | must |
| 2.4 | Written approval required before leave commences. Verbal not valid. | must |
| 2.5 | Unapproved absence = LOP regardless of subsequent approval | will |
| 2.6 | Max 5 days carry-forward. Above 5 forfeited on 31 Dec. | may / are forfeited |
| 2.7 | Carry-forward days must be used Jan–Mar or forfeited | must |
| 3.2 | 3+ consecutive sick days requires medical cert within 48hrs | requires |
| 3.4 | Sick leave before/after holiday requires cert regardless of duration | requires |
| 5.2 | LWP requires Department Head AND HR Director approval | requires |
| 5.3 | LWP >30 days requires Municipal Commissioner approval | requires |
| 7.2 | Leave encashment during service not permitted under any circumstances | not permitted |

**The trap:** Clause 5.2 requires TWO approvers. AI will often preserve "requires approval" but drop "from both Department Head and HR Director." That is a condition drop — not a softening.

---

## Enforcement Rules Your agents.md Must Include
1. Every numbered clause must be present in the summary
2. Multi-condition obligations must preserve ALL conditions — never drop one silently
3. Never add information not present in the source document
4. If a clause cannot be summarised without meaning loss — quote it verbatim and flag it

---

## Skills to Define in skills.md
- `retrieve_policy` — loads .txt policy file, returns content as structured numbered sections
- `summarize_policy` — takes structured sections, produces compliant summary with clause references

---

## What Will Fail From the Naive Prompt
Run `"Summarize the policy document."` first.
Then check: which of the 10 clauses above are missing? Which have had conditions dropped?
Scope bleed to look for: phrases like "as is standard practice", "typically in government organisations", "employees are generally expected to" — none of these are in the source document.

---

## Commit Formula
```
UC-0B Fix [failure mode]: [why it failed] → [what you changed]
```
