
skills:
name: load_dataset
description: Reads the budget CSV file, validates dataset columns, and identifies all null rows prior to returning data.
input:
type: string
format: "File path to the target budget CSV file."
output:
type: object
format: "A parsed structure of rows alongside a report of identified null rows, their indices, and notes."
error_handling:
invalid_input: "Halt execution and report an error if the file path is incorrect, inaccessible, or does not contain required columns (period, ward, category, budgeted_amount, actual_spend, notes)."
ambiguous_input: "Not applicable for file paths."
failure_modes:
- "Report the total count of null values in 'actual_spend' and log which rows are null along with their reason notes before returning the parsed dataset."
name: compute_growth
description: Computes period-over-period growth for a specified ward and category using the designated growth formula, flagging nulls and exposing calculations.
input:
type: object
format: "A structure containing 'ward' (string), 'category' (string), and 'growth_type' (string)."
output:
type: array
format: "A sequence of records for each period containing the calculated growth metric, actual spend, and the explicit formula used."
error_handling:
invalid_input: "Refuse calculation and ask the user to clarify if the growth type is unspecified, missing, or unsupported."
ambiguous_input: "Refuse to execute and present an error if asked to aggregate across all wards or categories without explicit ward-by-ward or category-by-category instructions."
failure_modes:
- "Flag target rows with null actual spend, reporting the null reason from the notes column instead of attempting to compute growth values."