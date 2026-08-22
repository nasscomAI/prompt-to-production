skills:
  - name: document_indexer
    description: Ingests and parses municipal policy text files into searchable text chunks with filename and line tracking.
    input: Path to policy documents directory.
    output: Indexed list of document passages with metadata (filename, line number, content).
    error_handling: Skips empty or unreadable text files and logs non-fatal warnings.

  - name: grounded_query_matcher
    description: Matches citizen/employee queries against indexed policy passages using keyword relevance scoring.
    input: User query string and indexed document corpus.
    output: Top ranked matching passage with explicit source document attribution.
    error_handling: Returns a structured NOT_FOUND response when relevance score falls below threshold.

  - name: attributed_qa_responder
    description: Formats and outputs the answer alongside mandatory document citation and excerpt evidence.
    input: Matched passage dictionary and original query.
    output: Formatted string containing answer, source_document, and citation excerpt.
    error_handling: Disallows cross-document synthesis by restricting output context to the single highest-confidence document match.