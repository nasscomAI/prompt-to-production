skills:
  - name: retrieve_documents
    description: >
      Loads all three policy documents from disk, parses them into an
      indexed structure keyed by document name and section number, and
      returns the structured data for downstream querying.
    input: >
      None. The skill reads from hardcoded relative paths:
      ../data/policy-documents/policy_hr_leave.txt
      ../data/policy-documents/policy_it_acceptable_use.txt
      ../data/policy-documents/policy_finance_reimbursement.txt
    output: >
      A dict (or equivalent structured object) with document names as
      top-level keys. Each document entry contains a list of sections,
      where each section has a section_number (str, e.g. "2.6") and
      body (str, full text of that section). Returned in memory.
    error_handling: >
      If a file is missing or unreadable, raise a FileNotFoundError
      with the specific missing path. Do not silently skip files. If
      section parsing fails, raise ValueError with the offending
      document name and line range.

  - name: answer_question
    description: >
      Accepts a user question, searches the pre-loaded document index
      for the single most relevant section, and returns a formatted
      answer with source citation or the verbatim refusal template.
    input: >
      question (str) — the user's natural language query.
      document_index (dict) — the output of retrieve_documents.
    output: >
      A string answer. If a match is found: the answer text followed
      by "Source: [document_name.txt], section [X.Y]". If no match
      found: the exact refusal template: "This question is not covered
      in the available policy documents (policy_hr_leave.txt,
      policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
      Please contact [relevant team] for guidance."
    error_handling: >
      If document_index is empty or None, return the refusal template.
      If the question is empty or whitespace-only, return the refusal
      template. If multiple sections match, return an answer from the
      most directly relevant section only — never blend sections from
      different documents or even different sections of the same
      document unless they are contiguous sub-sections.
