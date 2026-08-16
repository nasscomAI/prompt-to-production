# skills.md - UC-0A Complaint Classifier

skills:
  - name: read_csv
    description: >
      Ability to read citizen complaints from data/city-test-files/test_pune.csv (handling any missing or malformed rows gracefully).
  
  - name: call_llm
    description: >
      Ability to pass each complaint description to an LLM using the rules defined in agents.md to get structured classification data.
      
  - name: write_csv
    description: >
      Ability to write the classified output (category, priority, reason, flag) to a new file named results_pune.csv inside the uc-0a folder.