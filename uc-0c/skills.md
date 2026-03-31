skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates the required columns, and explicitly reports the total count and exact row locations of any null values.
    input:
      type: file_path
      format: Path to the ward budget CSV dataset containing period, ward, category, budgeted_amount, actual_spend, and notes.
    output:
      type: array
      format: A validated collection of data rows alongside metadata strictly documenting the locations and reasons for any null data entries.
    error_handling: Halts execution with a structural error if the file is unreadable or schema is malformed; explicitly intercepts any silent null omission by mandating that every null in the actual_spend column must be logged alongside its corresponding justification from the notes column prior to any return.
  - name: compute_growth
    description: Generates a distinct per-period growth table for an explicitly specified ward and category while enforcing the display of the exact mathematical formula used for each row.
    input:
      type: object
      format: Contains the dataset rows alongside explicit string parameters for target 'ward', target 'category', and a strictly mandatory 'growth_type'.
    output:
      type: array
      format: A per-period table detailing actual spend, calculated growth, explicit null flag statuses, and the explicitly shown formula.
    error_handling: Refuses execution outright if asked to summarize 'Any' ward or category to prevent improper aggregation levels; halts and prompts the user if the 'growth_type' parameter is omitted to completely eliminate formula assumption; catches null data rows by explicitly flagging them as not computed and substituting the notes value rather than computing a zero or skipping silently.
