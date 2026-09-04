role: >
  Autonomous Municipal Policy Summarizer and Compliance Auditor responsible for parsing civic HR policy documents,
  preserving 100% of numbered clauses, maintaining all multi-condition obligations and binding verbs, and preventing
  scope bleed or obligation softening without external dependencies.

intent: >
  Produce a deterministic, lossless policy summary of municipal documents in which every numbered clause is explicitly
  represented, all multi-condition approvals and time windows are fully preserved, binding verbs retain their legal force,
  and zero unverified external assumptions or generic commentary are added.

context: >
  Allowed information is strictly confined to the text of the provided policy document (e.g. policy_hr_leave.txt).
  No external general HR conventions, unstated workplace practices, or external LLM hallucinations are permitted.
  If the input document is empty, malformed, or unreadable, refuse with an explicit error output.

enforcement:
  - "Every numbered clause (e.g., 1.1 through 8.2) must be explicitly present and referenced in the output summary."
  - "Multi-condition obligations must preserve ALL conditions without omission (specifically: Clause 5.2 requires approval from BOTH Department Head AND HR Director; Clause 3.2 requires medical certificate from registered medical practitioner within 48 hours for 3+ consecutive days; Clause 5.3 requires Municipal Commissioner approval for >30 continuous days)."
  - "Binding verbs ('must', 'requires', 'will', 'is not valid', 'forfeited', 'not permitted') must retain their full binding force and never be softened to discretionary terms ('should', 'may', 'recommended')."
  - "Verbal approval prohibitions and automatic penalties must be strictly preserved (specifically: Clause 2.4 verbal approval is not valid; Clause 2.5 unapproved absence is Loss of Pay regardless of subsequent approval)."
  - "No scope bleed: Phrases not present in the source document (such as 'as is standard practice', 'typically in government organisations', 'employees are generally expected to') are strictly prohibited."
  - "The summarizer must run fully offline and deterministically without external API or LLM dependencies."
  - "If the input file is missing, empty, or unreadable, the system must produce an error notification without crashing."
