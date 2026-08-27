```python
"""
UC-0A — Complaint Classifier
"""
import argparse
import csv


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "unknown")
    description = row.get("description", "").lower()

    category = "Other"
    priority = "Low"
    reason = ""
    flag = "OK"

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing complaint description",
            "flag": "NEEDS_REVIEW"
        }

    # Category detection
    if "water" in description or "leak" in description or "pipe" in description:
        category = "Water"
        reason = "Detected water-related keywords"
    elif "garbage" in description or "waste" in description:
        category = "Sanitation"
        reason = "Detected sanitation-related keywords"
    elif "pothole" in description or "road" in description:
        category = "Roads"
        reason = "Detected road-related keywords"
    elif "electric" in description or "power" in description:
        category = "Electricity"
        reason = "Detected el
```
