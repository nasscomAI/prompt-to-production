skills:
  - name: retrieve_policy
    description: Reads the CMC Employee Leave Policy text file and parses it into structured numbered sections for easier analysis.
    input: Path to the .txt policy file.
    output: A structured object (dictionary) containing sections and their corresponding text.
    error_handling: Returns an error if the file is not found or is in an unsupported format.

  - name: summarize_policy
    description: Takes structured policy sections and generates a concise summary that preserves all core obligations and multi-condition requirements.
    input: Structured policy content.
    output: A textual summary organized by clause number, strictly following RICE enforcement rules.
    error_handling: If a section is missing core data or is too ambiguous to summarize safely, it quotes the source verbatim.
