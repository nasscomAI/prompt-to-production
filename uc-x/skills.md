# Policy Q&A Skills

- `retrieve_documents`
  - Input: list of policy file paths.
  - Output: loaded text content indexed by document name and section number.
- `answer_question`
  - Input: user question, indexed documents.
  - Output: single-source answer with citation, OR exact refusal template.
