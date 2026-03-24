- name: classify_complaint
  description: Classifies complaint text into categories
  input: string
  output: category
  error_handling: Return "Other" if no match

- name: read_csv
  description: Reads complaints from CSV file
  input: file path
  output: list of complaints
  error_handling: Show error if file missing