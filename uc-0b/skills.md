# skills.md

skills:
  - name: retrieve_policy
    description: Load the .txt policy file and return content as structured numbered sections.
    input: file_path (str, path to policy_hr_leave.txt).
    output: dict mapping section number (e.g. "2.3") to its raw text line(s).
    error_handling: If a line does not match the "N.N " numbered-clause pattern, it is attached to the previous clause number as a continuation line (multi-line clauses) rather than dropped or raising.

  - name: summarize_policy
    description: Take structured sections and produce a compliant clause-by-clause summary with clause references, preserving every condition and flagging any clause that cannot be paraphrased without meaning loss.
    input: dict of {clause_number: raw_text} from retrieve_policy.
    output: str — the summary text, one line per clause, prefixed with the clause number; a trailing COMPLIANCE CHECK block listing all 10 ground-truth clause numbers and PRESENT/MISSING.
    error_handling: If a required ground-truth clause number is absent from the input dict (source document changed/truncated), it is reported as MISSING in the COMPLIANCE CHECK rather than silently omitted from the summary.
