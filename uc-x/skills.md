skills:
  - name: retrieve_documents
    description: "loads all 3 policy files, indexes by document name and section number"
    input: "paths to the 3 policy .txt files"
    output: "structured text indexed strictly by document name and section number"
    error_handling: "If a file is unreadable, report the failure and safely continue without it."

  - name: answer_question
    description: "searches indexed documents, returns single-source answer + citation OR refusal template"
    input: "the indexed document text and the raw interactive user query"
    output: "a highly constrained string containing either a single-source explicitly cited factual answer or the strict refusal template"
    error_handling: "If the question requires pulling facts from more than one policy file, safely refuse and use the exact refusal template without hallucinating."
