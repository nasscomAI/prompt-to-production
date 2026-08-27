# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
   - name: summerize_and_categorize_leave
    description: Reads all the clauses for a category of leave and summarizes key requirement of the leaves as must requires 
    input: A dictionary of  a leave description   (string)
    output: A dictionary with keys 'Clause' (string), 'Core Obligation' (one sentence summarizing requirements for the leave including approvals, 'Binding verb' (must/requires/not permitted/will)
    error_handling: If a clause cannot be summarised without meaning loss — quote it verbatim and flag it

- name: summerize_all_leave
  description: Reads the leave detaisl from a txt file and generates a table of leae mandates
    input: A txt file of he_leaves (string)
    output: A csv file with leave categorired (string) Output written to [output_csv_path]
    error_handling:  If input file not found, raise FileNotFoundError; 
    ensure all rows are processed even if some fail.
