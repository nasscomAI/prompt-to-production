# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description and classifies it by category and priority.
    input: A string containing the complaint description.
    output: A JSON object with the following fields: `category` (string), `priority` (string), `reason` (string), `flag` (string).
    error_handling: If the description is empty or nonsense, set category to "Other", priority to "Low", and reason to "Invalid input description".

  - name: batch_classify
    description: Processes a CSV file of complaints, classifies each row, and writes the results to a new CSV file.
    input: File path to the input CSV (e.g., `data/city-test-files/test_pune.csv`).
    output: File path to the generated results CSV (e.g., `results_pune.csv`).
    error_handling: Ensure the output directory is writable. If a row fails to classify, skip it and log the error, or use default values.
