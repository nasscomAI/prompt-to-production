del skills.md

(

echo skills:

echo - name: load\_dataset

echo   description: Read the budget CSV, validate required columns, identify null actual\_spend values, and report their reasons.

echo   input: Path to ward\_budget.csv.

echo   output: Validated budget records and null-row report.

echo   error\_handling: Reject missing columns or invalid data and explicitly report null actual\_spend rows instead of silently dropping them.

echo - name: compute\_growth

echo   description: Compute the requested growth type for one ward and one category at the monthly per-period level with the formula shown.

echo   input: Ward, category, and explicitly specified growth\_type.

echo   output: Per-period growth table containing period, actual spend, previous spend, formula, growth result, and null status.

echo   error\_handling: Refuse unspecified growth types, cross-ward or cross-category aggregation, and growth calculations involving null current or previous values.

)>skills.md

