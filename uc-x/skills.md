skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (HR, IT, Finance) and indexes their text strictly by document name and section number for safe context injection.
    example_invocation:
      call: `retrieve_documents(['../data/policy-documents/policy_hr_leave.txt', ...])`
      returns: `"{'policy_hr_leave.txt': '...', 'policy_it_acceptable_use.txt': '...'}"`
    input: A list of file paths corresponding to the required policy documents.
    output: An aggregate text mapping associating the absolute content of the files mapped clearly to their respective filenames.
    error_handling: System exception (FileNotFoundError) immediately if any document cannot be located or loaded.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer adhering to citations, or rigorously dumps the predefined exact refusal template.
    example_invocation:
      call: `answer_question("Can I install Slack on my work laptop?")`
      returns: `"No. According to policy_it_acceptable_use.txt (section 2.3), installing non-standard software requires written IT approval."`
    input: The employee's question block as a text string.
    output: The compliant structured answer containing the strict document name and section number citation, or the unvaried refusal string matching enforcement rule 3.
    error_handling: Default immediately and solely to the exact refusal template if there is any multi-document ambiguity or non-explicitness.
