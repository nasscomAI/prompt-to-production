skills:

name: retrieve_policy_documents
description: Loads policy document files so they can be searched for answers.
input: No user input. Reads text files from ../data/policy-documents/.
output: Dictionary where keys are filenames and values are lists of lines from each document.
error_handling: If a file cannot be opened or read, the program prints an error and exits.

name: answer_policy_question
description: Searches the loaded policy documents and returns an answer from one document with citation.
input: User question string and dictionary of loaded documents.
output: A sentence from a document followed by the document filename as citation.
error_handling: If no relevant text is found, the function returns the refusal template instead of guessing.