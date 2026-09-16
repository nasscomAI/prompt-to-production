skills:
  - name: retrieve_documents
    description: Loads the three approved policy documents and indexes them by document filename and section number.
    input: "No user document input; files are resolved relative to app.py from ../data/policy-documents."
    output: "Dictionary keyed by filename with section-number dictionaries containing clause text."
    error_handling: "Raises clear errors for missing files, unreadable text, empty policies, null content, or failure to parse numbered sections."
  - name: answer_question
    description: Answers a policy question from exactly one indexed document with citation or returns the exact refusal template.
    input: "Question string plus indexed documents."
    output: "Plain-text answer with source filename and section number, or the exact unsupported-question refusal."
    error_handling: "Refuses blank, ambiguous, unsupported, multi-document, or hallucination-prone questions; never blends documents or uses hedged wording."
