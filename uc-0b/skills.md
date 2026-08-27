skills:
  - name: complaint_data_reader
    description: Read complaint records from a CSV file and convert them into structured data for processing.
    input: CSV file containing complaint_id and description fields.
    output: List of complaint records in dictionary format.
    error_handling: If the file is missing or unreadable, return an empty list and display an error message.

  - name: keyword_search
    description: Search complaint descriptions for a specific keyword provided by the user.
    input: Complaint records (list of dictionaries) and a keyword string.
    output: List of complaint records where the description contains the keyword.
    error_handling: If the keyword is empty or not found in any record, return an empty result and notify the user.

  - name: result_display
    description: Format and display the matching complaint records in a readable form.
    input: List of complaint records that match the search keyword.
    output: Printed output showing complaint_id and description of matching complaints.
    error_handling: If no matching records are found, display a message indicating that no complaints match the search criteria.