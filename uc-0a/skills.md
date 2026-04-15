- name: classify_complaint
  description: Classify complaint into category, priority, reason and flag
  input: complaint text
  output: category, priority, reason, flag
  error_handling: mark NEEDS_REVIEW if unclear

- name: batch_classify
  description: Process CSV and classify all complaints
  input: csv file
  output: classified csv file
  error_handling: return error if file invalid
