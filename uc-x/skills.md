skills:
  - name: retrieve_documents
    description: >
      Loads all three CMC policy files and indexes them by document name and
      clause number, keeping each clause tied to the document it came from so
      that an answer can always be attributed to one source.
    input: >
      No arguments. Reads policy_hr_leave.txt, policy_it_acceptable_use.txt and
      policy_finance_reimbursement.txt from data/policy-documents.
    output: >
      A dict of document name to a list of clause dicts, each holding doc,
      number, section title and the full clause text with wrapped lines
      rejoined. The document name is carried on every clause; it is what makes
      the single-source rule checkable rather than aspirational.
    error_handling: >
      A continuation line appearing before any clause number is discarded
      rather than attached to the preceding clause, because text attributed to
      the wrong clause is cited to the wrong rule. A missing policy file raises
      rather than answering from the remaining two -- an assistant that
      silently drops a document will confidently refuse questions that document
      answers.

  - name: answer_question
    description: >
      Answers a staff question from exactly one policy document with clause
      citations, or returns the refusal template unchanged.
    input: >
      question -- free text. index -- the structure from retrieve_documents.
    output: >
      Either a citation block, one line per clause, in the form
      'document.txt section N.M: "clause text"', all lines from the same
      document; or the refusal template verbatim. There is no third shape.
    error_handling: >
      Refusal is returned, not an approximation, in each of these cases.
      No clause scores above the relevance floor -- the question is outside the
      documents.
      Two documents score within the margin of each other -- the question is
      genuinely ambiguous across sources, and picking one would be arbitrary
      while merging them would invent a rule that exists in neither.
      A hedging phrase would appear in the response -- a hedge is how an answer
      that is not in the documents gets delivered as though it were.
      Clause selection deliberately returns the top clause together with its
      siblings from the same section, rather than a single best guess. A rule
      and its conditions are written next to each other: returning IT 3.1
      without 3.2 gives a permission without the limit that qualifies it.
      Narrowing to exactly one clause would mean tuning score thresholds
      against the seven known test questions, which fits the retriever to the
      answer key instead of to the documents.
