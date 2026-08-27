skills:
  - name: retrieve_policy
    description: >
      Loads the policy .txt file and returns it as ordered numbered sections,
      each holding its numbered clauses, so that completeness can later be
      checked by clause number rather than by impression.
    input: >
      input_path -- path to data/policy-documents/policy_hr_leave.txt. Sections
      appear as "N. TITLE", clauses as "N.M text", and clause text wraps across
      several physical lines.
    output: >
      A list of section dicts, each with number, title and a list of clause
      dicts holding number and the full clause text. Wrapped lines are joined
      back together, so a clause is never handed on as half a sentence.
      Decorative rule lines and blank lines are dropped; nothing carrying
      clause text is.
    error_handling: >
      A continuation line that appears before any clause number is discarded
      rather than attached to the wrong clause, because text attributed to the
      wrong clause is worse than text that is missing. A file that yields zero
      sections is returned as zero sections rather than silently treated as an
      empty policy -- the caller's clause count check then fails loudly. An
      unreadable file raises.

  - name: summarize_policy
    description: >
      Produces the summary, compressing wording without compressing
      obligations. Every clause appears under its own number.
    input: >
      sections -- the structure returned by retrieve_policy.
    output: >
      A single string. Each section header, then every clause prefixed with its
      own number. Clauses containing binding language are reproduced verbatim
      and tagged [BINDING]; only clauses with no obligation in them are
      shortened.
    error_handling: >
      Rewording is where conditions are lost, so any clause carrying must,
      will, requires, cannot, is not permitted or an only-after restriction is
      not reworded at all. This deliberately limits how much shorter the
      summary can be. A policy in which nearly every clause is binding cannot
      be halved in length without dropping a rule, and a summary that is barely
      shorter but correct is preferred to one that is concise and permits
      something the policy forbids.

  - name: verify
    description: >
      Checks the produced summary against the source before it is written to
      disk, so a misrepresenting summary never reaches a reader.
    input: >
      sections -- the source structure. summary -- the produced text.
    output: >
      None on success. The caller writes the file only if this returns.
    error_handling: >
      Raises PolicyError listing every problem found, not just the first, so one
      run shows the full picture. Four checks run: every source clause number
      appears in the summary; every binding word present in a source clause is
      still present; no scope-bleed phrase such as "standard practice" or "in
      government organisations" has been introduced; no softener such as
      "should", "generally" or "typically" appears unless the source itself used
      it; and every figure in the source survives unrounded. On failure the
      summary is not written at all -- a partial or unverified summary on disk
      looks exactly like a verified one.
