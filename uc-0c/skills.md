# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: [load_dataset]
    description: [Reads the provided CSV budget dataset, comprehensively validates all expected columns, and explicitly reports the total count and exact locations of any null values before returning the data.]
    input: [String representing the file path to the input CSV document.]
    output: [Parsed dataset object accompanied by a metadata report detailing the number and locations of any null actual_spend rows.]
    error_handling: [Halts execution if the file is missing or malformed; strictly traps silent null handling by explicitly highlighting flagged rows and citing the null reason from the notes column instead of dropping or guessing the value.]

  - name: [compute_growth]
    description: [Calculates the specified growth metric for a strictly defined single ward and single category, returning a per-period table that visibly displays the applied formula.]
    input: [Validated dataset object, a specific ward string, a specific category string, and an explicitly provided growth_type string.]
    output: [A structured, per-period table output representing the growth over time alongside the exact mathematical formula used for each row's specific calculation.]
    error_handling: [Actively refuses computation if the growth_type is not explicitly provided rather than assuming a default; strictly rejects any cross-ward or cross-category aggregation requests; skips computation for flagged null rows and instead outputs the null reason to prevent formula errors.]
