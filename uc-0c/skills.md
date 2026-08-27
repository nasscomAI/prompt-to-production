skills:
  - name: load_dataset
    role: >
      Load and validate the ward-budget CSV before any growth calculation. This skill
      only prepares and reports the source data; it does not aggregate or compute growth.

    intent: >
      Return the validated rows together with a null-data report that states the total
      number of null actual_spend values and identifies every affected period, ward,
      category, and null reason from notes.

    context: >
      Use only the supplied CSV. Require period, ward, category, budgeted_amount,
      actual_spend, and notes columns; period values must be YYYY-MM. Treat blank
      actual_spend cells as nulls, not zeroes. Do not infer or substitute missing values.

    enforcement:
      - "Validate that all required columns exist before returning any rows; refuse an invalid or unreadable CSV."
      - "Report every null actual_spend row and its notes value before returning the dataset."
      - "Never aggregate, impute, drop, or silently coerce ward, category, period, or actual_spend values."
      - "Refuse to continue if a required field or a null reason cannot be read rather than guessing."

  - name: compute_growth
    role: >
      Compute explicitly requested growth for one ward and one category from validated
      budget data, preserving the per-period detail.

    intent: >
      Return a per-period table for the requested ward and category. Each computable row
      includes the actual spend, the comparison period and value, the named growth type,
      the formula with substituted values, and the resulting percentage; rows affected by
      missing data are flagged with their null reason instead of receiving a result.

    context: >
      Accept a validated dataset plus an exact ward, category, and growth_type. Support
      MoM as (current actual_spend - previous month's actual_spend) / previous month's
      actual_spend * 100. If YoY is requested, compare with the same month in the prior
      year only when that value is present; the supplied 2024-only data has no such
      comparison values. Use actual_spend only, not budgeted_amount, to calculate growth.

    enforcement:
      - "Never aggregate across wards or categories; refuse a request that omits either scope or asks for all-ward/all-category growth."
      - "Refuse and ask for growth_type when it is absent or unsupported; never select MoM or YoY by assumption."
      - "Flag a row whenever its current or comparison actual_spend is null, include the applicable notes reason, and do not compute it."
      - "Show the applicable formula in every output row; mark unavailable comparison data as not computable rather than inventing a value."
