# skills.md

skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and converts it into a clause-indexed structure for faithful clause-by-clause summarization.
    input: A filesystem path string pointing to a plain-text policy document, expected here to be ../data/policy-documents/policy_hr_leave.txt.
    output: A structured object with section headings and numbered clauses, where each clause includes clause_id, section_title, source_text, and any continuation lines merged into the original clause text.
    error_handling: Returns a blocking error if the file is missing, unreadable, not a .txt file, contains unnumbered policy content that cannot be attached to a clause, or cannot be parsed into stable numbered sections without ambiguity.

  - name: summarize_policy
    description: Converts structured policy clauses into a summary_hr_leave.txt-style plain-text summary with clause references, full clause coverage, and no meaning drift.
    input: The structured clause object returned by retrieve_policy, including every numbered clause's clause_id, section_title, and source_text.
    output: Plain text ordered by clause number where each line contains the clause reference and a meaning-preserving summary; if a clause cannot be safely compressed, the output includes the clause reference, the verbatim source text, and a visible flag such as QUOTED_VERBATIM.
    error_handling: Refuses to summarize if any numbered clause would be omitted, if any condition or approver would be dropped, if scope-bleed language not present in the source would be introduced, or if the input clause structure is incomplete; in those cases it reports the affected clause_ids instead of guessing.
