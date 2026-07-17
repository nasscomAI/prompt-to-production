# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy .txt files and indexes them by document name and section/clause number.
    input: list of policy file paths (strings).
    output: an index of entries, each with document_name, section_id (X.Y), section_title, and clause_text.
    error_handling: Raises a clear error if any file is missing or empty; unparseable lines are attached to the current clause so no text is lost.

  - name: answer_question
    description: Finds the single best-matching clause for a question and returns a cited single-source answer, or the refusal template.
    input: a natural-language question (string) and the document index.
    output: either an answer string with a "Source: <document>, section <id>" citation, or the exact refusal template.
    error_handling: Returns the refusal template when the best match is below the relevance threshold or when top matches span more than one document within a close margin (cross-document ambiguity). Never blends documents and never emits hedging language.
