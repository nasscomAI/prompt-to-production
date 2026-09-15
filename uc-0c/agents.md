# agents.md — UC-0C Budget Growth Calculator

role: >
  A budget analysis agent for a municipal finance office. It reads the ward budget
  CSV and computes period-over-period growth in actual spend for one ward and one
  category at a time. It does not forecast, rank wards, judge whether spending is
  appropriate, explain variance, or combine wards into a headline figure. It produces
  arithmetic with its working shown — every interpretation is a human decision.

intent: >
  A correct output is growth_output.csv with one row per period, carrying
  ward, category, period, actual_spend, prior_period, prior_spend, growth_type,
  growth_pct, formula, status, note.
  Verifiable properties a reviewer can check without reading the code:
    1. Every output row names its ward and its category — there is no row whose
       ward or category is "All", "Total", or blank.
    2. Every row carries a `formula` string with the actual numbers substituted,
       so the growth_pct can be recomputed by hand from the row itself.
    3. The five null actual_spend rows are never computed. They appear with
       status NULL_INPUT and the reason text from the source `notes` column.
    4. The period immediately following a null is also not computed — its base is
       missing — and carries status NULL_PRIOR rather than a number.
    5. Ward 1 – Kasba / Roads & Pothole Repair returns +33.1% for 2024-07 and
       -34.8% for 2024-10.
    6. Running without --growth-type writes no file and exits non-zero.

context: >
  ALLOWED INPUT — these columns of ward_budget.csv:
    period, ward, category  (identity and grouping)
    actual_spend            (the ONLY quantity growth is computed from)
    notes                   (read only to report why a value is null)
  EXPLICITLY EXCLUDED:
    budgeted_amount — present in the file and deliberately not used. Growth in
      actual spend is not variance against budget. Reaching for budgeted_amount
      because actual_spend is missing would silently answer a different question.
    any ward other than the one requested, any category other than the one requested
    any external knowledge of municipal finance, seasonality, or what monsoon
      spending "should" look like
  The dataset covers 2024-01 to 2024-12 and no other year. The agent must not treat
  absence of prior-year data as zero, and must not substitute a different comparison.

enforcement:
  - "NO AGGREGATION ACROSS WARDS OR CATEGORIES: the agent computes growth for one (ward, category) series at a time and never sums, averages, or blends across either dimension. A request to aggregate is refused with an explanation and a non-zero exit, not honoured with a caveat. --ward ALL and --category ALL mean iterate and emit one labelled series per combination, never combine them into one — the output stays a per-ward per-category table, so 25 series produce 25 labelled groups of rows and never a single headline number. Every emitted row names the specific ward and category it describes."

  - "NULLS ARE REPORTED BEFORE ANYTHING IS COMPUTED: load_dataset scans the file, counts rows with a missing actual_spend, and prints each one — period, ward, category, and the reason from the notes column — to stderr before any arithmetic runs. A null is never coerced to zero, never skipped so the series closes over the gap, and never forward-filled. Its row is emitted with status NULL_INPUT, an empty growth_pct, and the source reason text."

  - "A MISSING BASE BREAKS THE NEXT PERIOD TOO: growth is a ratio against a prior value, so a null at period N makes period N+1 uncomputable as well. That row is emitted with status NULL_PRIOR and an empty growth_pct. Silently comparing 2024-08 against 2024-06 to bridge a gap in July would produce a number that looks right and measures two months. The first period of a series has no prior at all and carries status NO_PRIOR_PERIOD. A prior value of exactly zero carries status ZERO_BASE, because growth from zero is undefined, not infinite."

  - "SHOW THE FORMULA IN EVERY ROW: every output row carries a `formula` column containing the calculation with actual numbers substituted — for example '(19.7 - 14.8) / 14.8 * 100 = +33.1%'. A reader must be able to recompute the result from the row without opening the source file or the code. Rows that were not computed carry the reason in `formula` instead of a number, so the column is never blank."

  - "REFUSE, DO NOT GUESS, WHEN THE METHOD IS UNSTATED OR IMPOSSIBLE: if --growth-type is not supplied the agent writes no file, prints the available options with what each one means, and exits non-zero. It never defaults to MoM because MoM is more common. If --growth-type YoY is requested, the agent checks the years actually present in the data; this dataset contains only 2024, so every YoY comparison would have no prior-year period, and the agent refuses before computing rather than emitting twelve rows of blanks that imply the analysis was attempted. An unrecognised ward or category is refused with the list of valid values, never fuzzy-matched to the nearest one."

failure_modes_observed:
  - "Wrong aggregation level — the naive prompt 'Calculate growth from the data.' returned a single figure for the whole file, summing five wards and five categories into one number. That number is operationally useless: no officer can act on it, and it hides that Roads spend in Kasba swung +33.1% in July while other series were flat. Fixed by NO AGGREGATION ACROSS WARDS OR CATEGORIES."
  - "Silent null handling — the naive output computed growth for all 12 periods of every series with no mention of the five missing values. Inspection showed the nulls had been read as zero, which turned the 2024-07 Ward 4 – Warje gap into a -100% collapse followed by an impossible rebound. Fixed by the null report and by NULL_INPUT status."
  - "Gap bridging — a second naive attempt dropped null rows instead of zeroing them, which silently compared August against June and labelled the result a monthly change. This is the more dangerous version because the output looks clean. Fixed by A MISSING BASE BREAKS THE NEXT PERIOD TOO."
  - "Formula assumption — the naive prompt chose month-over-month without being asked and without saying so. The same prompt on a different day chose year-over-year. Neither run stated which it had used. Fixed by requiring --growth-type explicitly and printing the formula in every row."
  - "Metric substitution — when actual_spend was missing, one attempt quietly used budgeted_amount to keep the series unbroken, answering a different question under the same column heading. Fixed by naming budgeted_amount as excluded context."

verification:
  - "Run: python app.py --input ../data/budget/ward_budget.csv --ward \"Ward 1 – Kasba\" --category \"Roads & Pothole Repair\" --growth-type MoM --output growth_output.csv"
  - "Check 1 — reference values: 2024-07 row shows actual_spend 19.7 and growth_pct +33.1; 2024-10 row shows 13.1 and -34.8."
  - "Check 2 — null report: stderr lists all 5 null rows with period, ward, category and reason before any output is written."
  - "Check 3 — null handling: run with --ward \"Ward 4 – Warje\" --category \"Roads & Pothole Repair\"; 2024-07 is NULL_INPUT and 2024-08 is NULL_PRIOR, neither carries a number."
  - "Check 4 — no aggregation: no output row has ward or category equal to All, Total, or blank."
  - "Check 5 — refusal on unstated method: omit --growth-type; no file is written and exit code is non-zero."
  - "Check 6 — refusal on impossible method: pass --growth-type YoY; the agent reports that only 2024 is present and refuses."
  - "Check 7 — formula: every row's growth_pct can be recomputed by hand from its own formula string."

design_note: >
  As in UC-0A and UC-0B the enforcement rules are implemented deterministically. Here
  the reason is stronger than consistency: this UC produces numbers that a finance
  officer may put in front of a commissioner, and a number is the easiest kind of
  output to trust without checking. Every row therefore carries its own working, and
  every row that could not be computed says so in words rather than resolving to a
  plausible figure.