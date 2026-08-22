# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its content as structured numbered sections.
    input: one string — path to a .txt policy file (e.g. ../data/policy-documents/policy_hr_leave.txt), as passed via --input CLI argument.
    output: dict mapping clause IDs to text — {section_number: str, clause_id: str (e.g. "2.3"), text: str} per numbered clause, preserving original wording exactly; also returns the document header/metadata block.
    error_handling: Missing or unreadable file → exit early with a clear error message and produce no output file. Lines without clause numbering are attached to the current section as header/context, never silently discarded.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references.
    input: dict from retrieve_policy — structured clauses keyed by clause ID.
    output: None returned — writes summary_hr_leave.txt containing one entry per clause in source order, each starting with its clause number; obligations stated with the source's binding verb and every condition preserved.
    error_handling: A clause that cannot be compressed without meaning loss → quoted verbatim and marked [QUOTE-VERBATIM] instead of paraphrased. An expected critical clause missing from retrieve_policy's output → flagged [MISSING CLAUSE] rather than skipped. No clause is ever dropped or merged.
