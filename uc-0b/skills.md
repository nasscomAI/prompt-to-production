# skills.md

skills:
  - name: clause_extraction
    description: Extract specified clause from policy text using clause ID and return its full obligation text.
    input: "Policy text (string), Clause ID (e.g. '2.3', '5.2'), and binding verb marker to locate (e.g. 'must', 'requires')"
    output: "Extracted clause text (string) or NOT_FOUND if clause ID not in policy; includes binding verb and all conditions"
    error_handling: "If clause ID cannot be found, return error code NOT_FOUND with the clause ID and section reference"

  - name: multi_condition_validator
    description: Verify that multi-condition obligations (joined by AND) preserve all conditions; specifically checks clause 5.2 for dual approval.
    input: "Clause ID (string), extracted clause text (string), expected conditions (list of strings)"
    output: "PASS (all conditions present) or FAIL with list of missing conditions; if any condition is dropped, raise MULTI_CONDITION_VIOLATION"
    error_handling: "If a condition is missing or weakened (e.g. 'approval' instead of 'Department Head AND HR Director approval'), return FAIL with specific violation"

  - name: binding_verb_preservation
    description: Check that original binding verb is preserved and not substituted with weaker alternative (e.g. 'must' not changed to 'should').
    input: "Clause ID (string), source binding verb (string), summary binding verb (string)"
    output: "PASS or FAIL; if FAIL, return the substitution (e.g. 'must' → 'should') as violation"
    error_handling: "Flag any softening as BINDING_VERB_VIOLATION; reject substitutions like must→should, will→may"

  - name: clause_completeness_check
    description: Verify that all 10 critical clauses are present in the summary; count them and report any missing.
    input: "Summary text (string), clause ID list (list of 10 strings: ['2.3', '2.4', ..., '7.2'])"
    output: "Integer count of clauses found (0–10), list of missing clause IDs (empty list if all found)"
    error_handling: "If count < 10, return INCOMPLETE with missing clause IDs; this is a CRITICAL FAILURE condition"

  - name: validation_report_generator
    description: Generate a structured validation report showing clause count, binding verb checks, multi-condition preservation, and overall summary status.
    input: "Summary text (string), clause extraction results (dict), validation results (dict of pass/fail for each clause)"
    output: "Report (string) showing: Total Expected (10), Total Found (count), Missing (IDs), Violations (list), Overall Status (PASS/FAIL)"
    error_handling: "If any violation detected, mark overall status as FAIL and list all violations; do not mask or downgrade errors"
