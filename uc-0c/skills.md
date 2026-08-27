skills:
  - name: csv_data_reader
    description: Read classified complaint data from a CSV file and convert it into structured records.
    input: CSV file containing complaint_id, category, priority, reason, and flag fields.
    output: List of complaint records stored as dictionaries.
    error_handling: If the file cannot be found or read, return an empty dataset and display an error message.

  - name: category_summary_generator
    description: Count and summarize the number of complaints for each category.
    input: List of complaint records containing a category field.
    output: Dictionary mapping each category to its complaint count.
    error_handling: If category data is missing in a record, classify it under "Unknown".

  - name: priority_summary_generator
    description: Count and summarize the number of complaints based on priority levels.
    input: List of complaint records containing a priority field.
    output: Dictionary mapping each priority level to its complaint count.
    error_handling: If priority data is missing or invalid, classify it under "Unknown".

  - name: summary_report_display
    description: Display the complaint summary statistics in a readable format.
    input: Category summary and priority summary dictionaries.
    output: Printed report showing counts of complaints by category and priority.
    error_handling: If the summaries are empty, display a message indicating that no complaint data is available.