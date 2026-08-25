skills:
  - name: classify_complaint
    description: "Takes one complaint row and returns category, priority, reason, and flag."
    input: "a single citizen complaint record containing description and location text"
    output: "4 strictly mapped fields: category, priority, reason, flag"
    error_handling: "If the category is genuinely ambiguous, refuse to confidently guess and set the flag to 'NEEDS_REVIEW'."

  - name: batch_classify
    description: "reads input CSV, applies classify_complaint per row, writes output CSV"
    input: "CSV dataset of unclassified complaints"
    output: "A new CSV strictly mirroring the input with the new classification fields appended safely."
    error_handling: "If a row is corrupted or empty, insert 'ERROR' in classification fields and safely proceed."
