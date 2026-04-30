skills:
  - name: [load_dataset]
    description: [Reads the CSV dataset, validates required columns, and explicitly reports the total count and specific rows containing null values before returning the data.]
    input: [type: string format: Filepath to the CSV dataset]
    output: [type: object format: Validated dataset structure containing the data and a metadata report of all null rows.]
    error_handling: [If required columns are missing, throw an error; if null actual_spend values exist, flag them and report the null reason from the notes column instead of silently handling them.]

  - name: [compute_growth]
    description: [Computes the specified growth metric for a specific ward and category over time, outputting the result and the exact formula used. ]
    input: [type: object format: Parameters including ward (string), category (string), and growth_type (string)]
    output: [type: table format: Per-period table output showing actual spend, computed growth, and the explicit formula used for every row]
    error_handling: [If growth_type is not specified, refuse and ask instead of guessing; if asked to aggregate across wards or categories, refuse; if a null actual_spend row is encountered, flag it and do not compute the result.]
