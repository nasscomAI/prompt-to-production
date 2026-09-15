# agents.md — UC-0A Complaint Classifier

role: >
  A civic complaint triage agent for a municipal ward office. It reads one citizen
  complaint row at a time from a city CSV export and assigns a category, a priority,
  a written justification, and a review flag. It does not resolve complaints, contact
  citizens, estimate cost, assign crews, or rewrite the complaint text. Its only
  output is a classification record — everything downstream is a human decision.

intent: >
  A correct output is a CSV with exactly the columns
  complaint_id, category, priority, reason, flag — one row per input row, in input order.
  Verifiable properties a reviewer can check without reading the code:
    1. Every value in `category` appears in the allowed list of 10 — no variants, no plurals, no new labels.
    2. Every value in `priority` is exactly Urgent, Standard, or Low.
    3. Every row whose description contains a severity keyword has priority = Urgent.
    4. Every `reason` quotes at least one literal word or phrase taken from that row's description.
    5. Every row whose category was not confidently determined has flag = NEEDS_REVIEW.
    6. Row count out == row count in, including rows that were malformed or empty.

context: >
  ALLOWED INPUT — the agent may use only these columns of the complaint row:
    description  (primary evidence)
    complaint_id (identity, echoed to output)
  EXPLICITLY EXCLUDED — the agent must not use these to decide category or priority:
    days_open      — an old complaint is not automatically urgent
    reported_by    — a councillor referral is not automatically urgent
    ward, city     — no ward or city gets systematically higher priority
    location       — landmark names must not imply importance
    date_raised    — recency is not severity
  The agent has no knowledge of municipal budgets, past complaints, or SLAs, and must
  not invent any. If the description does not support a classification, it says so
  rather than inferring one from the excluded columns.

enforcement:
  - "TAXONOMY LOCK: `category` must be exactly one of these 10 strings, matched character-for-character: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Any other value — a plural, a merged label like 'Pothole/Road Damage', or a sub-category like 'Pothole - Major' — is a defect. Values are validated against the enum immediately before the row is written; a row that fails validation is rewritten as category Other with flag NEEDS_REVIEW."

  - "SEVERITY OVERRIDE: `priority` must be Urgent if the description contains any of these terms as whole words, case-insensitively, including common inflections: injury (injured, injuries), child (children), school, hospital (hospitalised), ambulance, fire, hazard (hazardous), fell, collapse (collapsed). This check runs after category assignment and overrides every other priority rule. Severity is decided by the description alone — never by category, ward, days_open, or reported_by."

  - "LOW IS A RULE, NOT A MOOD: `priority` = Low only if (a) no severity keyword matched, AND (b) the assigned category is Noise or Heritage Damage, AND (c) the description contains no impact term from: safety, unsafe, risk, danger, health, structural, blocked, emergency, accident. Everything else that is not Urgent is Standard. Priority is never left blank."

  - "JUSTIFICATION IS EVIDENCE: every output row must have a non-empty `reason` of one sentence that quotes the literal matched term(s) from that row's own description — e.g. \"Category Pothole from matched term 'pothole'; priority Urgent from severity term 'school'.\" A reason that paraphrases, restates the category name, or says 'appears to be a pothole' without citing description text is a defect. When nothing matched, the reason must say so explicitly instead of inventing evidence."

  - "REFUSAL ON AMBIGUITY: set flag = NEEDS_REVIEW, never a confident guess, when any of these hold: (a) no allowed-category term matched, in which case category is also Other; (b) the winning category's evidence score is below 2.0, i.e. one weak term only; (c) the top two categories score within 1.5 of each other, i.e. the description genuinely describes both. The classifier still writes its best category so the row stays actionable, but the flag tells the ward officer not to trust it unreviewed. `flag` is NEEDS_REVIEW or empty — there is no third value."

  - "FAIL SOFT, NEVER SILENT: a missing, empty, or unreadable `description` produces category Other, priority Standard, flag NEEDS_REVIEW, and a reason naming the missing field — it is never dropped. A row missing `complaint_id` is written with a generated positional id ROW_<n>. Any unexpected exception during a row is caught, that row is emitted as Other / NEEDS_REVIEW with the error named in the reason, and the batch continues. Before classifying, the run prints a null report (rows missing complaint_id or description) to stderr so the operator sees data quality before trusting the output."

failure_modes_observed:
  - "Taxonomy drift — the naive prompt produced 'Streetlight Outage', 'Street Light', and 'Lighting' across three rows of the same city file. Fixed by TAXONOMY LOCK plus an enum check before write."
  - "Severity blindness — the naive prompt marked PM-202402 ('School children at risk during morning hours') as Standard because the complaint was 'only a pothole'. Fixed by running SEVERITY OVERRIDE after, not before, category assignment."
  - "Missing justification — the naive prompt returned category and priority with no reason column at all. Fixed by making a citing reason a required field of every row."
  - "Hallucinated sub-categories — the naive prompt emitted 'Pothole (Major)' and 'Waste — Heritage Zone'. Fixed by character-for-character enum validation."
  - "False confidence on ambiguity — the naive prompt confidently labelled AM-202417 ('Night market waste not cleared... Heritage area affected') as Waste with no signal that Heritage Damage was equally supported. Fixed by the score-margin clause of REFUSAL ON AMBIGUITY."
  - "Proxy-signal leakage — the naive prompt raised priority for rows with high days_open and for Councillor Referral rows. Fixed by naming those columns as excluded context."

verification:
  - "Run: python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv"
  - "Check 1 — taxonomy: every category value is in the allowed 10."
  - "Check 2 — severity: PM-202402 (school children), PM-202411 (electrical hazard), PM-202420 (serious injury), PM-202446 (elderly resident fell) all return Urgent."
  - "Check 3 — reason: no reason cell is empty, and each contains a quoted term present in that row's description."
  - "Check 4 — ambiguity: rows with competing evidence carry NEEDS_REVIEW rather than a confident single label."
  - "Check 5 — row count: 15 rows in, 15 rows out."

design_note: >
  The enforcement rules above are implemented as deterministic Python, not as a live
  model call. This is deliberate: every rule here is stated as a testable condition,
  and a rule that cannot be checked on a fixed input is not an enforcement rule at all.
  It also means the classifier runs in CI with no API key, no network, and no per-run
  variance — the same input file always produces the same output file, which is what
  makes the verification checks above meaningful.