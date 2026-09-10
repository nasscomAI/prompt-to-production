# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy .txt files and indexes every numbered clause by document name and section number.
    input: policy_dir (str), the directory containing the 3 policy .txt files.
    output: list of {doc (str filename), clause (str "N.N"), text (str)} entries, one per clause across all 3 documents.
    error_handling: Raises IOError if any of the 3 expected files is missing; raises ValueError if zero clauses are indexed in total (format check), so a broken index never silently answers with nothing.

  - name: answer_question
    description: Scores every indexed clause against the question's keywords and returns either the single best-matching clause (with citation) or the refusal template.
    input: question (str), the index from retrieve_documents, the precomputed term-rarity weights.
    output: str — either "<clause text>\n(Source: <doc>, section <clause>)" for exactly one clause, or the exact refusal template.
    error_handling: An empty/whitespace-only question returns the refusal template immediately rather than matching against everything; if the top match's score is at or below the minimum relevance threshold, refuses rather than guessing a weak match.
