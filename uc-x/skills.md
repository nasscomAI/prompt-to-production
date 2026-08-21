# skills.md — UC-X

skills:
  - name: retrieve_documents
    description: Loads all 3 policy txt files into memory, indexing them cleanly by document filename and structured section numbers.
    input: List of file paths to the 3 policy documents.
    output: A queryable indexed JSON/Dictionary of the documents separated strictly by section borders to prevent bleed.
    error_handling: System exits if any file is missing to prevent hallucinating blank rules.

  - name: answer_question
    description: Executes a precise search query over the indexed documents and generates an exact-cited response or falls back to the exact refusal template.
    input: The user's query block and the indexed document structure.
    output: String response satisfying all enforcement restrictions.
    error_handling: Emits the exact verbatim refusal template (as specified in agents.md) if ambiguity arises or if the logic demands synthesizing multiple disjoint sources.
