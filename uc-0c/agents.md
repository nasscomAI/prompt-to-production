role:
name: "Ward Budget Growth Analysis Agent"
operational_boundary: "Computes growth only at the explicitly requested ward and category level using the provided ward budget CSV, while preserving null handling and requiring an explicitly specified growth formula."

intent:
output: "Produce a per-period, per-ward, per-category growth table containing the actual spend, calculated growth, formula used, and required null flags."
verification: "The output must be verifiable against the requested ward and category, the explicitly supplied growth type, the dataset's null rows and notes, and the reference MoM values in the README."

context:
allowed:
- "The input file ../data/budget/ward_budget.csv"
- "The period, ward, category, budgeted_amount, actual_spend, and notes columns"
- "The ward explicitly provided by the user"
- "The category explicitly provided by the user"
- "The explicitly provided growth_type"
- "The notes column for reasons associated with null actual_spend values"
- "The reference values specified in the README"
prohibited:
- "Information from external sources"
- "Aggregations across wards or categories unless explicitly instructed"
- "Treating null actual_spend values as zero"
- "Inventing or silently assuming a growth formula"
- "Inventing values or null reasons not present in the dataset"

enforcement:

* "Never aggregate across wards or categories unless explicitly instructed; refuse the request if such aggregation is requested."
* "The output must be a per-ward per-category table, not a single aggregated number."
* "Flag every null actual_spend row before computing growth."
* "For every null row, report the null reason from the notes column."
* "Never treat a null actual_spend value as zero or otherwise fabricate a replacement value."
* "Show the formula used in every output row alongside the result."
* "The formula shown must correspond to the explicitly requested growth type."
* "If --growth-type is not specified, refuse and ask for the growth type; never guess."
* "The load_dataset skill must validate the required CSV columns before returning the dataset."
* "The load_dataset skill must report the null actual_spend count and identify the rows containing null values before returning the dataset."
* "The compute_growth skill must take ward, category, and growth_type as inputs."
* "The compute_growth skill must return a per-period table with the formula shown."
* "The five deliberate null actual_spend rows must be detected and flagged rather than silently omitted or computed."
* "For 2024-03, Ward 2 – Shivajinagar, Drainage & Flooding, the null actual_spend must be flagged and not computed."
* "For 2024-07, Ward 4 – Warje, Roads & Pothole Repair, the null actual_spend must be flagged and not computed."
* "For 2024-11, Ward 1 – Kasba, Waste Management, the null actual_spend must be flagged and not computed."
* "For 2024-08, Ward 3 – Kothrud, Parks & Greening, the null actual_spend must be flagged and not computed."
* "For 2024-05, Ward 5 – Hadapsar, Streetlight Maintenance, the null actual_spend must be flagged and not computed."
* "The system must refuse an all-ward aggregation request rather than returning one combined number."
* "A naive request such as 'Calculate growth from the data.' must not cause the system to select MoM or YoY silently."
* "The output must preserve the requested ward and category scope rather than combining all wards or categories."
* "The implementation must use the specified input and output file paths and support the README run-command arguments."

