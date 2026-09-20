# agents.md — UC-0A Complaint Classifier

role: >
  Careful Python engineer building a deterministic municipal complaint
  classifier. Maps one input CSV row to a fixed taxonomy using only the
  complaint description. No external APIs, no model calls, no cross-row state.

intent: >
  Read the provided input CSV and produce output rows with exactly
  complaint_id, category, priority, reason, flag. Correct output is verifiable:
  every category is one of the 10 allowed strings, every priority is one of
  Urgent/Standard/Low, every reason is one sentence citing description words,
  and batch run over data/city-test-files/test_<city>.csv yields one output
  row per input row with the header
  complaint_id,category,priority,reason,flag.

context: >
  Allowed input: the current input row only, limited to complaint_id and
  description for decisions. Allowed values: category must be exactly one of
  Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage,
  Heat Hazard, Drain Blockage, Other; priority must be exactly one of Urgent,
  Standard, Low; Urgent triggers are exactly injury, child, school, hospital,
  ambulance, fire, hazard, fell, collapse (case-insensitive substring).
  Exclusions: do not invent categories or synonyms; do not use external APIs;
  do not read beyond the current row; do not modify any file in data/.

enforcement:
  - "1. Category must exactly match one allowed category: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — exact case; test fails on any other string."
  - "2. Priority must be Urgent whenever lowercase description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (substring, so hospitalised counts); else Low if category is Noise without a trigger; else Standard; test fails on any severity miss."
  - "3. Every output row must contain a one-sentence reason citing words from the description (format: because description contains '<matched phrase>'); test fails if reason is missing, multi-sentence, or quotes no description word."
  - "4. If the description genuinely cannot be classified confidently (no detector matches, vague text, or null), output category Other and flag NEEDS_REVIEW; flag must otherwise be NEEDS_REVIEW or blank; test fails on confident Other without flag or invented category."
  - "5. Never invent a new category: output category string must be in the 10-item list; test fails on plurals, synonyms, or casing variants."
  - "6. Empty descriptions must not crash: null/empty/whitespace description returns Other, Standard, missing-text reason, NEEDS_REVIEW; test fails on any exception."
  - "7. Batch processing must continue on malformed rows: per-row try/except degrades to Other/Standard/NEEDS_REVIEW, missing complaint_id falls back to ROW-n, and output always has full header plus one row per input; test fails if one bad row aborts the run."
  - "8. Keep the existing CLI interface from classifier.py: --input <test csv> and --output <results csv> with argparse; test fails if flags are renamed, removed, or made optional."
