# skills.md — UC-0B Policy Summariser Skills

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses its content into structured, numbered sections and individual clause strings.
    input: `file_path` (str, path to policy `.txt` file, e.g., `policy_hr_leave.txt`).
    output: Dictionary mapping section titles to lists of parsed clause objects, each containing `clause_number` (str) and `text` (str).
    error_handling: If file path is invalid, unreadable, or missing required numbered sections, raises a FileNotFoundError or returns an error object detailing the parsing failure.

  - name: summarize_policy
    description: Processes structured policy sections and generates a high-fidelity summary ensuring every numbered clause is preserved with exact binding verbs and multi-approval conditions intact.
    input: Structured policy dictionary produced by `retrieve_policy`.
    output: Formatted string containing the policy summary structured by clause numbers, maintaining binding modal verbs (must, will, requires, not permitted) without scope bleed.
    error_handling: If any multi-condition clause cannot be summarized without legal precision loss, quotes the clause verbatim and appends a `[VERBATIM_FLAG]` tag. If any clause is omitted, fails validation and retries clause inventory alignment.
