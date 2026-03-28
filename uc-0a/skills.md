- name: classify_complaint
  description: Analyzes text to determine the correct department for routing.
  input: "string (raw complaint text)"
  output: "string (category name)"
  error_handling: "If text is empty, return 'Error: No input'."
- name: save_results
  description: Appends the classified results to a CSV file.
  input: "list of classified objects"
  output: "CSV file"
  error_handling: "Ensure the file results_bengaluru.csv is created if it doesn't exist."