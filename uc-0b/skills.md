# skills.md - UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    purpose: >
      Load the source .txt policy file faithfully and return its complete
      content as structured numbered sections using the original clause
      numbers.
    input:
      type: file path
      format: ".txt policy file path, specifically ../data/policy-documents/policy_hr_leave.txt"
    output:
      type: structured numbered sections
      requirements:
        - "Preserve every source section and clause number exactly as written."
        - "Preserve the complete source wording and clause content."
        - "Keep clause references such as 2.3, 2.4, 5.2, and 7.2 attached to their source text."
    expected_behavior:
      - "Read the supplied .txt file as the sole policy source."
      - "Separate the document into its original numbered sections and clauses without changing their order."
      - "Return all source content needed by summarize_policy, including conditions, actors, thresholds, deadlines, exceptions, consequences, and prohibitions."
      - "Do not paraphrase, interpret, merge, normalize, or omit source content during retrieval."
    constraints:
      - "Do not add facts, headings, clause numbers, explanations, or external policy language."
      - "Do not silently discard text that is not part of a numbered clause."
    error_handling:
      - "If the path is invalid, the file cannot be read, or the content is not a readable .txt policy, report the retrieval error rather than inventing or reconstructing policy text."

  - name: summarize_policy
    purpose: >
      Convert the structured sections returned by retrieve_policy into a
      source-faithful policy summary with checkable clause references.
    input:
      type: structured numbered policy sections
      source: retrieve_policy
    output:
      type: source-faithful summary
      destination: uc-0b/summary_hr_leave.txt
      requirements:
        - "Include every required clause reference: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2."
        - "Attach each clause's summary to its original clause number."
        - "Preserve all conditions, actors, thresholds, deadlines, exceptions, consequences, and prohibitions."
    expected_behavior:
      - "Summarize only information present in the retrieved policy sections."
      - "Preserve the binding force of must, requires, will, forfeited, and not permitted."
      - "For Clause 2.3, preserve the 14 calendar day advance requirement and Form HR-L1."
      - "For Clause 2.4, preserve written approval from the direct manager before leave commences and that verbal approval is not valid."
      - "For Clause 2.5, preserve the LOP consequence for unapproved absence regardless of subsequent approval."
      - "For Clause 2.6, preserve the maximum 5-day carry-forward, following-calendar-year scope, and 31 December forfeiture of days above 5."
      - "For Clause 2.7, preserve mandatory use during January-March of the following year and forfeiture if unused."
      - "For Clause 3.2, preserve the 3-or-more consecutive-day threshold, registered medical practitioner, and 48-hour return-to-work submission deadline."
      - "For Clause 3.4, preserve both immediately-before and immediately-after cases, public holiday and annual leave contexts, and the regardless-of-duration condition."
      - "For Clause 5.2, explicitly state that LWP requires approval from both the Department Head and the HR Director, and that manager approval alone is not sufficient."
      - "For Clause 5.3, preserve the exceeding-30-continuous-days threshold and Municipal Commissioner approval."
      - "For Clause 7.2, preserve that leave encashment during service is not permitted under any circumstances."
      - "If a clause cannot be safely summarized without meaning loss, quote that clause verbatim and flag it for review."
    constraints:
      - "Do not invent categories, procedures, legal requirements, customary practices, actors, limits, exceptions, or consequences."
      - "Do not merge clauses in a way that loses an original clause reference or condition."
      - "Do not replace binding terms with weaker language such as should, may, generally, typically, or usually."
      - "Do not use generic or external policy language that is absent from the source."
    error_handling:
      - "If a required clause is missing from the structured input, identify the missing clause rather than fabricating a summary for it."
      - "If a clause is ambiguous or unsafe to paraphrase, include its verbatim source text and an explicit review flag."
