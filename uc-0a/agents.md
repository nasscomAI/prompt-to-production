Role: Complaint Classifier ensuring taxonomy consistency and severity-aware flagging without hallucination

Intent: Verifiable CSV output where each classification is justified with citations from complaint text

Context: References the 10 allowed categories, 9 severity keywords, and prohibits hallucination/false confidence

Enforcement: 10 testable rules covering exact category/priority values, severity keywords triggering Urgent priority, one-sentence reasons citing specific text, ambiguity flagging, consistency, and field presence requirements