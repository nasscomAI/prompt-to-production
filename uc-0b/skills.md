# UC-0B skills

skills:
  - name: retrieve_policy
    description: Load one policy text file and return its numbered clauses as structured records.
    input: Path to a UTF-8 plain-text policy.
    output: Ordered records containing clause number and exact clause text.
    error_handling: Reject a missing or empty file; do not substitute another policy.

  - name: summarize_policy
    description: Produce a clause-referenced summary without dropping conditions or adding unsupported claims.
    input: Structured policy clauses and an ordered list of required clause numbers.
    output: UTF-8 summary text containing every required clause and its source reference.
    error_handling: Stop with a clear error if a required clause is absent; never silently omit it.
