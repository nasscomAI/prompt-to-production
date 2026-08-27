
## skills.md
 
skills:
- name: retrieve_policy
  description: >
    Loads the HR leave policy text file and transforms it into
    a structured representation with preserved numbering.
  input: >
    Path or identifier of a .txt HR policy document.
  output: >
    Structured policy object with section numbers, clause numbers,
    and original clause text preserved verbatim.
  error_handling: >
    If the document is missing, unreadable, or unstructured,
    return an error and do not infer or reconstruct content.
 
- name: summarize_policy
  description: >
    Generates a compliant policy summary that preserves all obligations
    without semantic loss and includes clause references.
  input: >
    Structured policy sections produced by retrieve_policy.
  output: >
    A summarized document where:
    - Every required clause is present
    - Each summary point references its clause number
    - Non-compressible clauses are quoted verbatim and flagged
  error_handling: >
    If any required clause is missing, if a multi-condition obligation
    cannot be preserved, or if meaning would change through summarization,
    the function must fail explicitly and explain why.
 