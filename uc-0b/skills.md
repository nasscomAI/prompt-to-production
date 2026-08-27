skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into a structured list of numbered sections and clauses, preserving the exact text of each clause.
    input: file_path (str) — absolute or relative path to a .txt policy document.
    output: A list of dicts, each with keys — section_num (str, e.g. "2.3"), section_title (str, parent section heading), clause_text (str, verbatim clause content).
    error_handling: If the file does not exist, raise FileNotFoundError with the path. If the file is empty or contains no numbered clauses, raise ValueError with a descriptive message. Never return partial results silently.

  - name: summarize_policy
    description: Takes the structured clause list from retrieve_policy and produces a clause-faithful, obligation-preserving summary as formatted text, with every clause present and flagged where verbatim quoting was required.
    input: clauses (list of dicts from retrieve_policy) — structured representation of the policy document.
    output: A formatted string containing the full summary, organised by section, with clause references (e.g. [2.3]), binding verbs preserved, and [VERBATIM – condition-sensitive] tags where applicable.
    error_handling: If the clauses list is empty, return a summary stating 'No clauses found to summarise' with a NEEDS_REVIEW flag. If a clause text is missing or empty, include the clause number in the output with the note 'Clause text unavailable — manual review required'.
