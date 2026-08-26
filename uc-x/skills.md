# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes every numbered clause by document name and section number.
    input: fixed list of the three policy .txt paths in ../data/policy-documents/.
    output: index of (document_name, section_number, clause_text) entries covering every numbered clause in all three files.
    error_handling: Any of the three files missing or containing no numbered clauses → exits at startup with the file name and problem; the CLI never starts with a partial index.

  - name: answer_question
    description: Returns a single-source cited answer or the exact refusal template for one user question.
    input: question string typed at the CLI.
    output: up to 2 clauses quoted verbatim from ONE document, each prefixed [document Sec N.N]; OR the refusal template verbatim; OR an explicit two-document ambiguity notice naming both documents without blending them.
    error_handling: Empty input → re-prompts. Question matching fewer than 2 distinct meaningful terms in every section → refusal template exactly. Equal-strength matches in two different documents → ambiguity notice, never a blended answer.
