# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured, numbered sections.
    input: Path to a .txt policy file.
    output: Structured map or dictionary of clause numbers to clause content.
    error_handling: Fail if the file is missing or if the content does not contain discernable clause numbers.

  - name: summarize_policy
    description: Produces a high-fidelity summary that preserves all conditions and includes every numbered clause.
    input: Structured policy sections and the enforcement rules defined in agents.md.
    output: Markdown summary with explicit clause references and flags for verbatim quotes where meaning loss was risked.
    error_handling: Refuse to process if mandatory clauses are missing or if obligations cannot be summarized without softening.
