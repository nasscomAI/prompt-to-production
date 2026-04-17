# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: "retrieve_documents"
    description: "Loads and indexes HR, IT, and Finance policy documents, segmenting them by section headers and ID numbers for precise retrieval."
    input: "Paths to all 3 .txt policy files."
    output: "A searchable index of clauses including document origin and section content."
    error_handling: "Report which files could not be loaded and log the impact on reachability."

  - name: "answer_question"
    description: "Processes a natural language query against the document index to find a single-source answer with a mandatory citation."
    input: "User query (question) and the indexed policy database."
    output: "A response consisting of the answer text + citation OR the mandatory refusal template."
    error_handling: "If multiple documents contain conflicting or partial info, favor the refusal template to avoid blending."
