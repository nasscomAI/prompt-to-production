# skills.md

skills:
  - name: retrieve_documents
    description: Recursively loads all 3 specified policy files and structurally indexes their raw strings sequentially by document name and numeric section number.
    input: Filenames referring to the 3 mandatory policy text files.
    output: A queryable indexed representation binding source text exactly to its host document and section node.
    error_handling: System halts execution if any of the three mandatory foundational textual documents cannot be located or parsed.

  - name: answer_question
    description: Processes an employee question dynamically, searching indexed nodes deterministically. It either maps a single-source explicit answer alongside formal citation, or triggers a universal native refusal text block.
    input: Employee textual question alongside queried indexed documents.
    output: A single-source answer ending with `[Document: Section]` or the explicit deterministic Refusal string verbatim.
    error_handling: Never blends multi-document returns. Automatically resolves to the refusal template explicitly on missing scope or mathematical/policy ambivalence.
