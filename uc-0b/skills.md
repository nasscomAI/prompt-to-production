# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Ingests a raw policy text file and parses its contents into structured sections, headings, and distinct numbered clauses.
    input: file_path (str, path to the input .txt policy document).
    output: Structured representation containing metadata (document reference, version) and a list of section objects with numbered clause texts.
    error_handling: Raises descriptive FileNotFoundError if the path is invalid; gracefully captures unformatted introductory lines and preserves all clause texts without truncation.

  - name: summarize_policy
    description: Transforms structured policy clauses into an accurate, complete summary adhering to zero clause omission, preserved binding obligations, and strict approver requirements.
    input: Structured policy sections or raw text from retrieve_policy.
    output: Plain-text formatted summary covering all numbered clauses (1.1 through 8.2) with strict binding terms and clause citations.
    error_handling: If a clause cannot be compressed without risking obligation softening or condition loss, quotes the clause verbatim with a preservation notice.
