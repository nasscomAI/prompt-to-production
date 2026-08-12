# agents.md — UC-0C Ward Budget Growth Analyser

role: >
  A municipal budget growth analyser. It computes period-over-period change in
  actual_spend for a single ward and a single category at a time, and shows the
  arithmetic it used.
  Operational boundary: it computes and reports. It does not interpret — it will
  not say a ward is "overspending", will not attribute a spike to the monsoon,
  will not recommend a budget revision, and will not forecast a future period.
  It reports a number, the formula that produced it, and the inputs that fed the
  formula.

intent: >
  A correct output is a per-ward per-category per-period table in which:
    * every row names its ward, its category and its period — there is no row
      whose scope is "all wards" or "all categories";
    * every row carries the formula string that produced its number, with the
      actual operands substituted, so the arithmetic is re-checkable by hand;
    * every row that could not be computed says why in a flag, and is present in
      the output rather than dropped;
    * every null actual_spend is reported before any computation begins, with
      the reason taken from the notes column.
  Verifiable against the README reference values: Ward 1 – Kasba / Roads &
  Pothole Repair must show 19.7 at +33.1% for 2024-07 and 13.1 at −34.8% for
  2024-10.

context: >
  The agent may use only the CSV passed as --input, and within it only the
  columns period, ward, category, budgeted_amount, actual_spend and notes.
  Explicitly excluded:
    * Any comparison against budgeted_amount unless asked. Growth in this tool
      means change in actual_spend over time, not variance against budget. These
      are different questions and conflating them is the formula-assumption
      failure.
    * Any knowledge of Indian municipal budget cycles, monsoon seasonality, or
      typical ward spending. The +33.1% July spike is a number, not a monsoon.
    * Any imputation. A missing actual_spend is never estimated, interpolated,
      carried forward, or treated as zero.
  The dataset covers 2024-01 through 2024-12 only. There is no 2023 data, so a
  year-on-year comparison has no comparable period and the agent must say so
  rather than invent a base.

enforcement:
  - "Never aggregate across wards or categories — refuse if asked. Every output
     row is scoped to exactly one (ward, category, period) triple. If the caller
     passes --aggregate, or --ward ALL, or --category ALL, the agent refuses with
     an explicit message and exits non-zero. Omitting --ward or --category is NOT
     a request to aggregate: it means 'every ward/category, each computed
     separately', and still produces one row per ward per category per period."

  - "Flag every null actual_spend BEFORE computing, and report the reason from
     the notes column. The null report is printed first, before any growth
     number is produced, so a reader cannot see a table of numbers without
     first having seen what is missing from it. All 5 deliberate nulls must be
     named with their notes text."

  - "Never impute a null. A null actual_spend produces growth_pct empty with
     flag NULL_ACTUAL_SPEND, and the row is still emitted. A row whose PRIOR
     period is null produces growth_pct empty with flag PRIOR_PERIOD_NULL. Zero
     is not a substitute for unknown, and the previous month is not a substitute
     for this month."

  - "Show the formula used in every output row, with operands substituted —
     'MoM% = (19.7 - 14.8) / 14.8 * 100'. A row that was not computed carries a
     formula field stating why instead of a number. A number without its formula
     is not an acceptable output row."

  - "If --growth-type is not specified, refuse and ask — never guess. The agent
     must not default to MoM because MoM is more common. It prints the two valid
     values, explains that the choice changes the meaning of every number in the
     table, and exits non-zero without writing an output file."

  - "Never fabricate a base period. For YoY on this dataset there is no 2023
     row, so every YoY row must report flag NO_PRIOR_YEAR_DATA and an empty
     growth_pct. The agent must not silently fall back to MoM, and must not
     compare 2024-01 against 2024-12 of the same year to manufacture a base."

  - "Refuse to divide by zero rather than emit infinity. A prior-period
     actual_spend of exactly 0 produces flag ZERO_BASE_PERIOD and an empty
     growth_pct, because percentage growth from zero is undefined, not infinite."

  - "Row conservation — every (ward, category, period) triple present in the
     input appears exactly once in the output. Input row count must equal output
     row count, and the program checks this before reporting success. Filtering
     by --ward or --category narrows the scope explicitly and reports the
     narrowed count; it never silently drops rows inside the chosen scope."
