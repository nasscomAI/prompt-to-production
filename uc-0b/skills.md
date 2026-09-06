# skills.md

skills:
  - name: retrieve_policy
    description: Loads the Employee Leave Policy text file from disk and parses it into structured clause sections keyed by clause ID, preserving each clause's full normative text.
    input: policy_path (str) — path to the policy text file, e.g. ../data/policy-documents/policy_hr_leave.txt.
    output: A dict mapping each clause ID (e.g. "2.3") to a dict with 'section' (the schema heading, e.g. "ANNUAL LEAVE") and 'text' (the clause's normalized full text with line-wrapping collapsed).
    error_handling: If the file is missing, unreadable, or yields no numbered clauses, raises an error immediately and returns nothing — it never returns a silently partial clause set.

  - name: summarize_policy
    description: Takes the parsed clauses, applies condensation-by-exclusion (removing only boilerplate and redundant framing) to every clause 1.1–8.2, and enforces the grounding checks that make the summary lossless.
    input: clauses (dict from retrieve_policy), digests (dict of clause ID -> (active-voice digest text, list of condition keywords that MUST survive verbatim)), banned_phrases (list of out-of-scope phrases that MUST NOT appear), output_path (str — destination file).
    output: Writes uc-0b/summary_hr_leave.txt containing a short header plus one line per clause ID with its condensed digest; returns the list of clauses flagged [QUOTED] verbatim.
    error_handling: Runs a self-check pass BEFORE writing — verifies (a) all 29 clause IDs present, (b) every ground-truth condition keyword survives in both the digest and the source (covering the 'entitled to' lockdown, the 3.3 'to the following year' / 3.4 'immediately' / 6.1 'each year' qualifiers, and modal verbs must/will/requires/not permitted), (c) no banned scope-bleed phrase appears, (d) no softened modal verb is used, and (e) the digest is at least 15% shorter than the source clause text. Any failure raises an EnforcementError listing exact violations and writes NO output file.