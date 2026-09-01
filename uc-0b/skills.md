# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads policy_hr_leave.txt and returns content as structured numbered sections with clause IDs and verbatim text.
    input: Path to policy_hr_leave.txt (UTF-8 text file).
    output: Ordered dict mapping clause_id (e.g., "2.3") to dict {section: "2. ANNUAL LEAVE", text: "Employees must submit..."} plus header metadata.
    error_handling: If file missing or unreadable → raise FileNotFoundError with path; if no clauses matched → raise ValueError "No numbered clauses found"; preserves original whitespace for verbatim fallback.

  - name: summarize_policy
    description: Takes structured sections and produces compliant summary with clause references, preserving every numbered clause and all binding conditions.
    input: Ordered dict from retrieve_policy.
    output: String summary where each line starts with "Clause X.Y:" followed by obligation preserving binding verbs (must/requires/will/not permitted/may/are forfeited) and all conditions.
    error_handling: If a clause cannot be shortened without dropping a condition (e.g., 5.2 both approvers, 2.4 written+verbal) → outputs verbatim text flagged [VERBATIM]; never invents conditions; never omits a clause.
