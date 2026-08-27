# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single municipal complaint row into a rigid taxonomy and determines its severity-based priority.
    input: A single string representation or dictionary corresponding to one complaint row, specifically providing the `description`.
    output: A dictionary or structured object containing strictly `category`, `priority`, `reason`, and `flag` fields.
    error_handling: If the description is empty, unparsable, or ambiguous across multiple categories, do not crash but set the output `flag` to 'NEEDS_REVIEW' and assign `category` to 'Other'.

  - name: batch_classify
    description: Iterates through a CSV file and applies classify_complaint sequentially to every complaint.
    input: An input file path to a CSV (e.g. `test_pune.csv`) containing municipal complaints.
    output: An output file path for the results CSV where the classified columns (`category`, `priority`, `reason`, `flag`) are successfully appended to the original schema.
    error_handling: Catch exceptions for individual bad rows without halting the entire job. Let failed rows pass through with `flag` set to 'SYSTEM_ERROR' or proceed to the next valid row cleanly.
