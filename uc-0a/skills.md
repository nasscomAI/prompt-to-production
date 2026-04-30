skills:
    name: [classify_complaint]
    description: [Analyzes a single citizen complaint text and extracts the corresponding category, priority, reason, and ambiguity flag]
    input: [type: string format: unstructured text description of a single citizen complaint.]
    output: [ype: object format: dictionary with exactly four keys (category, priority, reason, flag) strictly conforming to the schema.]
    error_handling: [ If input is ambiguous, it sets the flag to NEEDS_REVIEW to avoid false confidence; if input matches severity blindness failure modes, it forces priority to Urgent based on keywords; if input induces taxonomy drift or hallucination, it rejects variations and forces exact string matching to the allowed categories.]

    name: [batch_classify]
    description: [Reads an input CSV file of complaints, iterates over each row using the classify_complaint skill, and writes the structured results to an output CSV file.]
    input: [type: file format: CSV file path containing a list of citizen complaints]
    output: [type: file format: CSV file path identical to the input but with fully populated category, priority, reason, and flag columns]
    error_handling: [If the input file is invalid or unreadable, it halts execution and throws an error; if an individual row causes a classification failure or is completely invalid, it falls back to the Other category and flags it as NEEDS_REVIEW to prevent the entire batch operation from failing.]
