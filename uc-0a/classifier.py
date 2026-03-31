"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def parse_complaint_text(raw_text: str) -> dict:
    """
    Parses raw complaint text to normalized tokens and key phrases for categorization.
    Input: string: raw complaint text (utf-8), e.g. "There is a big pothole on 5th and Main."
    Output: object with text, tokens, key_phrases
    Error handling: If input is empty or not text, return error object
    """
    if not isinstance(raw_text, str) or not raw_text.strip():
        return {
            "error": "invalid_input",
            "message": "Complaint text must be nonempty string"
        }
    
    # Normalize text: strip, lowercase for processing
    cleaned_text = raw_text.strip()
    
    # Tokenize: split on whitespace and punctuation
    tokens = re.findall(r'\b\w+\b', cleaned_text.lower())
    
    # Extract key phrases: simple approach - find sequences of words that might be relevant
    # For now, extract potential keywords from the category lists
    category_keywords = [
        "pothole", "sinkhole", "water leak", "leak", "burst pipe", "pipe burst", "water line", "sewer",
        "power outage", "no power", "electricity out", "blackout", "power cut",
        "noise", "loud", "shouting", "honking", "construction",
        "trash", "garbage", "waste", "dump", "litter",
        "streetlight", "street light", "lamp", "lamppost", "light out",
        "graffiti", "vandalism", "spray paint",
        "tree", "fallen tree", "branch", "tree damage", "roots"
    ]
    
    key_phrases = []
    text_lower = cleaned_text.lower()
    for kw in category_keywords:
        if kw in text_lower:
            key_phrases.append(kw)
    
    return {
        "text": cleaned_text,
        "tokens": tokens,
        "key_phrases": key_phrases
    }

def classify_from_parsed(parsed: dict) -> dict:
    """
    Classifies parsed complaint into category, priority, and provides explanation.
    Input: object with text, key_phrases
    Output: object with category, priority, reason, flag
    Error handling: If classification is ambiguous, set Other/Medium/NEEDS_REVIEW
    """
    if "error" in parsed:
        return {
            "category": "Other",
            "priority": "Medium",
            "reason": parsed["message"],
            "flag": "NEEDS_REVIEW"
        }
    
    text = parsed["text"]
    key_phrases = parsed["key_phrases"]
    text_lower = text.lower()
    
    category_keywords = [
        ("Pothole", ["pothole", "sinkhole"]),
        ("WaterLeak", ["water leak", "leak", "burst pipe", "pipe burst", "water line", "sewer"]),
        ("PowerOutage", ["power outage", "no power", "electricity out", "blackout", "power cut"]),
        ("Noise", ["noise", "loud", "shouting", "honking", "construction"]),
        ("TrashCollection", ["trash", "garbage", "waste", "dump", "litter"]),
        ("StreetLight", ["streetlight", "street light", "lamp", "lamppost", "light out"]),
        ("Graffiti", ["graffiti", "vandalism", "spray paint"]),
        ("TreeDamage", ["tree", "fallen tree", "branch", "tree damage", "roots"]),
    ]
    
    matched_categories = []
    for cat, keys in category_keywords:
        for kw in keys:
            if kw in text_lower:
                matched_categories.append(cat)
                break
    
    if len(matched_categories) > 1:
        return {
            "category": "Other",
            "priority": "Medium",
            "reason": "Ambiguous complaint text; matches multiple categories",
            "flag": "NEEDS_REVIEW",
        }
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
        evidence = ", ".join([kw for kw in key_phrases if kw in [k for _, ks in category_keywords for k in ks if _ == category]])
    else:
        category = "Other"
        evidence = "no clear category keywords"
    
    urgent_keywords = ["urgent", "danger", "injury", "collapse", "hazard", "fire", "ambulance", "school", "hospital"]
    high_keywords = ["broken", "blocked", "flood", "fall", "collapse", "danger"]
    
    priority = "Medium"
    if any(word in text_lower for word in urgent_keywords):
        priority = "Urgent"
    elif any(word in text_lower for word in high_keywords):
        priority = "High"
    
    if category == "Other" and evidence == "no clear category keywords":
        reason = f"No specific category keyword found in complaint text: '{text}'"
        flag = "NEEDS_REVIEW"
    else:
        reason = f"Detected keywords '{evidence}' in complaint text"
        flag = ""
    
    if category == "Other" and not flag:
        flag = "NEEDS_REVIEW"
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag

    Behavior follows agents.md + skills.md:
      - category one of: Pothole, WaterLeak, PowerOutage, Noise, TrashCollection, StreetLight, Graffiti, TreeDamage, Other
      - priority one of: Low, Medium, High, Urgent
      - reason cites text from complaint
      - ambiguous -> Other/Medium/NEEDS_REVIEW
    """

    def _normalize_text(value):
        if value is None:
            return ""
        normalized = str(value).strip()
        return normalized

    text = ""
    for key in ["complaint", "description", "text", "details"]:
        if key in row and row.get(key) is not None:
            text = _normalize_text(row.get(key))
            if text:
                break

    if not text:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Complaint text is empty or missing",
            "flag": "NEEDS_REVIEW",
        }

    # Use the skills
    parsed = parse_complaint_text(text)
    classification = classify_from_parsed(parsed)
    
    return classification


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    - flag null/empty complaint text
    - not crash on bad rows
    - output results even if some rows fail
    """

    with open(input_path, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header")

        out_fieldnames = list(reader.fieldnames) + ["category", "priority", "reason", "flag"]

        with open(output_path, "w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=out_fieldnames)
            writer.writeheader()

            for index, row in enumerate(reader, start=1):
                try:
                    classification = classify_complaint(row)
                except Exception as e:
                    classification = {
                        "category": "Other",
                        "priority": "Medium",
                        "reason": f"Error during classification: {e}",
                        "flag": "NEEDS_REVIEW",
                    }

                out_row = dict(row)
                out_row.update(classification)
                writer.writerow(out_row)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
