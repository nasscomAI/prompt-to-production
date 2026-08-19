skills:
  - name: retrieve_policy
    description: Reads and parses a policy text file into structured sections and individual numbered clauses.
    input: File path to policy document (e.g., policy_hr_leave.txt).
    output: A dictionary or list of structured sections mapping section titles and numbered clause keys (e.g., 2.3, 5.2) to text content.
    error_handling: Raises FileNotFoundError if file is missing; flags unparsed or unnumbered paragraphs.

  - name: summarize_policy
    description: Generates a complete policy summary adhering strictly to all RICE enforcement rules and preserving all binding obligations.
    input: Structured policy sections dictionary produced by retrieve_policy.
    output: Plain text policy summary with explicit section headings, clause references, and exact multi-condition requirements.
    error_handling: If a clause cannot be summarized without losing critical condition details, quotes the exact clause verbatim.
