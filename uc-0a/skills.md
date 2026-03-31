skills:
  - name: classify_complaint
    description: "Classifies a single citizen complaint to output the category, priority, reason, and flag."
    input: "A text string representing the complaint description."
    output: "A structured object containing exactly four fields (category, priority, reason, flag)."
    error_handling: "If the input is genuinely ambiguous (false confidence on ambiguity), it sets the flag to NEEDS_REVIEW. It prevents missing justification by enforcing a one-sentence reason citing exact words. It prevents taxonomy drift and hallucinated sub-categories by enforcing exact string matching against the allowed list. It prevents severity blindness by strictly forcing Urgent if any defined severity keywords are detected."
  - name: batch_classify
    description: "Reads an input CSV of complaints, applies classify_complaint per row, and writes the output CSV."
    input: "The file path to the input CSV file."
    output: "The file path to the output CSV file containing the classifications."
    error_handling: "If the input data is missing or unreadable, it aborts execution with an error. If an individual row classification fails, it assigns the Other category and sets the flag to NEEDS_REVIEW to endure graceful batch processing."
