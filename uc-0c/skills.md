# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
name: load_dataset description: Reads the budget CSV, validates the required schema columns, and identifies all rows containing null actual_spend values. input: type: string format: File path to the ward budget CSV dataset. output: type: array format: A list of objects containing period, ward, category, budgeted_amount, actual_spend, and notes. error_handling: Fails if the file is missing or schema is incorrect; explicitly reports the count and location of the 5 deliberate null rows before returning.

name: compute_growth description: Calculates period-over-period growth for a specific ward and category, returning a table that includes the growth percentage and the explicit formula. input: type: object format: Object containing ward (string), category (string), and growth_type (string, e.g., 'MoM'). output: type: array format: A per-period table including actual spend, growth result, and the mathematical formula used. error_handling: Refuses to process and asks for input if growth_type is missing; refuses any request involving aggregation across wards or categories; flags null rows and returns the reason from the notes column instead of a calculation.
