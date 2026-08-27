role: >
  Budget growth reporter for the Pune Municipal Corporation ward expenditure
  ledger. It computes period-over-period growth in actual spend for a named
  ward and a named category, and reports the data quality of the rows it used.
  Its operational boundary is arithmetic and reporting only: it does not judge
  whether spending was appropriate, explain variances, forecast future periods,
  or recommend budget changes. It never fills in a value the ledger does not
  contain.

intent: >
  For a requested ward and category, emit one output row per period showing the
  actual spend, the growth against the comparison period, and the formula that
  produced it. A reader must be able to recompute any single row by hand from
  the two spend figures and the printed formula. Where a spend figure is
  missing, the output must say so in that row rather than showing a number.
  Correctness is checkable against the published reference values: Ward 1 Kasba
  Roads and Pothole Repair is +33.1% in 2024-07 and -34.8% in 2024-10.

context: >
  Input is data/budget/ward_budget.csv -- 300 rows covering 5 wards x 5
  categories x 12 months of 2024, with columns period, ward, category,
  budgeted_amount, actual_spend, notes. Growth is computed from actual_spend
  only. budgeted_amount is present in the file but is not a substitute for a
  missing actual_spend and must never be used as one. Five actual_spend cells
  are deliberately empty and each carries an explanation in notes; that
  explanation is part of the output, not discard material. No outside knowledge
  of municipal finance, inflation, or typical seasonal spending may enter the
  calculation.

enforcement:
  - "An empty actual_spend is missing data, not zero. It must never be coerced
     to 0, to the budgeted_amount, to the previous period's value, or to any
     interpolated figure. Substituting a number for absence produces a total
     that looks complete and is not."
  - "Every missing actual_spend must be reported before any growth figure is
     computed, listing its period, ward, category and the verbatim text of its
     notes field. The reason a figure is missing is information the ward office
     supplied deliberately and it survives into the output."
  - "A period whose actual_spend is missing yields growth of MISSING_DATA, not
     a number and not a blank cell. A period whose comparison period is missing
     yields the same, because growth against an unknown base is not computable."
  - "The count of missing rows encountered must appear in the results file as a
     column, so that a reader who sees only that file still knows the source was
     incomplete. It must not be written as a trailing comment line: a CSV reader
     counts a comment as an extra data row, and a results file that corrupts its
     own consumer is the same class of failure as a total that silently excludes
     a ward."
  - "The growth type is supplied by the caller and never inferred. If
     --growth-type is absent the request is refused with the list of supported
     types. Month-on-month and year-on-year answer different questions and a
     silently chosen default produces a number the reader will misread as the
     one they asked for."
  - "Every output row shows the formula that produced its own figure, with the
     two spend values substituted in, so that a reader can recompute that row by
     hand without opening the source ledger or this code."
  - "A growth type the ledger cannot support is refused, not attempted. This
     ledger covers 2024-01 to 2024-12 only, so year-on-year growth has no
     comparison base for any row; returning 300 uncomputable rows would look
     like a defect in the code rather than a limit of the data."
  - "Growth is computed within a single ward and a single category. Spend from
     two different wards, or two different categories, is never added together
     before a growth figure is taken. Five wards times five categories is
     twenty-five independent series, not one."
  - "A request to aggregate across wards or across categories is refused, not
     served. --ward all, --category all and any equivalent is answered with a
     refusal naming the permitted values. The refusal is the correct output:
     a citywide growth number is arithmetically valid and operationally
     useless, because no ward officer can act on it."
  - "Every output row carries its own ward and category. A results file whose
     rows cannot be attributed to a specific ward and category is invalid
     output even if every number in it is correct."
  - "An unrecognised ward or category name is refused with the list of valid
     values. It is never silently matched to the nearest name, and never
     silently returns an empty result that would read as 'no spending'."
  - "MISSING_DATA and NO_PRIOR_PERIOD are distinct and must not be merged. The
     first period of a series has no comparison base by definition -- that is a
     property of the series, not a gap in the ledger. Reporting both as the same
     value would tell a reader the January figure is untrustworthy when it is
     simply the start of the range."
