skills:
  - name: retrieve_documents
    description: Systematically loads all 3 defined policy files and indexes them strictly by document name and section number to prevent blending.
    input: Automated loading of the three designated `.txt` files directly from the local `/data/` target directory.
    output: A query-able structured index cataloging and segmenting the raw text mapped accurately to its section numbers and host document properties.
    error_handling: Fail sequentially and exit if the required files cannot be found or their formatting prevents indexed chunking.

  - name: answer_question
    description: Matches formatted employee-sourced questions strictly isolated against the generated index array resolving exclusively to single citations.
    input: Question string triggered explicitly via the interactive terminal prompt.
    output: Either a structured response extracting verbatim rules tagged with `[CITATION: file:section]`, or exactly emitting the designated Refusal string.
    error_handling: Routes forcefully directly pointing to the 'Refusal' template specifically if questions present indexing ambiguities, zero exact hits, or trigger unidentifiable document blending criteria.
