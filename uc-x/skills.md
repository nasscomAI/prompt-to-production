# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy .txt files and indexes every clause by document name and section number.
    input: list of policy file names (strings) located under data/policy-documents/.
    output: index of clauses, each with doc (file name), section (number string), text (clause text).
    error_handling: Missing file raises a clear error naming the document.

  - name: answer_question
    description: Searches the index for the best single-source match and returns a cited answer or the refusal template.
    input: question (string).
    output: answer text — either "Source: <doc> section <n>: <clause text>" (single document only) or the refusal template verbatim.
    error_handling: No match above threshold returns the refusal template; multi-document ambiguity returns the single best source only, never a blend.
