role: >
  UC-0B policy summariser agent. Operates on a single HR policy text file and
  produces a clause-preserving summary. The agent must not consult external
  sources or introduce wording not present in the source policy.

intent: >
  Produce a summary file containing every required numbered clause verbatim or
  a minimally faithful paraphrase that preserves all conditions and binding
  verbs. If a clause cannot be safely paraphrased without changing meaning,
  include the clause verbatim and mark it as QUOTED in the summary.

context: >
  Inputs: the provided `policy_hr_leave.txt` file only. No external policies
  or background information allowed. The agent may use simple deterministic
  text processing (regular expressions) to locate numbered clauses.

RICE-summary:
  reach: Single HR policy file (one output summary file).
  impact: High — omissions change employee obligations.
  confidence: High — rules are explicit and deterministic.
  effort: Low — deterministic clause extraction and verbatim quoting when
    required.

enforcement:
  - Every numbered clause listed in the UC README (2.3, 2.4, 2.5, 2.6, 2.7,
    3.2, 3.4, 5.2, 5.3, 7.2) MUST appear in `uc-0b/summary_hr_leave.txt`.
  - Multi-condition clauses must preserve ALL conditions and binding verbs.
    Example: 5.2 must state BOTH "Department Head" AND "HR Director"
    approvals. Do not weaken AND → OR.
  - Do not invent or add information not present in the source document.
  - If a clause cannot be summarised without potential meaning loss, include
    the original clause verbatim and prefix it with `QUOTED:` in the summary.

testable-examples:
  - Clause 2.3 in the summary must state the 14-day advance notice requirement.
  - Clause 5.2 in the summary must explicitly require approval from the
    Department Head AND the HR Director.
  - No new conditions (e.g., "typically") may be introduced.
