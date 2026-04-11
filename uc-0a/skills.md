skills:
  - name: classify_complaint
    description: Analyzes a single civic complaint description to accurately categorize it, assign priority based on severity keywords, and justify the classification.
    input: A single citizen complaint describing an issue (String/Text row).
    output: A structured record containing `category` (exact predefined string), `priority` (Urgent, Standard, Low), `reason` (1 sentence citing specific text), and `flag` (NEEDS_REVIEW or blank).
    error_handling: If the category is genuinely ambiguous and cannot be confidently determined from the text alone, sets the `flag` field to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV dataset of complaints, applies `classify_complaint` sequentially to each row, and writes out a fully classified CSV file.
    input: File path to the input dataset CSV (e.g., `test_pune.csv`) and file path to the desired output CSV.
    output: Writes a structured CSV file named using the format `results_[city_name].csv` (e.g., `results_pune.csv`) populated with the generated classification columns for all rows.
    error_handling: If a row is malformed or classification fails, it logs the error, safely skips or flags the row, and continues processing the rest of the batch.
