# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Reads the input policy text file (.txt) and extracts all numbered policy clauses (1.1 through 8.2) into a structured section map.
    input: File path input_path (str) to policy text file.
    output: Dictionary mapping section/clause numbers (e.g. "2.3", "5.2") to section title and full text content.
    error_handling: Handles missing policy file gracefully by writing an error header to the output destination without crashing.

  - name: summarize_policy
    description: Processes structured policy sections and generates a comprehensive summary preserving all numbered clauses, binding verbs (must, will, requires, not permitted), multi-condition approvals, and exact scope.
    input: Dict of sections from retrieve_policy.
    output: Formatted string containing complete section-by-section summary.
    error_handling: Verifies presence of all 10 ground-truth key clauses. Quotes complex multi-condition clauses verbatim to prevent obligation softening or condition loss.