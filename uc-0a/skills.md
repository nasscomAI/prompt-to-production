- name: classify_complaint
  description: Classifies a single citizen complaint row into a specific category and priority level based on a predefined schema and severity keywords.
  input: Dictionary representing a single CSV row containing at least a text description.
  output: Dictionary containing category (string), priority (string), reason (string), and flag (string).
  error_handling: If the description contains severity keywords, force 'Urgent' priority; if the category is ambiguous, set flag to 'NEEDS_REVIEW'; if input is missing a description, return a schema-compliant error row with the flag 'NEEDS_REVIEW'.
  
- name: batch_classify
  description: Orchestrates the end-to-end processing of a city-specific input CSV file by applying individual classification logic to every row and saving the results.
  input: Path to a CSV file (string) formatted as ../data/city-test-files/test_[your-city].csv.
  output: Path to the generated CSV file (string) located at uc-0a/results_[your-city].csv.
  error_handling: Validates the presence of the input file and prevents taxonomy drift by enforcing exact string matching across all rows; if the input file contains zero rows or invalid columns, the skill logs a failure and aborts the write process.
