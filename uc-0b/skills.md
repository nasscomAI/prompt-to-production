# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Load the HR leave policy text file and parse it into structured numbered sections
    input: file_path (str — path to policy_hr_leave.txt)
    output: dict with keys: sections (dict mapping clause_number -> clause_text), full_text (str)
    error_handling: If file not found, raise FileNotFoundError. If file is empty, raise ValueError. If clause numbering is malformed, log warning but continue with best-effort parsing.

  - name: summarize_policy
    description: Generate a compliant summary from structured policy sections preserving all 10 clause inventory items
    input: sections (dict mapping clause_number -> clause_text), clause_inventory (list of clause numbers to include)
    output: summary_text (str — formatted summary with clause citations)
    error_handling: If any clause from clause_inventory is missing from sections, include a note: "[CLAUSE X.Y NOT FOUND IN SOURCE]". If summary generation fails, raise RuntimeError with details.