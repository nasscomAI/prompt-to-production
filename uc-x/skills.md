# Document Q&A Skills

- `retrieve_documents() -> dict`: Loads and segments the provided policy files (`policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, `policy_finance_reimbursement.txt`) into section-indexed content for precise retrieval.
- `answer_question(query: str, indexed_docs: dict) -> str`: Analyzes the query, identifies the single most relevant source, and provides an answer citing the document and section number. It returns the refusal template if the answer is multiple-sourced or not in the documents.
