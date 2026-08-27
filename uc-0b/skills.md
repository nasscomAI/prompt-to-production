# skills.md — UC-0B Summary That Changes Meaning

# Implements: agents.md · core failure modes: clause omission, scope bleed, obligation softening

skills:
  - name: retrieve_policy
    description: >
      Loads a single UTF-8 policy .txt file (HR leave policy path per agents.md io_contract), parses it
      into structured numbered sections so summarization can trace obligations back to clause ids, and
      exposes the full source text for audit—no external corpora.
    input: >
      Filesystem path to one policy file (default or specified: policy_hr_leave.txt). Optional encoding
      hint; UTF-8 is required per typical CMC documents.
    output: >
      A structured object: raw_text (full string), and sections as a list of records each with at
      least clause_id or heading line (e.g. lines matching “2.3”, “5.2”, section headers), plus body
      fragments so agents.md clause_inventory ids (2.3 through 7.2) can be mapped to source spans.
    error_handling: >
      If the path is missing, not a file, or not readable UTF-8, fail fast with a clear error. If the
      file is empty, return empty sections and signal error. Do not fabricate missing clauses.
      Parsing must preserve line breaks where needed so multi-sentence obligations (e.g. 5.2 two
      approvers) are not split across logic incorrectly.

  - name: summarize_policy
    description: >
      Takes structured sections (from retrieve_policy) and produces a single compliant summary suitable
      for summary_hr_leave.txt: every agents.md clause_inventory entry is covered with clause id or
      equivalent traceability, binding verbs preserved, no scope bleed, and verbatim QUOTE where
      paraphrase would lose meaning.
    input: >
      Structured sections + optional checklist derived from clause_inventory (ids 2.3, 2.4, 2.5, 2.6,
      2.7, 3.2, 3.4, 5.2, 5.3, 7.2). May include LLM or template pipeline config; must not receive
      withheld text from other policies.
    output: >
      Final summary text (plain UTF-8) written to uc-0b/summary_hr_leave.txt per io_contract, with
      explicit or implied references to each clause id where required, and flags/markers for verbatim
      quotes when used. Output must be reviewable against clause_inventory in agents.md.
    error_handling: >
      If required sections cannot be found in source, do not invent—surface gaps (e.g. “clause 5.2 not
      found in parse”) or refuse to finalize until retrieve_policy is fixed. If summarization would drop
      a multi-condition rule (especially 5.2 Department Head AND HR Director), fail the compliance check
      or emit QUOTE of source per agents.md enforcement. Reject additions of generic boilerplate not in
      source (scope bleed).

alignment:
  agent_spec: "agents.md"
  enforcement: >
    summarize_policy MUST satisfy every agents.md enforcement bullet: all 10 clauses represented;
    multi-condition rules intact; no extrinsic facts; quote + flag when summarization risks meaning loss.
    retrieve_policy MUST delegate only to the specified policy file contents—no other documents.
