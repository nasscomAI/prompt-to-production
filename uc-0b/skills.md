# skills.md

skills:
  - name: summarize_policy
    description: Create a concise summary of HR leave policy that preserves all clauses, obligations, and conditions without changing meaning.
    input: Path to input policy text file (string); output path string for summary file.
    output: Text file written to output path containing summary with all 10 inventory clauses included, multi-conditions preserved, no added information.
    
    constraints:
      clause_presence: "Every numbered clause must be present in the summary."
      multi_condition_preservation: "Multi-condition obligations must preserve ALL conditions — never drop one silently."
      no_information_addition: "Never add information not present in the source document."
      binding_verbs: ["must", "requires", "will", "may", "are forfeited", "not permitted"]
      scope_preservation: "Maintain exact scope limitations (e.g., 'during service', 'under any circumstances')."
    
    error_handling: 
      - "If summary cannot preserve all clauses without omission: output with [CLAUSE_OMISSION_WARNING] flag."
      - "If multi-condition cannot be preserved: flag [CONDITION_DROP_WARNING]."
      - "If obligation softened: flag [OBLIGATION_SOFTENING_WARNING]."
      - "File I/O errors: raise exception with context."
      - "Empty input: output empty summary with [EMPTY_INPUT_WARNING]."
