#!/usr/bin/env python3
"""
UC-0A — Complaint Classifier
Municipal complaint classification system following RICE framework
"""
import argparse
import csv
import re
from typing import Dict, List


class ComplaintClassifier:
    """
    Municipal complaint classifier that categorizes complaints and assigns priorities
    based on severity keywords and content analysis.
    """
    
    def __init__(self):
        # Exact category names as per enforcement rules
        self.categories = {
            'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 
            'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
        }
        
        # Severity keywords that trigger Urgent priority
        self.urgent_keywords = {
            'injury', 'child', 'school', 'hospital', 'ambulance', 
            'fire', 'hazard', 'fell', 'collapse'
        }
        
        # Category detection patterns
        self.category_patterns = {
            'Pothole': ['pothole', 'pot hole', 'hole in road', 'road hole'],
            'Flooding': ['flood', 'flooded', 'water logged', 'waterlogged', 'knee-deep', 'standing water'],
            'Streetlight': ['streetlight', 'street light', 'light', 'lighting', 'dark', 'flickering', 'sparking'],
            'Waste': ['garbage', 'waste', 'trash', 'overflowing', 'bins', 'smell', 'dead animal'],
            'Noise': ['noise', 'music', 'sound', 'loud', 'midnight'],
            'Road Damage': ['road', 'cracked', 'sinking', 'surface', 'broken tiles', 'upturned'],
            'Heritage Damage': ['heritage', 'old city'],
            'Heat Hazard': ['heat', 'hot'],
            'Drain Blockage': ['drain', 'blocked', 'manhole', 'cover missing']
        }
    
    def classify_complaint(self, row: dict) -> dict:
        """
        Classify a single complaint row.
        Returns: dict with keys: complaint_id, category, priority, reason, flag
        """
        complaint_id = row.get('complaint_id', '')
        description = row.get('description', '').lower()
        
        if not description.strip():
            return {
                'complaint_id': complaint_id,
                'category': 'Other',
                'priority': 'Standard',
                'reason': 'No description provided',
                'flag': 'NEEDS_REVIEW'
            }
        
        # Classify category
        category, reason_words = self._classify_category(description)
        
        # Determine priority based on severity keywords
        priority = self._classify_priority(description)
        
        # Generate reason citing specific words
        reason = self._generate_reason(description, reason_words, category)
        
        # Set flag for ambiguous cases
        flag = 'NEEDS_REVIEW' if category == 'Other' else ''
        
        return {
            'complaint_id': complaint_id,
            'category': category,
            'priority': priority,
            'reason': reason,
            'flag': flag
        }
    
    def _classify_category(self, description: str) -> tuple:
        """Classify category based on description patterns."""
        matches = []
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in description:
                    matches.append((category, pattern))
        
        if not matches:
            return 'Other', []
        
        # Return first match and the words that triggered it
        category, trigger_word = matches[0]
        return category, [trigger_word]
    
    def _classify_priority(self, description: str) -> str:
        """Classify priority based on severity keywords."""
        for keyword in self.urgent_keywords:
            if keyword in description:
                return 'Urgent'
        return 'Standard'
    
    def _generate_reason(self, description: str, trigger_words: List[str], category: str) -> str:
        """Generate reason citing specific words from description."""
        if category == 'Other':
            return "Category could not be determined from description"
        
        if trigger_words:
            return f"Contains '{trigger_words[0]}' indicating {category.lower()} issue"
        else:
            return f"Classified as {category} based on description content"
    
    def batch_classify(self, input_path: str, output_path: str):
        """
        Read input CSV, classify each row, write results CSV.
        """
        results = []
        processed_count = 0
        error_count = 0
        
        try:
            with open(input_path, 'r', newline='', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                
                for row in reader:
                    try:
                        classified = self.classify_complaint(row)
                        results.append(classified)
                        processed_count += 1
                    except Exception as e:
                        # Handle individual row errors
                        error_result = {
                            'complaint_id': row.get('complaint_id', f'ERROR_{error_count}'),
                            'category': 'Other',
                            'priority': 'Standard',
                            'reason': f'Classification error: {str(e)}',
                            'flag': 'NEEDS_REVIEW'
                        }
                        results.append(error_result)
                        error_count += 1
        
        except FileNotFoundError:
            print(f"ERROR: Input file not found: {input_path}")
            return
        except Exception as e:
            print(f"ERROR: Failed to read input file: {e}")
            return
        
        # Write output CSV
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            print(f"Classification completed:")
            print(f"- Processed: {processed_count} complaints")
            print(f"- Errors: {error_count} complaints")
            print(f"- Output written to: {output_path}")
            
        except Exception as e:
            print(f"ERROR: Failed to write output file: {e}")


def main():
    """Main entry point for the complaint classifier."""
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    classifier = ComplaintClassifier()
    classifier.batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
