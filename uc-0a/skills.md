# Complaint Classifier Skills

- `classify_complaint(description: str) -> dict`: Evaluates a single complaint description and returns its category, priority, reason, and flag. It uses keyword-based urgency detection and specific category mapping.
- `batch_classify(input_file: str, output_file: str)`: Reads a CSV file of complaints, iterates through each complaint, and writes the classified results to a new CSV file.
