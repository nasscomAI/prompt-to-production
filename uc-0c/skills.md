UC-0C Skills

skills:

- name: answer_policy_question
  description: Reads a policy document and answers questions based on the content.
  inputs: policy_text (string), question (string)
  outputs: answer (string)
  error_handling: If the answer cannot be found, return "Answer not found in policy".

- name: extract_relevant_section
  description: Finds the relevant section in the policy that relates to the question.
  inputs: policy_text (string), question (string)
  outputs: relevant_section (string)
  error_handling: If no section matches the question, return an empty string.