# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:

    name: document_retriever
    description: "Scans all policy text files for keywords matching the user's query."
    input: "User question (string)"
    output: "List of relevant text snippets and their filenames."
    error_handling: "If no keywords match, return an empty list."

    name: policy_answer_generator
    description: "Synthesizes an answer from retrieved snippets while citing sources."
    input: "Text snippets + User question"
    output: "Natural language answer with source attribution."
    error_handling: "If snippets are contradictory, flag the answer for HR review."
