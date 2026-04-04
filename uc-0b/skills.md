# skills.md — UC-0B Legal / Policy Summarizer

skills:
  - name: retrieve_policy
    description: Opens and parses the text policy file, returning it structured by numbered clauses.
    input: 
      - filepath (str): Path to the `.txt` policy document.
    output: 
      - dictionary: Mapping of clause numbers (e.g. "2.3") to their raw string text.
    error_handling: 
      If the file cannot be found or read, raises a clear FileNotFoundError. If parsing fails to identify sections, falls back to returning the whole document as a single "1.0" clause.

  - name: summarize_policy
    description: 
      Takes a structured dictionary of policy clauses and condenses them into a compliant summary 
      that strictly preserves binding verbs and multi-approval conditions.
    input: 
      - sections (dict): Dictionary mapping string clause numbers to string clause content.
    output: 
      - string: A properly formatted markdown document summarizing the policy, clause by clause.
    error_handling: 
      If a clause is empty, it skips it. If it predicts that meaning might be lost on complex phrasing, it retains the raw phrase and tags it with [NEEDS_REVIEW].
