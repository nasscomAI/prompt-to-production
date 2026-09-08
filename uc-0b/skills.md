# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt HR policy file from disk and parses it into structured, numbered sections — section number/title, then each clause's number and full text — so summarization always has clause boundaries to anchor to instead of working from raw, unstructured text.
    input: A file path to a plain-text (.txt) policy document formatted with "N. SECTION TITLE" headers and "N.N clause text" clauses, where clause text may wrap across multiple indented lines.
    output: A structured document — {metadata (header lines before the first section), sections: [{number, title, clauses: [{number, text}]}]}. Clause text has line-wrapping collapsed into a single normalized string but is otherwise unmodified from the source (no paraphrasing at this stage).
    error_handling: Raises a specific error for a missing file, a path that isn't a file, a permission-denied file, a file that can't be decoded as text, or a file containing no numbered clauses (nothing to summarize). Never fabricates section or clause content to compensate for a parse failure — an unparseable or empty document is reported as an error, not silently patched or guessed at.

  - name: summarize_policy
    description: Takes the structured sections produced by retrieve_policy and produces a clause-referenced summary, preserving every clause number, every condition of multi-condition obligations, and the original binding strength of each obligation.
    input: The structured document returned by retrieve_policy (metadata + sections + clauses).
    output: A plain-text summary, organized by section in source order, where every clause is tagged with its clause number (e.g. "[5.2]"). Clauses identified as binding and/or carrying more than one condition (numeric thresholds, named approvers, deadlines, "regardless of" / "not permitted" / "required" language) are kept verbatim and explicitly marked "(VERBATIM)" per the agents.md rule against summarizing away meaning, rather than being paraphrased.
    error_handling: If given an empty, missing, or malformed section list (e.g. retrieve_policy found no clauses), raises a clear error rather than producing an empty or invented summary. Never drops a clause it is unsure how to condense — it falls back to quoting it verbatim and flagging it instead of silently omitting it.
