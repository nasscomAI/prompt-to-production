# skills.md — Policy Summarization Skills

skills:
  - name: retrieve_policy
    description: Parses a plain-text HR leave policy document and extracts numbered clauses with their binding verbs, conditions, and obligations as structured JSON.
    input: |
      - file_path: string (path to .txt policy document, e.g., "policy_hr_leave.txt")
      - section_filter: string, optional (e.g., "ANNUAL LEAVE", "SICK LEAVE", "LEAVE WITHOUT PAY"; if omitted, returns all sections)
    output: |
      JSON object with structure:
      {
        "document_meta": {
          "title": "EMPLOYEE LEAVE POLICY",
          "reference": "HR-POL-001",
          "version": "2.3",
          "effective_date": "1 April 2024"
        },
        "sections": [
          {
            "section_number": "2",
            "section_title": "ANNUAL LEAVE",
            "clauses": [
              {
                "clause_id": "2.3",
                "text": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
                "binding_verb": "must",
                "core_obligation": "submit leave application at least 14 calendar days in advance",
                "conditions": ["14 calendar days advance notice", "using Form HR-L1"]
              },
              {
                "clause_id": "2.4",
                "text": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
                "binding_verb": "must",
                "core_obligation": "receive written approval before leave commences",
                "conditions": ["written (not verbal)", "from direct manager", "before leave commences"]
              }
            ]
          }
        ]
      }
    error_handling: |
      - If file does not exist: return error "Policy file not found at [path]"
      - If file is not UTF-8 text: return error "File format not supported (expected .txt)"
      - If section_filter matches no sections: return error "Section not found in policy"
      - If clause structure is malformed (missing binding verb): flag clause with "AMBIGUOUS_VERB" and include raw text for manual review

  - name: summarize_policy
    description: Takes structured policy clauses and produces a condition-complete summary that preserves all binding verbs, multi-condition constraints, and clause references. Enforces the 10-clause ground truth inventory and tests output against compliance rules.
    input: |
      - structured_clauses: JSON (output from retrieve_policy skill)
      - summary_style: string, one of:
          * "condensed": 1-sentence per clause, preserving all conditions
          * "paragraph": Grouped by leave type, preserving all conditions
          * "formal": Verbatim with inline edits, preserving all conditions
      - ground_truth_clauses: array, optional (list of clause IDs that MUST appear; defaults to 10 critical clauses if omitted)
    output: |
      JSON object:
      {
        "summary_text": "string: the summarized policy",
        "compliance_audit": {
          "total_clauses_required": 10,
          "clauses_found": [
            {
              "clause_id": "2.3",
              "status": "PRESENT",
              "binding_verb_preserved": true,
              "conditions_preserved": true,
              "quote_from_summary": "...text from summary..."
            },
            {
              "clause_id": "5.2",
              "status": "PRESENT",
              "binding_verb_preserved": true,
              "conditions_preserved": true,
              "conditions_detail": ["Department Head approval", "HR Director approval"],
              "quote_from_summary": "...text from summary..."
            }
          ],
          "clauses_missing": [],
          "binding_verb_errors": [],
          "condition_drops": [],
          "scope_bleed_flags": [],
          "pass_fail": true/false,
          "summary": "Compliance report: all 10 clauses present, all conditions preserved"
        },
        "metadata": {
          "summary_style": "condensed",
          "clause_count": 10,
          "word_count": integer,
          "generated_at": "ISO timestamp"
        }
      }
    error_handling: |
      - If structured_clauses is missing a binding verb: return error "Cannot summarize clause [ID]: binding verb ambiguous in source"
      - If multi-condition clause would require dropping a condition to meet length targets: flag with "CONDITION_PRESERVATION_REQUIRED" and include verbatim text
      - If summary passes binding-verb test but fails condition test (e.g., clause 5.2 drops HR Director): return compliance_audit.pass_fail = false with details
      - If scope bleed detected (phrases like "typically", "as is standard practice"): flag in scope_bleed_flags and return pass_fail = false

