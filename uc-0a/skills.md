skills:
  - name: classify_complaint
    description: Evaluates a single citizen complaint to determine its category and priority.
    input: 
      - description (string): The raw text of the citizen complaint.
    output: 
      - category (string): One of the strictly approved taxonomy categories.
      - priority (string): Urgent, Standard, or Low depending on keyword triggers.
      - reason (string): One sentence quoting words from the description.
      - flag (string): 'NEEDS_REVIEW' if ambiguous, else blank.
    error_handling: "If input is unparseable or completely ambiguous, category=Other, flag=NEEDS_REVIEW."

  - name: batch_classify
    description: Reads a CSV of complaints, applies classify_complaint to each row, and writes results to a new CSV.
    input:
      - input_path (string): Path to `test_[city].csv`
      - output_path (string): Path to `results_[city].csv`
    output: 
      - A CSV file written to output_path containing original rows plus the 4 new classification columns.
    error_handling: "Must process all rows. If a row fails entirely, output default values with flag=NEEDS_REVIEW. Do not crash the entire batch."
