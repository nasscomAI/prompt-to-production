# agents.md — UC-0B Policy Summariser

role: >
  A compliance summariser for a municipal HR policy document. It reads one policy
  .txt file, parses it into numbered clauses, and emits a summary an HR officer can
  act on without opening the source. It does not interpret the policy, advise on
  individual cases, reconcile it with labour law, fill gaps the document leaves open,
  or explain why a rule exists. Its output is a navigational digest of what the
  document says — never an account of what it probably means.

intent: >
  A correct output is summary_hr_leave.txt containing an at-a-glance figures block,
  a binding-obligations index, a multi-condition register, a prohibitions list, the
  full verbatim clause record, and a verification block.
  Verifiable properties a reviewer can check without reading the code:
    1. Every numbered clause in the source (1.1 through 8.2, 29 in total) is cited in the summary.
    2. Clause 5.2 names both approvers — Department Head AND HR Director — not "approval" alone.
    3. Every one of the 10 critical clauses from the UC-0B README appears in the summary.
    4. No word in the summary body is absent from the source document, except a
       declared list of structural template words.
    5. Every quantity in the at-a-glance block carries the clause number it came from.
    6. The verification block reports counts, and reports zero omissions.

context: >
  ALLOWED INPUT — the text of the policy file at the given path, and nothing else.
  EXPLICITLY EXCLUDED — the agent must not use, and must not let leak into the output:
    Indian labour law, the Maternity Benefit Act, Shops and Establishments rules
    general HR convention, "standard practice", what other municipalities do
    the agent's own knowledge of what leave policies usually contain
    any inference about employee intent, manager discretion, or unwritten exceptions
  If the document is silent on something, the correct output is silence. A gap in the
  source is a fact about the source, not a prompt to supply the missing rule.

enforcement:
  - "CLAUSE INVENTORY COMPLETENESS: every clause id matching the pattern <section>.<number> found in the source must be cited at least once in the summary. The program parses the source clause ids, parses the clause ids cited in its own output, and writes the diff into the verification block. A non-empty omission set is a failed run, not a stylistic choice. Clause 1.2 (exclusion of daily wage workers and consultants) counts — scope clauses are the ones summaries drop first."

  - "MULTI-CONDITION PRESERVATION: any clause whose obligation carries more than one condition must have every condition enumerated separately in the MULTI-CONDITION OBLIGATIONS section, numbered, in the source's own words. Conditions include conjoined approvers ('the Department Head and the HR Director'), time limits ('within 48 hours', 'at least 14 calendar days'), preconditions ('only after exhausting all applicable paid leave'), negations of alternatives ('Manager approval alone is not sufficient', 'Verbal approval is not valid'), and scope qualifiers ('regardless of subsequent approval', 'regardless of duration'). Conjoined approvers are split into separate numbered conditions rather than listed on one line, because 'the Department Head and the HR Director' is where 'and the HR Director' goes missing downstream. Clause 5.2 requires TWO approvers; a rendering that says 'LWP requires approval' has dropped a condition and is a defect, not a shorter sentence."

  - "NO NEW INFORMATION — CHECKED, NOT PROMISED: the summary body may contain no word that does not appear in the source document, other than a fixed, declared list of structural template words (section headings, labels, digits, punctuation). The program tokenises its own output, subtracts the source vocabulary and the declared template vocabulary, and writes any remainder into the verification block as a SCOPE BLEED warning. Only lines that cite a clause id are audited: a section heading asserts nothing about the policy, while a line reading '[5.2] LWP requires approval from...' does. This is what makes 'do not hallucinate' testable: phrases like 'as is standard practice', 'typically in government organisations', or 'employees are generally expected to' introduce words absent from the source and are caught mechanically."

  - "NO PARAPHRASE OF BINDING LANGUAGE: clause text is reproduced verbatim, with only line-wrap whitespace normalised. Binding verbs are classified, never rewritten — 'must' is not restated as 'should', 'requires' is not restated as 'needs', 'is not permitted under any circumstances' is not restated as 'is generally not allowed'. Obligation softening is prevented by removing the step at which it can occur."

  - "REFUSAL BY FLAGGING, NOT BY GUESSING: when a clause cannot be shortened without losing an obligation — it is one of the 10 critical clauses, or carries two or more conditions, or contains an absolute qualifier such as 'under any circumstances', 'regardless of', 'not valid', 'not sufficient' — the summariser refuses to compress it, reproduces it verbatim, and marks it [VERBATIM-REQUIRED] with the reason. If the source file is empty, unreadable, or yields zero parsable clauses, the program writes no summary file at all and exits non-zero, because a plausible-looking empty summary is worse than a visible failure."

failure_modes_observed:
  - "Clause omission — the naive prompt 'Summarize the policy document.' returned eight bullet points covering sections 2 through 7 and silently dropped 1.2, 2.5, 2.7, 3.4, 5.4, 6.3, 8.1 and 8.2. Clause 1.2 mattered most: without it the summary reads as though the policy covers daily wage workers and consultants, which it explicitly does not. Fixed by CLAUSE INVENTORY COMPLETENESS with a machine-checked omission set."
  - "Condition drop on clause 5.2 — the naive output said 'Leave without pay requires prior approval'. Both named approvers and the sentence 'Manager approval alone is not sufficient' were gone, so the summary licensed exactly the thing the clause forbids. Fixed by MULTI-CONDITION PRESERVATION, which enumerates each condition on its own numbered line."
  - "Obligation softening — 'must submit at least 14 calendar days in advance' became 'should ideally apply two weeks ahead'; 'will be recorded as Loss of Pay' became 'may be treated as unpaid'. Two binding verbs downgraded to advisory ones. Fixed by NO PARAPHRASE OF BINDING LANGUAGE."
  - "Scope bleed — the naive output added 'in line with standard government HR practice' and 'subject to applicable labour law', neither of which appears anywhere in HR-POL-001. Fixed by the mechanical vocabulary diff in NO NEW INFORMATION."
  - "Qualifier erosion — 'regardless of subsequent approval' (2.5) and 'regardless of duration' (3.4) were both dropped, which inverts the meaning of each clause. Fixed by treating scope qualifiers as conditions subject to enumeration."

verification:
  - "Run: python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt"
  - "Check 1 — completeness: verification block reports 29 clauses parsed, 29 cited, 0 omitted."
  - "Check 2 — the 5.2 trap: grep 'Department Head' and 'HR Director' in the summary; both must appear, and the multi-condition register must list them as separate numbered conditions."
  - "Check 3 — critical 10: verification block lists all of 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2 as PRESENT."
  - "Check 4 — scope bleed: verification block reports no unsourced words."
  - "Check 5 — softening: grep 'should', 'generally', 'typically', 'ideally' in the summary; none may appear."

design_note: >
  This agent compresses structurally rather than lexically. Paraphrase is the exact
  mechanism by which all three failure modes in this UC occur, so the design removes
  the step where they can happen: the 29 clauses are never rewritten, they are indexed.
  The reader's saving is navigational — a nine-line obligations index, a register of
  every multi-condition rule, and a prohibitions list, each pointing at verbatim text —
  rather than a shorter restatement that a compliance officer cannot rely on. The
  enforcement rules above are implemented as deterministic checks for the same reason
  as UC-0A: a rule that cannot be verified on a fixed input is not a rule.