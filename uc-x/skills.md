# skills.md

skills:
  - name: retrieve_documents
    description: Load the three policy documents, parse them into numbered sections, and return a searchable index keyed by document filename and section number.
    input: A list of file paths (strings) pointing to the three policy documents: `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, `policy_finance_reimbursement.txt`.
    output: A dict-like index with structure: `{ "policy_filename": {"section_number": "section text", ... }, ... }` and a small metadata object listing section titles when available.
    error_handling: If a file is missing or unreadable, return an error entry for that filename and do NOT attempt to synthesize content; surface the missing-file error so callers can use the refusal template.

  - name: answer_question
    description: Search the indexed documents for the best single-source answer to a user question; return either a single-source factual answer with an exact citation or the refusal template (verbatim) when the documents do not contain an authoritative answer.
    input: {
      "question": string,
      "index": the dict returned by `retrieve_documents`,
      "refusal_template": the exact refusal string to use when refusing (see `uc-x/agents.md`).
    }
    output: {
      "answer_text": string,         # The one-paragraph factual answer OR the refusal template verbatim
      "citation": {                 # Machine-readable citation used for the answer
          "document": "policy_filename",
          "section": "section_number"  # If multiple sections from same doc used, list as array
      }
    }
    error_handling: |
      - If the best answer can be found entirely in a single section of one document, return that answer_text and citation.
      - If the question requires combining facts from more than one document and that combination would change meaning, return the refusal template verbatim.
      - Do not use hedging phrases; if confidence < threshold or no clear section matches, return the refusal template verbatim.
      - Always include a machine-readable citation referencing exactly one document and the section number(s) used.

Notes:
- The `refusal_template` must be used verbatim when refusing; see `uc-x/agents.md` for the exact string.
- Every factual claim in `answer_text` must be directly supported by the cited section; do not infer unstated permissions or combine multiple documents.
- Agents consuming these skills must enforce the README test-suite (7 test questions and the critical cross-document test).
