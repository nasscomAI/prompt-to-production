skills:
*  name: retrieve_policy
   description: Loads the .txt policy file and returns its content as structured numbered sections.
   input: File path to the source .txt document (String).
   output: The content of the policy document mapped into structured numbered sections (List of objects).
   error_handling: Halt execution and return an error message if the input file path is invalid, missing, or improperly formatted.

*  name: summarize_policy
   description: Takes the structured sections and produces a compliant summary with exact clause references.
   input: The structured numbered sections (List of objects).
   output: A comprehensive, compliant summary document with exact clause references (String).
   error_handling: Refuse to summarize ambiguous clauses, defaulting to quoting them verbatim and flagging the risk of meaning loss.