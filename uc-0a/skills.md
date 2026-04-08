- name: classify_complaint
  description: Classifies complaint into predefined categories
  input: "Complaint text string"
  output: "Category label"
  error_handling: >
    If complaint is empty or unclear, return 'Unclassified'