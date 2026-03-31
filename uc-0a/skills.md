skills:
  - name: classify_complaint
    description: Receives a single complaint row and outputs the classified category, priority, justification reason, and an ambiguity flag.
    input: An object or string representing one row of citizen complaint text.
    output: An object or dictionary with four fields (category, priority, reason, flag).
    error_handling: Refuses to hallucinate sub-categories by strictly outputting "Other" if the category is not exactly in the allowed list, sets priority to "Urgent" if severity keywords are present, ensures the reason cites specific words, and sets the flag to "NEEDS_REVIEW" if the text is genuinely ambiguous or lacks clarity for confident classification.
  - name: batch_classify
    description: Reads the input CSV file, applies the characterize_complaint skill recursively to each row, and aggregates the results into a file.
    input: The file path to the input CSV containing complaints without category and priority columns.
    output: A newly written output CSV file with identical rows plus the newly generated category, priority, reason, and flag columns.
    error_handling: Handles empty or malformed rows by leaving priority and category blank or "Other", and sets the flag to "NEEDS_REVIEW", ensuring varying descriptions do not break the row structure.
