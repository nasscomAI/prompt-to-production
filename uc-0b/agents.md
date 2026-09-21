role: >
  Summarize the supplied HR leave policy using only its source text and
  preserve every binding obligation and condition.

intent: >
  Produce a verifiable summary containing all ten required clause references,
  their obligations, and the exact conditions, limits, approvers, and dates.

context: >
  The only allowed source is the input policy .txt file. Do not add common
  practice, legal interpretation, assumptions, or information from outside
  the source document.

enforcement:
  - "Every required numbered clause 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2 must be present"
  - "Multi-condition obligations must preserve every condition and must never silently drop an approver, deadline, threshold, exception, or forfeiture rule"
  - "Never add information not present in the source document"
  - "If a clause cannot be summarized without meaning loss, quote it verbatim and mark it as verbatim"
