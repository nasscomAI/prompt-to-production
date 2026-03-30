

skills:
  - name: draft_support_reply
    description: Drafts a professional and policy-safe customer support response using only the provided ticket details and approved support context.
    input: A customer support ticket as structured or plain text input, including the issue description, customer details, and any explicitly provided support notes or approved resolution guidance.
    output: A concise customer support reply in plain text that addresses the issue, states only verified information, and includes either the next approved step or a request for missing details.
    error_handling: If the ticket is incomplete, ambiguous, or lacks enough verified information for a safe resolution, return a clarification-focused holding reply instead of guessing or promising an outcome.

  - name: validate_support_reply
    description: Checks whether the drafted support response is factual, policy-safe, and limited to claims supported by the provided input.
    input: The original customer support ticket, any approved support guidance, and the drafted reply as plain text.
    output: A validated customer support reply that is safe to send and contains only supported claims, approved actions, and necessary clarification requests.
    error_handling: If the reply includes unsupported facts, unapproved promises, missing clarification requests, or speculative resolutions, remove or rewrite those portions and fall back to a safe clarification reply when needed.
