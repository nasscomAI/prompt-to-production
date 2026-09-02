# agents.md - UC-0B Policy Summarizer

role: >
  Act as a source-faithful employee leave policy summarization specialist.
  Extract and summarize the numbered rules in the supplied policy document
  without changing their scope, conditions, limits, deadlines, exceptions, or
  binding force.

intent: >
  Produce a complete, checkable summary of the source policy. Every required
  clause in the UC-0B inventory must appear with its clause reference, and no
  source obligation may be omitted, weakened, or supplemented with information
  that is not in the policy.

context: >
  The source is ../data/policy-documents/policy_hr_leave.txt. The output is a
  summary written to uc-0b/summary_hr_leave.txt. The README identifies these
  ten clauses as the completeness ground truth:

  2.3: Employees must submit a leave application at least 14 calendar days in
  advance using Form HR-L1.
  2.4: Leave applications must receive written approval from the employee's
  direct manager before leave commences; verbal approval is not valid.
  2.5: Unapproved absence will be recorded as Loss of Pay (LOP) regardless of
  subsequent approval.
  2.6: Employees may carry forward a maximum of 5 unused annual leave days to
  the following calendar year; days above 5 are forfeited on 31 December.
  2.7: Carry-forward days must be used within January-March of the following
  year or they are forfeited.
  3.2: Sick leave of 3 or more consecutive days requires a medical certificate
  from a registered medical practitioner, submitted within 48 hours of
  returning to work.
  3.4: Sick leave immediately before or after a public holiday or annual leave
  period requires a medical certificate regardless of duration.
  5.2: LWP requires approval from both the Department Head and the HR Director;
  manager approval alone is not sufficient.
  5.3: LWP exceeding 30 continuous days requires Municipal Commissioner approval.
  7.2: Leave encashment during service is not permitted under any circumstances.

  The full source document is authoritative for wording and scope. The summary
  may include other source clauses, but it must not replace, merge, or omit any
  of the ten required inventory clauses.

enforcement:
  - rule: "Include every required clause reference: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2"
    test: "Extract clause references from the summary and assert that all ten required references occur at least once."

  - rule: "Every summarized clause must include its exact source clause number"
    test: "For each required clause, assert that its summary text is attached to the matching reference, not presented as an unreferenced general paragraph."

  - rule: "Preserve every condition in a multi-condition obligation"
    test: "Compare each required clause with its source conditions and reject a summary that omits a threshold, actor, timing condition, exception, consequence, or second approver."

  - rule: "Clause 5.2 must state both Department Head and HR Director approval and that manager approval alone is not sufficient"
    test: "Require the strings or unambiguous equivalents for Department Head, HR Director, both approvals, and manager approval alone not being sufficient in the 5.2 item."

  - rule: "Preserve Clause 2.3's 14 calendar days and Form HR-L1 requirement"
    test: "Require 14, calendar days, advance submission, and Form HR-L1 in the 2.3 item."

  - rule: "Preserve Clause 2.4's written direct-manager approval before leave commences and verbal approval not being valid"
    test: "Require written approval, direct manager, before leave commences, and verbal approval not valid in the 2.4 item."

  - rule: "Preserve Clause 2.5's LOP consequence and regardless-of-subsequent-approval condition"
    test: "Require unapproved absence, Loss of Pay or LOP, and regardless of subsequent approval in the 2.5 item."

  - rule: "Preserve Clause 2.6's maximum of 5 days, following-calendar-year scope, and 31 December forfeiture of days above 5"
    test: "Require 5, carry-forward, following calendar year, above-5 days, and 31 December forfeiture in the 2.6 item."

  - rule: "Preserve Clause 2.7's mandatory January-March use period and forfeiture consequence"
    test: "Require must-use wording, January-March or first quarter, following year, and forfeiture in the 2.7 item."

  - rule: "Preserve Clause 3.2's 3-or-more consecutive-day threshold, registered medical practitioner, and 48-hour return-to-work deadline"
    test: "Require all three conditions and the deadline in the 3.2 item; reject a summary that merely says longer sick leave may need a certificate."

  - rule: "Preserve Clause 3.4's immediately-before-or-after relationship to a public holiday or annual leave period and regardless-of-duration condition"
    test: "Require both adjacent timing cases, both leave-context types, medical certificate, and regardless of duration in the 3.4 item."

  - rule: "Preserve Clause 5.3's more-than-30-continuous-days threshold and Municipal Commissioner approval"
    test: "Require exceeding 30 continuous days and Municipal Commissioner approval in the 5.3 item."

  - rule: "Preserve Clause 7.2's prohibition on leave encashment during service under any circumstances"
    test: "Require during service, leave encashment, and not permitted under any circumstances in the 7.2 item."

  - rule: "Preserve source binding force and do not soften must, requires, will, forfeited, or not permitted"
    test: "Compare modal meaning in each summary item with the source and reject words such as may, should, generally, or typically when they weaken a source obligation."

  - rule: "Never add information absent from the policy"
    test: "Check every factual claim against the source document and reject invented actors, processes, limits, reasons, exceptions, or consequences."

  - rule: "If a clause cannot be summarized without losing meaning, quote that clause verbatim and flag it for review"
    test: "For any flagged clause, require a verbatim source quotation and an explicit review flag; do not accept an unsupported paraphrase."

  - rule: "Do not use generic policy language absent from the source"
    test: "Reject phrases such as 'as is standard practice', 'typically in government organisations', or 'employees are generally expected to' unless the exact wording appears in the source."

  - rule: "Keep the summary within the source policy's scope"
    test: "Reject claims about policies, legal requirements, customary practice, or employee groups not stated in the source document."
