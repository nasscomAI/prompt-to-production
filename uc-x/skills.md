skills:
  - name: retrieve_documents
    description: Loads all three policy files and returns them as a dict indexed by document filename and reference code, with section structure preserved.
    input: data_dir (str) — path to the directory containing the three policy .txt files.
    output: dict with keys "policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt" — each value is the full file text as a string.
    error_handling: Raises FileNotFoundError with the missing filename if any of the three files is absent. All three files are required — the system does not operate with partial document sets.

  - name: answer_question
    description: Takes a user question and the loaded policy documents, queries the LLM with a strict single-source citation system prompt, and returns either a cited answer or the exact refusal template.
    input: question (str), documents (dict from retrieve_documents), client (OpenAI) — initialised API client.
    output: str — either a cited answer referencing one document + section per claim, or the exact refusal template string if the question is not in the documents.
    error_handling: If the API call fails, raises the underlying OpenAI exception. Never falls back to a hallucinated answer on API error. The refusal template is the only permissible response for out-of-scope questions.
