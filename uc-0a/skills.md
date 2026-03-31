skills:
  - name: Complaint Text Classification
    description: Classifies complaint text into predefined categories using keyword matching.
    input: A string containing the complaint description from the CSV file.
    output: A string representing the category (Water Issue, Road Issue, Garbage Issue, Other).
    error_handling: If the input text is empty or unclear, it assigns the category as "Other".

  - name: CSV File Processing
    description: Reads complaint data from an input CSV file and writes classified results to an output CSV file.
    input: A CSV file containing complaint descriptions (rows of text data).
    output: A new CSV file with an additional "Category" column.
    error_handling: If the file is missing or unreadable, the program stops with an error message.

  - name: Keyword Detection
    description: Identifies relevant keywords in complaint text to determine the correct category.
    input: A lowercase string of complaint text.
    output: Matching keyword category decision.
    error_handling: If no keywords are found, it defaults to "Other".

  - name: Data Validation
    description: Ensures that each row has valid complaint text before classification.
    input: Raw row data from CSV.
    output: Cleaned and validated complaint text.
    error_handling: Skips invalid or empty rows and assigns "Other" if needed.