skills.md — UC-0C Budget Growth Analyser
skills:

name: load_dataset
description: >
Reads the ward_budget CSV, validates that all required columns are present,
and reports the count and identity of null actual_spend rows before
returning the data.
input: >
A file path string pointing to a CSV with columns: period, ward, category,
budgeted_amount, actual_spend, notes.
output: >
A tuple of (list of row dicts, null_report list). The null_report is a list
of dicts with keys: period, ward, category, reason — one entry per null
actual_spend row. Prints a null summary to stdout before returning.
error_handling: >
If the file does not exist, raise FileNotFoundError with a clear message.
If any required column is missing, raise ValueError naming the missing
column. If actual_spend is present but non-numeric (and non-blank), flag
that row as null with reason "non-numeric value".
name: compute_growth
description: >
Takes a filtered dataset for one ward and one category, a growth type
(MoM or YoY), and returns a per-period table with growth rate and formula
shown for every row.
input: >
A list of row dicts (pre-filtered to one ward + one category), and a
growth_type string that must be exactly "MoM" or "YoY".
output: >
A list of result dicts with keys: period, actual_spend, prev_period,
prev_spend, growth_pct, formula_used, null_flag. Rows where growth cannot
be computed (null current or null previous) have growth_pct=None and
null_flag set to "NULL" or "PREV_NULL" accordingly.
error_handling: >
If growth_type is not "MoM" or "YoY", raise ValueError and refuse to
proceed — never default. If the filtered dataset is empty (ward/category
not found), raise ValueError naming the missing combination. Null rows are
never dropped — they appear in output with null_flag set.