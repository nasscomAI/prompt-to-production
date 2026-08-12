#!/usr/bin/env python3
"""
UC-0A: Complaint Classifier

Classifies citizen complaints into predefined categories and priorities,
ensuring taxonomy consistency and severity-appropriate flagging.

Enforcement Rules:
- Category must be exactly one of the allowed values
- Priority must be Urgent if severity keywords are present
- Reason must cite specific words from description
- Flag must be NEEDS_REVIEW only when genuinely ambiguous
- Taxonomy drift prevention: same complaint type must have same category
"""

import argparse
import csv
import os
import sys
from typing import Dict, List


# Configuration
ALLOWED_CATEGORIES = {
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other"
}

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
}


class ClassificationError(Exception):
    """Base exception for classification errors."""
    pass


class ComplaintClassifier:
    """
    Classifier for citizen complaints with strict enforcement of taxonomy rules.
    
    Implements two skills:
    - classify_complaint: Single row classification
    - batch_classify: CSV processing with validation
    """
    
    def __init__(self):
        """Initialize the classifier and track state for taxonomy consistency."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def classify_complaint(self, description: str) -> Dict[str, str]:
        """
        SKILL: classify_complaint
        Classifies a single complaint row into category, priority, reason, and flag.
        
        Args:
            description: The complaint description text
            
        Returns:
            Dictionary with keys: category, priority, reason, flag
            
        Raises:
            ClassificationError: If classification violates enforcement rules
        """
        # ERROR HANDLING: Missing description field
        if not description or not str(description).strip():
            raise ClassificationError("Missing description field")
        
        description = str(description).strip()
        description_lower = description.lower()
        
        # Check for severity keywords
        has_severity_keyword = any(
            keyword in description_lower
            for keyword in SEVERITY_KEYWORDS
        )
        
        # ENFORCEMENT: Priority must be Urgent if severity keywords present
        if has_severity_keyword:
            priority = "Urgent"
        else:
            priority = "Standard"
        
        # Determine category based on keyword matching
        category = self._determine_category(description)
        
        # ERROR HANDLING: Hallucinated category detection
        if category not in ALLOWED_CATEGORIES:
            raise ClassificationError(
                f"Hallucinated category detected: {category}"
            )
        
        # Generate reason citing specific words from description
        reason = self._generate_reason(description, category)
        
        # ERROR HANDLING: Missing justification check
        if not self._reason_cites_description(reason, description):
            raise ClassificationError(
                "Missing justification: reason must cite complaint text"
            )
        
        # Determine if classification is ambiguous
        flag = self._check_ambiguity(description, category)
        
        return {
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }
    
    def _determine_category(self, description: str) -> str:
        """
        Determine complaint category based on keyword analysis.
        
        Args:
            description: The complaint description
            
        Returns:
            Category string from ALLOWED_CATEGORIES or "Other"
        """
        description_lower = description.lower()
        
        # Keyword rules for each category
        category_keywords = {
            "Pothole": ["pothole", "hole in", "pit", "crater", "uneven road"],
            "Flooding": ["flood", "water", "waterlogging", "inundation", "overflow"],
            "Streetlight": ["light", "streetlight", "lamp", "broken light", "no light"],
            "Waste": ["garbage", "trash", "waste", "litter", "debris", "rubbish"],
            "Noise": ["noise", "sound", "loud", "honking", "music", "loud noise"],
            "Road Damage": ["road", "pavement", "broken road", "damaged road", "cracked"],
            "Heritage Damage": ["heritage", "monument", "historical", "old building", "ancient"],
            "Heat Hazard": ["heat", "hot", "temperature", "sun exposure", "heat hazard"],
            "Drain Blockage": ["drain", "blocked", "clogged", "stagnant", "overflow"]
        }
        
        # Find matching categories (for ambiguity detection)
        matching_categories = []
        for category, keywords in category_keywords.items():
            if any(kw in description_lower for kw in keywords):
                matching_categories.append(category)
        
        # Return first match or "Other"
        return matching_categories[0] if matching_categories else "Other"
    
    def _generate_reason(self, description: str, category: str) -> str:
        """
        Generate a one-sentence reason citing specific words from description.
        
        Args:
            description: The complaint description
            category: The assigned category
            
        Returns:
            One-sentence reason with quoted text from description
        """
        # Extract key phrase from description (first meaningful segment)
        words = description.split()
        
        if len(words) <= 10:
            phrase = description
        else:
            # Take up to first 12 words
            phrase = " ".join(words[:12]) + "..."
        
        # Create reason that cites the actual text
        reason = f"Classified as {category}: \"{phrase}\""
        
        return reason
    
    def _reason_cites_description(self, reason: str, description: str) -> bool:
        """
        Check if reason cites specific words from description.
        
        Args:
            reason: The generated reason
            description: The original description
            
        Returns:
            True if reason contains words from description, False otherwise
        """
        reason_lower = reason.lower()
        description_words = description.lower().split()
        
        # Check if at least 2 significant words from description appear in reason
        cited_words = 0
        for word in description_words:
            if len(word) > 3 and word in reason_lower:  # Ignore small words
                cited_words += 1
        
        return cited_words >= 2 or len(description) < 10
    
    def _check_ambiguity(self, description: str, assigned_category: str) -> str:
        """
        Check if classification is ambiguous and should be flagged for review.
        
        ENFORCEMENT: Flag as NEEDS_REVIEW when category assignment is genuinely ambiguous
        
        Args:
            description: The complaint description
            assigned_category: The assigned category
            
        Returns:
            "NEEDS_REVIEW" if ambiguous, empty string otherwise
        """
        description_lower = description.lower()
        
        category_keywords = {
            "Pothole": ["pothole", "hole", "pit", "uneven"],
            "Flooding": ["flood", "water", "waterlog"],
            "Streetlight": ["light", "lamp", "dark"],
            "Waste": ["garbage", "trash", "waste", "litter"],
            "Noise": ["noise", "sound", "loud"],
            "Road Damage": ["road", "pavement", "broken", "damaged", "crack"],
            "Heritage Damage": ["heritage", "monument", "historical"],
            "Heat Hazard": ["heat", "hot", "temperature"],
            "Drain Blockage": ["drain", "blocked", "clog", "stagnant"]
        }
        
        # Count how many categories match
        matching_count = 0
        for category, keywords in category_keywords.items():
            if any(kw in description_lower for kw in keywords):
                matching_count += 1
        
        # If multiple categories could apply, it's ambiguous
        if matching_count >= 2:
            return "NEEDS_REVIEW"
        
        # Check for explicit uncertainty language
        uncertainty_words = ["unclear", "might be", "could be", "seems", "appears to be"]
        if any(word in description_lower for word in uncertainty_words):
            return "NEEDS_REVIEW"
        
        return ""
    
    def batch_classify(self, input_path: str, output_path: str) -> None:
        """
        SKILL: batch_classify
        Reads input CSV, applies classify_complaint to each row, writes output CSV.
        
        Args:
            input_path: Path to input CSV file
            output_path: Path to output CSV file
            
        Raises:
            ClassificationError: If input validation or output validation fails
        """
        # ERROR HANDLING: Input file not found
        if not os.path.exists(input_path):
            raise ClassificationError(f"Input file not found: {input_path}")
        
        # Read input CSV
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                input_rows = list(reader)
        except Exception as e:
            raise ClassificationError(f"Error reading input file: {e}")
        
        if not input_rows:
            raise ClassificationError("Input file is empty")
        
        # ERROR HANDLING: Check for required description column
        if 'description' not in input_rows[0]:
            raise ClassificationError("Required column missing: description")
        
        # Classify each row
        output_rows = []
        for row_num, row in enumerate(input_rows, 1):
            try:
                classification = self.classify_complaint(row['description'])
                output_row = dict(row)
                output_row.update(classification)
                output_rows.append(output_row)
            except ClassificationError as e:
                # ERROR HANDLING: Log error, skip row, continue processing
                error_msg = f"Row {row_num}: {str(e)}"
                self.errors.append(error_msg)
                print(f"Warning: {error_msg}", file=sys.stderr)
        
        if not output_rows:
            raise ClassificationError(
                "No valid classifications produced - all rows failed"
            )
        
        # ENFORCEMENT: Validate all rows after processing
        validation_errors = self._validate_all_classifications(
            output_rows, input_rows
        )
        
        if validation_errors:
            error_summary = (
                f"Validation failed with {len(validation_errors)} error(s):\n" +
                "\n".join(validation_errors)
            )
            raise ClassificationError(error_summary)
        
        # ERROR HANDLING: Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                raise ClassificationError(
                    f"Failed to create output directory: {e}"
                )
        
        # Write output CSV
        try:
            fieldnames = list(output_rows[0].keys())
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(output_rows)
        except Exception as e:
            raise ClassificationError(f"Error writing output file: {e}")
    
    def _validate_all_classifications(self, output_rows: List[Dict],
                                     input_rows: List[Dict]) -> List[str]:
        """
        Validate all classifications for consistency and correctness.
        
        ENFORCEMENT CHECKS:
        - All categories must be in allowed list (no hallucination)
        - All priorities must be in allowed list
        - Severity keywords must trigger Urgent priority
        - Reasons must cite complaint text
        - Categories must be consistent (no taxonomy drift)
        
        Args:
            output_rows: List of classified rows with output fields
            input_rows: List of original input rows
            
        Returns:
            List of validation error messages (empty if valid)
        """
        validation_errors = []
        
        # Track category assignments for taxonomy drift detection
        category_patterns: Dict[str, str] = {}  # description_signature -> category
        
        for idx, row in enumerate(output_rows):
            description = input_rows[idx]['description']
            description_lower = str(description).lower()
            
            # ENFORCEMENT: Category must be in allowed list
            category = row.get('category', '')
            if category not in ALLOWED_CATEGORIES:
                validation_errors.append(
                    f"Row {idx+1}: Hallucinated category '{category}'"
                )
            
            # ENFORCEMENT: Priority must be in allowed list
            priority = row.get('priority', '')
            if priority not in ALLOWED_PRIORITIES:
                validation_errors.append(
                    f"Row {idx+1}: Invalid priority '{priority}'"
                )
            
            # ENFORCEMENT: Severity keywords must trigger Urgent priority
            has_severity = any(
                kw in description_lower for kw in SEVERITY_KEYWORDS
            )
            if has_severity and priority != "Urgent":
                validation_errors.append(
                    f"Row {idx+1}: Severity blindness - contains severity keyword "
                    f"but priority is '{priority}' (must be Urgent)"
                )
            
            # ENFORCEMENT: Reason must cite specific words from description
            reason = row.get('reason', '')
            if reason and not self._reason_cites_description(reason, description):
                validation_errors.append(
                    f"Row {idx+1}: Reason does not cite complaint text"
                )
            
            # ENFORCEMENT: Track categories for taxonomy drift
            # Create a pattern signature (first meaningful words)
            desc_words = description_lower.split()[:5]
            desc_pattern = " ".join(desc_words)
            
            if desc_pattern in category_patterns:
                if category_patterns[desc_pattern] != category:
                    validation_errors.append(
                        f"Row {idx+1}: Taxonomy drift - similar complaint "
                        f"previously classified as '{category_patterns[desc_pattern]}' "
                        f"but now classified as '{category}'"
                    )
            else:
                category_patterns[desc_pattern] = category
        
        return validation_errors


def main():
    """Main entry point for the complaint classifier."""
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    try:
        classifier = ComplaintClassifier()
        classifier.batch_classify(args.input, args.output)
        print(f"✓ Done. Results written to {args.output}")
        return 0
    except ClassificationError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
