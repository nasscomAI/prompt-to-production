skills:

  - name: retrieve_policy
    description: >
      Loads a raw policy text file (.txt) and parses it into structured sections
      and individual numbered clauses with metadata.
    input: >
      A string filepath to a policy document (e.g. data/policy-documents/policy_hr_leave.txt).
    output: >
      A structured dictionary containing document metadata (title, reference, version, effective date)
      and a list of sections, each with section title and numbered clause objects (clause_id, text).
    error_handling: >
      If file is missing or unreadable, raises FileNotFoundError with a descriptive error.
      If file is empty, raises ValueError indicating empty input.
      If structure deviates from standard section headers, gracefully falls back to line-based clause parsing.

  - name: summarize_policy
    description: >
      Generates a compliant, structured summary from parsed policy sections, ensuring
      complete clause coverage, preservation of multi-condition approvers, exact thresholds,
      and zero obligation softening.
    input: >
      A structured policy dictionary as returned by retrieve_policy.
    output: >
      A formatted plain text summary with document header, numbered sections, and
      every single numbered clause summarized with strict obligation fidelity.
    error_handling: >
      Validates that all numbered clauses in input are represented in the output.
      If any clause has complex conditions that risk alteration upon condensing,
      the skill quotes the clause verbatim to ensure zero meaning loss.
