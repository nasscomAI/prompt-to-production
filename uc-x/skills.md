# skills.md

skills:
  - name: answer_policy_question
    description: Takes a user question and provides an answer based solely on the content of the policy documents, using direct quotes or the refusal template if not covered.
    input: A string containing the user's question.
    output: A string containing the answer or the refusal template.
    error_handling: If the question is ambiguous or cannot be answered from documents, respond with the refusal template; do not attempt to interpret or guess.
