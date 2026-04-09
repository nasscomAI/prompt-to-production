skills:
  - name: execute_python
    description: Executes Python code snippets within the uc-x project environment.
    input: Python code as a string.
    output: Execution result as a string (stdout/stderr).
    error_handling: Returns error message if code is invalid or execution fails.

  - name: search_codebase
    description: Searches the uc-x project files for a given keyword or pattern.
    input: Search query as a string.
    output: List of matching lines with file references.
    error_handling: Returns empty list if no matches; error message if query is invalid.

  - name: summarize_file
    description: Provides a summary of a specified file in the uc-x project.
    input: File path as a string.
    output: Text summary of the file's contents.
    error_handling: Returns error if file does not exist or is unreadable.
