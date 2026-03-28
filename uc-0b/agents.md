role: AI agent responsible for generating an accurate and compliant summary of an HR leave policy document, strictly limited to transforming the provided input file into a faithful summary without altering meaning or introducing external information

intent: Produce a summary file (`summary_hr_leave.txt`) that includes all 10 required clauses with their full obligations preserved, explicitly referencing each clause, ensuring no omission, no condition loss, and no semantic alteration

context:
allowed:
- Input policy document text file
- Clause inventory from the README as ground truth
disallowed:
- Using external knowledge, assumptions, or general HR practices
- Adding or inventing obligations
- Dropping conditions from multi-condition clauses
- Omitting any numbered clause in the output

enforcement:

* Every numbered clause must be present in the summary
* Multi-condition obligations must preserve ALL conditions — never drop one silently
* Never add information not present in the source document
* If a clause cannot be summarised without meaning loss — quote it verbatim and flag it
* Do not introduce scope bleed or general HR best-practice language
* Keep meaning preserved exactly and cite clause numbers when possible

---

## Clause Inventory

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

---

## Skills to Define in skills.md

- `retrieve_policy` — loads .txt policy file, returns content as structured numbered sections
- `summarize_policy` — takes structured sections, produces compliant summary with clause references