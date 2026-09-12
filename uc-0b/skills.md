# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its content as an ordered structure of numbered sections and clauses so nothing can be silently skipped downstream.
    input: >
      path (str): filesystem path to a UTF-8 .txt policy document whose
      sections are headed "N. TITLE" and whose clauses begin with a number
      of the form N.N followed by text that may wrap onto indented
      continuation lines.
    output: >
      A dict with keys:
      title (str, the document heading lines before section 1),
      sections (list, in source order) where each section is a dict with
      number (int), heading (str), and clauses (list, in source order) of
      dicts with id (str such as "5.2"), text (str, the full clause with
      continuation lines joined by single spaces), and section (int).
      Also returns clause_count (int) equal to the total number of
      clauses parsed, used later as the completeness ground truth.
    error_handling: >
      If the file does not exist or cannot be decoded, raise a clear error
      naming the path; do not return an empty structure.
      If the file is empty or contains no lines matching the N.N clause
      pattern, raise an error stating that no numbered clauses were found.
      If a clause number appears out of sequence or is duplicated, keep
      both occurrences and mark the section with a warning so the reviewer
      sees it; never drop or merge clauses.
      Decorative divider lines (═══) and blank lines are ignored.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant plain-text summary with one entry per clause, preserving every binding verb and every condition.
    input: >
      policy (dict): the structure returned by retrieve_policy.
      verbatim_ids (list of str, optional): clause ids that must be copied
      word for word instead of summarised; defaults to ["2.5", "5.2", "7.2"].
    output: >
      A str containing the summary text ready to write to
      summary_hr_leave.txt. Layout: a title line naming the document
      reference and version, then each section heading, then one line per
      clause in source order formatted "N.N  <summary or verbatim text>",
      with verbatim clauses prefixed "[VERBATIM]". Ends with a footer
      "Clauses in source: X | Clauses in summary: Y" where X equals Y.
    error_handling: >
      If the policy dict has zero clauses, return an error string starting
      with "ERROR:" and do not produce a partial summary.
      If a clause's summary would drop any number, date, form name, role
      title, or binding verb present in the source, fall back to the
      verbatim text for that clause and prefix it [VERBATIM].
      If a clause is not in the verbatim list and no safe shortening is
      available, treat it as verbatim rather than paraphrase.
      After composing the output, re-count the clause ids present; if any
      id from the input is missing, append it verbatim under its section
      so the footer counts match, and log which ids were recovered.
      Never emit any sentence that does not map to a clause id.
