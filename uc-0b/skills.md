# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content as structured numbered
      sections and clauses, discarding only decorative formatting.
    input: >
      path : str — path to a policy .txt file, e.g.
      ../data/policy-documents/policy_hr_leave.txt
    output: >
      dict —
        header   : list[str], the masthead lines above the first section
                   (organisation, department, title, document reference,
                   version and effective date)
        sections : list of {number: str, title: str, clauses: [...]}
        clauses  : list of {ref: str ("5.2"), text: str} where text has its
                   line-wrap whitespace collapsed to single spaces and is
                   otherwise character-identical to the source
      Multi-line clauses are rejoined. Banner rules (═) are dropped as
      decoration. Nothing else is discarded.
    error_handling: >
      A missing or unreadable file exits non-zero with the path in the message.
      A file that parses to zero numbered clauses is refused outright rather
      than summarised as free prose — an unstructured document cannot have its
      clause completeness verified, so the system declines the job. A clause
      line that appears before any section header is attached to a synthetic
      section 0 rather than dropped, so no text is lost to a malformed header.

  - name: summarize_policy
    description: >
      Takes the structured sections and produces the compliance summary, with
      clause references, obligation and multi-condition indexes, and a coverage
      report — then audits its own output before returning it.
    input: >
      policy : dict — the structure returned by retrieve_policy
      mode   : str — "enforced" (default) or "naive". The naive mode is the
               Control step: it reproduces what an unconstrained summariser
               does, so the failure can be measured rather than assumed.
    output: >
      str — the full summary text, and in enforced mode a companion audit dict
      with clauses_total, clauses_present, verbatim_count, condensed_count,
      multi_condition refs, and the critical-clause coverage list.
    error_handling: >
      In enforced mode the function audits itself before returning: it asserts
      every source clause reference appears in the output, that every clause
      marked VERBATIM has its exact normalised source text present, and that no
      banned scope-bleed phrase occurs anywhere. Any failure raises with the
      offending clause reference or phrase named, and the caller writes no
      output file — a summary that fails its own audit must not reach disk,
      because a bad summary that exists is more dangerous than none. In naive
      mode the audit is deliberately not run; that is the whole point of the
      control, and its clause loss is reported instead.
