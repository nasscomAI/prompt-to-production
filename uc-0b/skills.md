# skills.md

skills:
  - name: retrieve_policy
    description: Loads and validates a policy document, extracts all numbered sections, and returns content as structured sections indexed by section number.
    input: "Path to policy .txt file"
    output: "Dictionary with keys: document_name (string), sections (dict with section_number → section_text). Example: {\"document_name\": \"policy_hr_leave.txt\", \"sections\": {\"2.3\": \"14-day advance notice required...\", \"2.4\": \"Written approval required...\"}}"
    error_handling: "If file not found, raise error with file path. If file is empty or unreadable, raise error. Count total sections and log them. Return error if section numbering is non-standard (not X.Y format)."

  - name: summarize_policy
    description: Takes structured policy sections and produces a clause-preserving summary with all numbered sections present, multi-condition requirements intact, and section references included.
    input: "Dictionary of policy sections (from retrieve_policy output); summary_type parameter (e.g., 'full', 'executive')"
    output: "Text file with summary where each numbered clause is present, all binding verbs preserved, multi-condition obligations show ALL conditions, and source section numbers cited. Example: '2.6 Carry-forward limit: max 5 days, forfeited on 31 Dec [SOURCE: 2.6]'"
    error_handling: "If input sections is missing or malformed, raise error. If any section number is absent from summary, raise error listing missing sections. Never drop conditions silently. If clause meaning cannot be preserved in summary form, quote verbatim and mark [VERBATIM SECTION X.X]."
