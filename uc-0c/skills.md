# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Loads CSV dataset and validates schema, identifying null rows
    input: File path to CSV
    output: List of rows + list of rows where actual_spend is null
    error_handling: Raises error if required columns missing or file unreadable

  - name: compute_growth
    description: Computes growth per period for a given ward and category using specified growth type
    input: ward (string), category (string), growth_type (MoM/YoY), dataset rows
    output: Table with period, actual_spend, growth %, and formula used
    error_handling: Skips null rows and flags them with reason from notes column