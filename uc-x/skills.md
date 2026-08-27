skills:
  - name: [retrieve_documents]
    description: [Loads all 3 policy files and indexes them by document name and section number. ]
    input: [type: array format: List of file paths to the policy documents. ]
    output: [type: object format: Indexed mapping of document names and section numbers to their text contents. ]
    error_handling: [If any required policy document is missing or unreadable, halt execution rather than running with incomplete data.]

  - name: [answer_question]
    description: [Searches indexed documents to return a single-source answer with an exact citation or the required refusal template.]
    input: [type: string format: The user's policy question in natural language. ]
    output: [type: string format: A factual answer citing the exact source document name and section number, or the exact refusal template.]
    error_handling: [If answering requires cross-document blending, drops required conditions, or invites hedged hallucination, immediately output the exact refusal template with no variations.]
