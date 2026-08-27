# agents.md — UC-0B Policy Summary Guardrails

## Objective
Produce a legally faithful summary of `../data/policy-documents/policy_hr_leave.txt` into `uc-0b/summary_hr_leave.txt`.
Primary risk to prevent: meaning drift through omission, softening, or added assumptions.

## Agent Topology
Use a 3-agent flow with explicit handoffs:

1. **Retriever Agent**
   - Loads source policy text.
   - Parses numbered clauses into structured records.
   - Output schema per clause:
     - `clause_id`
     - `raw_text`
     - `obligation`
     - `binding_verbs`
     - `conditions`

2. **Summarizer Agent**
   - Generates one summary line per clause with clause references.
   - Preserves legal force and all conditions.
   - If concise paraphrase risks meaning loss, quotes clause verbatim and marks it `FLAG_VERBATIM`.

3. **Verifier Agent**
   - Compares summary against clause inventory and source text.
   - Blocks output if any required clause/condition is missing, softened, or invented.

## Mandatory Enforcement Rules
1. Every numbered clause must be present in the summary.
2. Multi-condition obligations must preserve **all** conditions; never drop one silently.
3. Never add information not present in the source document.
4. If a clause cannot be summarized without meaning loss, quote it verbatim and flag it.

## Ground-Truth Clause Inventory (Must Be Preserved)
- **2.3**: 14-day advance notice required (`must`)
- **2.4**: Written approval required before leave commences; verbal not valid (`must`)
- **2.5**: Unapproved absence = LOP regardless of subsequent approval (`will`)
- **2.6**: Max 5 days carry-forward; above 5 forfeited on 31 Dec (`may` / `are forfeited`)
- **2.7**: Carry-forward days must be used Jan–Mar or forfeited (`must`)
- **3.2**: 3+ consecutive sick days requires medical cert within 48hrs (`requires`)
- **3.4**: Sick leave before/after holiday requires cert regardless of duration (`requires`)
- **5.2**: LWP requires Department Head **and** HR Director approval (`requires`)
- **5.3**: LWP >30 days requires Municipal Commissioner approval (`requires`)
- **7.2**: Leave encashment during service is not permitted under any circumstances (`not permitted`)

## Known Trap (Hard Fail)
Clause **5.2** requires **two approvers**. Any summary that says only “requires approval” is invalid if it does not explicitly include both:
- Department Head
- HR Director

## Validation Checklist Before Final Output
- Coverage check: all 10 required clauses present.
- Condition integrity check: no condition loss in any clause.
- Binding check: preserve force words (`must`, `requires`, `will`, `not permitted`, `forfeited`).
- Scope check: no external phrases or assumptions (for example: “standard practice”, “typically”, “generally expected”).
- Verbatim fallback check: ambiguous/high-risk clauses are quoted and flagged.

## Output Contract
- File: `uc-0b/summary_hr_leave.txt`
- Format: one line per clause, with clause id prefix (for example `2.3:`).
- If flagged verbatim, prepend `FLAG_VERBATIM:` and include exact clause text.

## Failure Handling Protocol
If verification fails:
1. Return a structured error list by `clause_id`.
2. Specify failure type: `MISSING_CLAUSE`, `CONDITION_DROP`, `OBLIGATION_SOFTENING`, or `SCOPE_BLEED`.
3. Regenerate only failed lines; re-run full verifier before writing file.

## Minimal Prompting Pattern
- Retriever prompt: “Extract numbered policy clauses exactly and structure obligation + conditions.”
- Summarizer prompt: “Summarize clause-by-clause with no added facts, preserving all conditions and binding verbs.”
- Verifier prompt: “Detect any omission, condition drop, obligation softening, or scope bleed against source.”
