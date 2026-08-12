# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns it as an ordered structure of
      numbered sections and numbered clauses, preserving source order and the
      exact wording of every clause.
    input: >
      path (str) — path to a policy .txt file such as
      data/policy-documents/policy_hr_leave.txt. The file is expected to use
      'N. SECTION HEADING' lines for sections and 'N.N clause text' lines for
      clauses, with continuation lines indented beneath their clause.
    output: >
      A dict with keys: title (str, the document header lines), sections
      (ordered list of {number, heading, clauses}), and clauses (flat ordered
      list of {number, section, text}), where text is the clause rewrapped to a
      single line with the source wording byte-identical apart from collapsed
      internal whitespace. Also returns clause_count (int) for the completeness
      check.
    error_handling: >
      Missing or unreadable file: exits with the offending path named, before
      any output file is written.
      File contains zero clauses matching the N.N pattern: exits rather than
      returning an empty structure, because an empty parse would otherwise
      render an empty summary that passes a naive completeness check trivially.
      Continuation line appearing before any clause number: attached to the
      document title block rather than silently discarded.
      Duplicate clause numbers in the source: both retained and reported, since
      dropping a duplicate would understate the clause count and hide a defect
      in the source document.
      A clause whose text is empty after parsing: retained with an explicit
      "(no text parsed)" marker so the gap is visible in the audit rather than
      absent from the summary.

  - name: summarize_policy
    description: >
      Takes the structured sections from retrieve_policy and produces a
      clause-complete compliance summary, compressing a clause only when every
      material token survives and quoting it verbatim when they do not.
    input: >
      The dict returned by retrieve_policy, plus mode (str) — "enforced"
      applies the agents.md rules; "naive" reproduces the unguarded
      first-sentence-per-section approach so the failure modes can be observed
      and compared.
    output: >
      A tuple of (summary_text, audit). summary_text is the full report written
      to summary_hr_leave.txt: an AT A GLANCE block of the critical
      obligations, a FULL CLAUSE INVENTORY covering every numbered clause with
      each line tagged [compressed] or [VERBATIM], and a FIDELITY AUDIT block.
      audit is a dict with clause counts, missing clause numbers, dropped
      material tokens per clause, banned phrases found, softened binding verbs,
      and an overall passed flag.
    error_handling: >
      Clause omission failure mode: the audit compares the set of clause
      numbers in the source against the set rendered; any difference is listed
      by number and fails the run rather than being absorbed silently.
      Condition drop failure mode: if a compressed line loses any digit group,
      acronym, capitalised role, or form number present in the source clause,
      the compression is discarded and the clause is re-emitted verbatim and
      tagged. The skill self-corrects rather than reporting a defect it could
      have prevented.
      Scope bleed failure mode: every alphabetic word in the summary body is
      checked against the source vocabulary plus a fixed declared list of
      renderer structural words; any word outside both is reported as bleed.
      Banned hedge phrases are additionally checked by exact substring match.
      Obligation softening failure mode: binding verbs present in a source
      clause are required to be present in that clause's summary line; a
      missing binding verb fails the run.
      Any failing check: written into the FIDELITY AUDIT section of the output
      file AND signalled by a non-zero exit code, so a defective summary can
      never be mistaken for a clean one by a caller that only checks status.
