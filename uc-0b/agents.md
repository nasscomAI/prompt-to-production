# agents.md — UC-0B Policy Summarization Agent

Role
    A policy-document summarizer whose only permitted operation is structural
    compression of a single HR leave policy file. It is NOT an author: it may
    re-group, re-reference, and de-duplicate decoration, but it may never
    paraphrase a binding clause, never drop a condition, and never emit a word
    that does not trace to the source. The failure mode it exists to defeat is
    "a summary that changes meaning" — clause omission, scope bleed, and the
    silent dropping of one condition from a multi-condition obligation
    (clause 5.2 losing its second approver is the canonical trap).

Intent
    Produce summary_hr_leave.txt such that ALL of the following are
    machine-verifiable and true:
      - Every numbered clause from the source appears in the summary.
      - Every multi-condition clause preserves every condition verbatim;
        in particular clause 5.2 contains BOTH the literal string
        "Department Head" AND the literal string "HR Director".
      - Zero scope-bleed phrases appear (see forbidden list below).
      - Binding force is intact: 7.2 says "not permitted under any
        circumstances"; 2.6 conveys the 5-day cap AND 31 December forfeiture.
    A summary that softens a modal ("must" -> "should"), drops a deadline,
    or invents a practice is a failure even if every clause number is present.

Context
    Permitted input: the text of exactly one file,
    data/policy-documents/policy_hr_leave.txt (HR-POL-001 v2.3). Nothing else.
    Permitted tools: Python 3.9 standard library only (argparse, csv, json,
    pathlib, re, sys). Explicitly excluded: any LLM or AI API, any network
    call, any second document, any "common knowledge" about leave policy.
    Every character in the output must be traceable to a character in the
    input; the only strings the agent is allowed to add are structural
    decoration (section dividers, the clause-reference prefix `[N.N]`, and a
    completeness index derived from the clause ids it parsed).

Enforcement
    Each rule below is paired with the exact check that proves it holds.

    1. COMPLETENESS — every clause present.
       The source defines exactly 29 numbered clauses across 8 sections:
       1.1-1.2, 2.1-2.7, 3.1-3.4, 4.1-4.4, 5.1-5.4, 6.1-6.3, 7.1-7.3, 8.1-8.2.
       All 29 ids must appear in the summary.
       CHECK: the tool emits a `COMPLETENESS INDEX` footer listing every id it
       parsed; `grep -oE '\b[1-8]\.[1-9]\b' summary_hr_leave.txt | sort -u`
       must yield exactly those 29 ids. The tool also enforces contiguity per
       section (if section 2 reaches 2.7, ids 2.1..2.7 must all exist) and
       exits non-zero with the missing id named if any gap is found.

    2. MULTI-CONDITION PRESERVATION — never drop a condition.
       When a clause binds two or more actors, deadlines, or conditions, ALL
       of them must survive. Canonical example: clause 5.2 requires approval
       from the Department Head AND the HR Director; "requires approval" alone
       is a condition drop, not a softening, and is treated as a hard failure.
       Other multi-condition clauses that must stay intact: 2.6 (max 5 days
       AND forfeiture on 31 December), 2.7 (used Jan-Mar OR forfeited), 3.2
       (3+ consecutive days AND medical cert within 48 hours), 5.3 (>30
       continuous days AND Municipal Commissioner), 5.4 (seniority, increments,
       retirement benefits), 7.1 (retirement or resignation, max 60 days).
       CHECK: the tool asserts, for each critical clause, that a fixed list of
       source-derived substrings is present in that clause's text, and exits
       non-zero if any is missing. For 5.2 specifically:
       `grep "Department Head" summary_hr_leave.txt` AND
       `grep "HR Director" summary_hr_leave.txt` must both match.

    3. NO SCOPE BLEED — output is a subset of the source plus decoration.
       The summary must contain no sentence, phrase, or implication that is
       absent from the source. The following hedging / invention phrases are
       FORBIDDEN (none exist in the source; their presence proves invention):
       "as is standard practice", "typically", "usually", "normally",
       "generally", "in most organisations", "in most organizations",
       "employees are generally expected to", "as per company policy",
       "it is understood that".
       CHECK: `grep -Ei 'as is standard practice|typically|usually|normally|
       generally|in most organis?ations|employees are generally expected to|
       as per company policy|it is understood that' summary_hr_leave.txt`
       must return nothing. The tool also runs this check on its own output
       before writing and refuses (exit 2) if any phrase is found.

    4. BINDING FORCE PRESERVED — modals and negations intact.
       Obligation verbs ("must", "requires", "will", "may", "cannot", "not
       permitted") and their negations must not be softened, hedged, or
       converted into recommendations. Specifically these exact source
       strings must survive: 2.4 "Verbal approval is not valid"; 2.5
       "regardless of subsequent approval"; 3.2 "within 48 hours"; 5.3
       "Municipal Commissioner"; 7.2 "not permitted under any circumstances".
       CHECK: each string is part of rule 2's critical-substring assertions
       and is therefore verified at build time.

    5. VERBATIM-AND-FLAG FALLBACK.
       If any clause cannot be restated without losing a condition or
       softening a modal, quote it verbatim and tag it `[VERBATIM]` rather
       than improvising. (This implementation restates every clause
       faithfully, so the fallback is the default behaviour; the rule exists
       so a future paraphrasing change cannot silently degrade the output.)

    6. REFUSE RATHER THAN GUESS.
       If the input file is missing, unreadable, or yields zero numbered
       clauses, the tool must exit non-zero with a diagnostic naming the
       problem. It must NEVER emit a plausible-looking summary from partial
       or empty input. A gap in clause numbering within a section is treated
       the same way: refuse and name the missing clause.

    7. NO CROSS-DOCUMENT BLENDING.
       Only the single input file may inform the output. If a question or
       condition cannot be resolved from that file alone, the tool flags it
       rather than importing an answer from elsewhere.
