# skills.md — UC-X Skills Specification

skills:
  - name: retrieve_documents
    description: Loads all 3 policy text documents (HR, IT, Finance) and parses them into an indexed corpus keyed by document name, section number, and clause text.
    input: List or paths of policy files.
    output: Indexed dictionary mapping document identifiers and section/clause numbers to their verbatim obligations and keywords.
    error_handling: Raises FileNotFoundError if any of the three policy files are missing.

  - name: answer_question
    description: Analyzes user query against the indexed documents, isolates the single relevant policy domain, verifies direct textual coverage, and outputs either a single-source cited answer or the exact refusal template.
    input: User question string.
    output: String containing single-source factual answer with document citation and section numbers, OR exact refusal template.
    error_handling: Prevents cross-document blending; outputs verbatim refusal template whenever coverage is ambiguous, speculative, or absent.
