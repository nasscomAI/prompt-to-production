skills:
  - name: retrieve_documents
    description: Loads the three allowed policy files and indexes their numbered clauses by document name and section.
    input: The repository policy-document directory containing the three required UTF-8 .txt files.
    output: A mapping from document filename to ordered section records containing section number and source text.
    error_handling: Fails clearly if a required file is missing, unreadable, empty, or has no numbered sections; never substitutes outside information.
  - name: answer_question
    description: Answers a question from one matching policy document with complete conditions and source citations, or refuses exactly.
    input: A non-empty staff question and the indexed policy documents.
    output: A plain-text answer citing filename and section number for every factual claim, or the exact refusal template.
    error_handling: Refuses unsupported, ambiguous, or cross-document questions using the exact template; never hedges or blends sources.
