# skills.md

skills:
  - name: retrieve_documents
    description: Loads and indexes all 3 policy files into numbered sections
    input: list of file paths
    output: dict indexed by filename → list of {section_id, section_text}
    behaviour:
      - reads all 3 .txt policy files
      - splits each file into numbered sections (pattern: digit.digit)
      - stores as {filename: [{section_id, section_text}]}
      - prints how many sections loaded per document on startup
      - raises clear error if any file is missing

  - name: answer_question
    description: Searches indexed documents and returns single-source answer with citation or refusal template
    input: question (str), indexed documents (dict)
    output: answer string with citation OR refusal template string
    behaviour:
      - searches all documents for sections relevant to the question
      - if match found in exactly one document: return answer + "Source: [filename] Section [X.X]"
      - if match found in multiple documents and they conflict or combine: return refusal template
      - if no match found in any document: return refusal template exactly
      - never answer from general knowledge
      - never blend two sources
