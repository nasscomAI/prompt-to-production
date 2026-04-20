# skills.md

skills:
  - name: retrieve_documents
    description: Loads the HR, IT, and Finance policy files and indexes them by document name and section number for granular retrieval.
    input: List of file paths for the three mandatory policy .txt files.
    output: A collection of indexed text sections mapped to document names and section IDs.
    error_handling: Fail if any of the three required policy documents are missing or if the section headers cannot be parsed.

  - name: answer_question
    description: Searches the indexed documents for a single-source answer, returning a cited response or a mandated refusal template.
    input: A user question string and the collection of indexed policy sections.
    output: A cited answer string (with Document and Section) or the exact required refusal template.
    error_handling: Force the refusal template if the answer requires blending documents or if no direct match exists.
