# skills.md — UC-X Policy Document Q&A
# Generated from the RICE prompt and refined against app.py.

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: the three policy txt paths under ../data/policy-documents/.
    output: dict mapping document filename to {section_id: section text}.
    error_handling: A missing policy file raises a clear refusal error instead of proceeding with an incomplete index.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation or the exact refusal template.
    input: question (string) and the document index dict.
    output: string — "Source: <doc>, section <n>" plus the quoted clause text, or the refusal template.
    error_handling: Empty questions, questions with no matched concept and questions whose best matches span two documents all return the exact refusal template; information from multiple policies is never blended into one answer.