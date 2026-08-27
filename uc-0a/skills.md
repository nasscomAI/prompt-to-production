- Categorization: Ability to assign each complaint to one of the predefined categories: Pothole, Water Leakage, Garbage, Streetlight, Flooding, or Other.

- Priority Detection: Detects urgent issues by scanning complaint descriptions for keywords like "injury," "child," "hospital," and "school," and marks those complaints with high priority.

- Reason Extraction: Extracts and cites specific keywords or phrases from the complaint description to explain the category and priority assigned.

- Refusal Handling: Flags complaints as NEEDS_REVIEW when the category cannot be confidently determined from the description alone.

- Data Usage: Operates only on complaint description and location fields, ignoring personal information and timestamps to maintain privacy.

- Error Handling: Gracefully handles missing or malformed complaint descriptions by assigning the category Other and flagging for review.
