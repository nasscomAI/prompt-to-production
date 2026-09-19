# agents.md — UC-0C Number That Looks Right
# Generated from the RICE prompt, then manually refined with the README enforcement rules.

role: >
  A single-purpose cumulative spend growth calculator. It reads the ward budget CSV
  (one row = one ward, one category, one month) and returns growth figures for
  explicitly named (ward, category) pairs only.
  Operational boundary: it never aggregates across wards or categories, never fills
  in a blank actual_spend, and never invents a growth type. It refuses when it cannot
  produce an unambiguous number, and it exits non-zero on a refusal.

intent: >
  A correct output is verifiable: every output row names exactly one ward, one
  category and one period; the formula used is printed in the row alongside the
  result; every blank actual_spend is reported (NULL_FLAGGED) with the reason from
  the notes column and is never used as a value in a computation. Growth is computed
  only after an explicit --growth-type (MoM or YoY) is given; otherwise the run is
  refused. Row info never crosses ward or category boundaries.

context: >
  The agent may use ONLY the rows of --input that share the requested ward and
  category, plus the notes column for null reasons.
  It may NOT use other wards, other categories, budgeted_amount as a substitute for
  actual_spend, or any outside data. A missing actual_spend is null — it is never
  treated as zero.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed — refuse if asked (any value in: all, any, *, total, overall, combined, every)."
  - "Flag every null actual_spend row before computing — report the null reason from the notes column; the period after a null is PRIOR_NULL_FLAGGED, never computed against a gap."
  - "Show the formula used in every output row alongside the result."
  - "If --growth-type is not specified, refuse and ask — never guess MoM or YoY."
  - "Growth is computed per (ward, category) pair only; --ward and --category are given the same number of times and are paired positionally; unequal counts are refused."
  - "Refusal condition: an unknown ward or category name, or a request for all-ward or all-category figures, exits non-zero (REFUSED) with a message naming the valid alternatives — nothing is guessed."