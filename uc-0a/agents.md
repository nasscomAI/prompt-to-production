# Complaint Classifier Agent

Role:
Classifies civic complaints into category and severity.

Intent:
Output must correctly identify complaint category and severity.

Context:
Uses only complaint text from input CSV.

Enforcement:
- Must classify using keywords
- Must assign severity based on risk words
- Must not guess randomly
- Must handle empty input safely