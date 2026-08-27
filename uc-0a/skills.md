# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint string and returns exactly mapped category, priority, an extracted reason citation, and an optional review flag.
    input: A single unstructured text string containing the citizen's complaint description.
    output: A structured record containing `category` (string), `priority` (string), `reason` (string), and `flag` (string).
    error_handling: "If the input string is empty or genuinely ambiguous preventing confident classification against the allowed schema, returns category='Other' and flag='NEEDS_REVIEW'."

  - name: batch_classify
    description: Processes a given input CSV file by systematically applying `classify_complaint` to each row and writing the structured outcomes into an output CSV.
    input: Filepaths to both the input CSV (containing unclassified complaints) and output CSV (destination).
    output: A newly formulated output CSV file populated with the classified data.
    error_handling: "If the batch process encounters missing files, it raises an exception to halt execution. If an individual row fails classification, it gracefully defaults that row to 'Other'/'NEEDS_REVIEW' ensuring the batch continues without crashing."
