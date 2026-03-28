# skills.md
skills:

* name: complaint_category_detection
  description: Identifies complaint category from complaint text.
  input: complaint text string
  output: category name string
  error_handling: returns "Unknown" if complaint text is unclear

* name: priority_assignment
  description: Assigns complaint priority based on severity keywords.
  input: complaint text string
  output: High / Medium / Low
  error_handling: defaults to Medium if uncertain
