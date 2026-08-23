# skills.md — UC-0C Budget Growth Agent

skills:
  - name: load_dataset
    description: Reads the ward-budget CSV, validates its columns, and reports the null actual_spend rows (count plus exact keys and reasons) before any computation happens.
    input: >
      One path — path to a CSV with columns period (YYYY-MM), ward (string),
      category (string), budgeted_amount (float, always present),
      actual_spend (float or blank) and notes (string giving the null
      reason).
    output: >
      Dict — { rows: [ { period: str, ward: str, category: str,
                         budgeted_amount: float,
                         actual_spend: float | None,
                         notes: str } ],
               wards: [str] (unique, order of appearance),
               categories: [str] (unique, order of appearance),
               null_report: { count: int,
                              rows: [ { period, ward, category,
                                        reason: str (verbatim from notes) } ] } }
    error_handling: >
      If the file is missing or unreadable, or any required column is
      absent, exit non-zero with an error naming exactly what is wrong —
      there is nothing to compute. Blank actual_spend cells are kept as
      None, never replaced by 0, averages or neighbouring months; each one
      becomes an entry in null_report with its reason copied verbatim from
      notes. Rows are otherwise passed through unchanged — no deduplication,
      sorting or cleaning that could hide data problems.

  - name: compute_growth
    description: Computes period-over-period growth for exactly one ward + category series, showing the formula on every row and flagging null months instead of computing through them.
    input: >
      The dict returned by load_dataset plus three arguments — ward (exact
      string as it appears in the CSV), category (exact string) and
      growth_type (MoM = month-over-month, YoY = same month one year
      earlier; there is no default).
    output: >
      CSV table — one row per period of that single series, columns:
      period, ward, category, actual_spend, previous_spend, growth_pct,
      formula, flag. Computed rows show the arithmetic inline, e.g.
      "growth_pct = (19.7 - 14.8) / 14.8 * 100" with growth_pct "+33.1%".
      Rows whose current or previous month has null actual_spend carry
      growth_pct NA and flag "NULL_SPEND: <reason from notes>"; the first
      period of the series (or of each YoY window) carries flag
      "NO_PREVIOUS_PERIOD".
    error_handling: >
      Refuses rather than guesses: missing or unknown growth_type, ward or
      category not found in the dataset (reply lists the valid options), or
      any request covering more than one ward or more than one category all
      exit non-zero with an explanation instead of returning a number.
      Null months are never interpolated or bridged — growth across a null
      gap is NA with the null reason, not a value computed around it. An
      empty series after filtering (e.g. ward exists but category does not)
      is treated as a refusal case, not an empty output file.
