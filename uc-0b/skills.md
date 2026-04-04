# skills.md

skills:
  - name: retrieve_policy
    description: Opens and loads the raw .txt text of the HR policy document, parsing it into a string format.
    input: absolute or relative file path to the text document.
    output: structured text block or array of strings representing the document content.
    error_handling: Return error if file doesn't exist or cannot be read.

  - name: summarize_policy
    description: Condenses the retrieved policy text into a highly strict summary that retains every numbered clause explicitly without scope bleed.
    input: the retrieved policy string text.
    output: a text summary ensuring every X.Y clause is represented perfectly with all conditions intact.
    error_handling: If document structure is unreadable, output an exact copy of the raw text so zero conditions are dropped.
