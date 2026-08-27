# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Automatically ingests all three targeted policy text files simultaneously and isolates the text rigidly by dynamically indexing document string names alongside exact section numbers.
    input: Implicit configuration bounds defining the exact filesystem path vectors exclusively for the three policy `.txt` files.
    output: A meticulously indexed internal data structure securely isolating all text within discrete boundaries bound strictly to their origin document names and explicitly parsed subsection numerics.
    error_handling: Halts cleanly tracking corrupt paragraphs rather than collapsing malformed clauses, ensuring isolation lines are not accidentally blurred across files.

  - name: answer_question
    description: Queries the strictly indexed knowledge base to output factual responses strictly limited to a solitary quoted source clause constraint or defaults gracefully to a hard refusal template.
    input: The user's queried string question alongside the tightly bound structure from retrieve_documents.
    output: A single-source string answer rigidly carrying the precise `Document Name + Section Number` citation or the verbatim refusal template.
    error_handling: Immediately defaults to outputting the strict "This question is not covered in the available policy documents..." fallback template if it fails to isolate a discrete, single-source section hit without hedging.
