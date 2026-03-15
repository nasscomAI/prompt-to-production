skills:

- name: summarize_document
  description: Reads a document and generates a concise summary.
  inputs: document_text (string)
  outputs: summary (string)
  error_handling: If the input text is empty, return "No content to summarize".

- name: extract_key_points
  description: Identifies important points from the document text.
  inputs: document_text (string)
  outputs: key_points (list of strings)
  error_handling: If no key points are detected, return an empty list.