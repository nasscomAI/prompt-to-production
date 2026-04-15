name: classify_complaint
  description: Transforms a single citizen complaint description into a structured classification containing category, priority, cited reason, and an ambiguity flag.
  input:
    type: Object
    format: Single CSV row representing a complaint (e.g., {"description": "..."})
  output:
    type: Object
    format: "{ \"category\": \"...\", \"priority\": \"...\", \"reason\": \"...\", \"flag\": \"...\" }"
  error_handling: When the complaint description is genuinely ambiguous, the skill must set the flag to NEEDS_REVIEW instead of forcing a category; if severity keywords like injury or hospital are present, it must override any default priority to Urgent to prevent severity blindness.

- name: batch_classify
  description: Orchestrates the classification of multiple complaints by reading an input CSV, applying individual classification logic, and writing the final results to a structured output CSV.
  input:
    type: String
    format: Path to the input CSV file (e.g., ../data/city-test-files/test_kolkata.csv)
  output:
    type: String
    format: Path to the generated output CSV file (e.g., uc-0a/results_kolkata.csv)
  error_handling: To prevent taxonomy drift, the skill must validate that every category generated matches the exact allowed strings and ensure naming consistency across all rows; if missing justification or hallucinated categories are detected during processing, the skill must abort and log the specific failure mode.
