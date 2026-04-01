# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Opens and reads multiple policy `.txt` files into indexed memory so logic limits can correctly parse section numbers against explicit questions without blending them.
    input: List of specific absolute or relative directory filepaths pointing to the target .txt policy files.
    output: A dictionary object securely compartmentalizing file name as key and distinct section numbering text blocks as mapped string value references.
    error_handling: Notifies the CLI runner if a specific configuration document fails to load, gracefully continuing with what was recovered without panicking.

  - name: answer_question
    description: Executes a highly precise match check resolving strict answers and mandated templates based on question parameters independently targeting single policy sources.
    input: Question string (str) from an interactive CLI prompt alongside indexed policy contents.
    output: A rigorous string containing an unapologetic, condition-present answer and its exact source citation — OR the identical mandated refusal template for out-of-bounds or cross-document trap queries.
    error_handling: Handles unrecognized or blended questions strictly by dumping the mandated exact refusal block string without variation.
