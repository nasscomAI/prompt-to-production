# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: [skill_name]
    description: [One sentence — what does this skill do?]
    input: [What does it receive? Type and format.]
    output: [What does it return? Type and format.]
    error_handling: [What does it do when input is invalid or ambiguous?]

  - name: [second_skill_name]
    description: [One sentence]
    input: [Type and format]
    output: [Type and format]
    error_handling: [What does it do when input is invalid or ambiguous?]
  - name: detect_flooding
    description: Analyze a report and supplied image evidence for flooding or waterlogging.
    input: Natural-language description, optional location, and optional image evidence text.
    output: Location, Fault, and Situation fields.
    error_handling: Return Unknown fields when evidence is insufficient or location is missing.

  - name: extract_location
    description: Extract the place name explicitly supplied in a report.
    input: Natural-language report or explicit location value.
    output: Location string or Unknown.
    error_handling: Never infer a location that was not supplied.
