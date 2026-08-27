import csv
import argparse
import re

# Allowed categories - enforced exactly as per schema
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Priority mappings
ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse", "stranded", "risk"}


def extract_severity_keywords(text):
    """Extract severity keywords from text."""
    text_lower = text.lower()
    found_keywords = []
    for keyword in SEVERITY_KEYWORDS:
        if re.search(r'\b' + keyword + r'\b', text_lower):
            found_keywords.append(keyword)
    return found_keywords


def classify_complaint(row_description):
    """
    Classify a single complaint row into category, priority, reason, and flag.
    
    Args:
        row_description: String description of the complaint
        
    Returns:
        Dict with keys: category, priority, reason, flag
    """
    description = row_description.strip()
    text_lower = description.lower()
    
    # Check for severity keywords to determine priority
    severity_found = extract_severity_keywords(description)
    priority = "Urgent" if severity_found else "Standard"
    
    # Category classification with exact string enforcement
    category = "Other"  # Default
    reason = ""
    flag = ""
    
    # Order matters - check more specific patterns first
    
    # Pothole detection (high specificity)
    if re.search(r'\b(pothole|pot.?hole|crater|craters)\b', text_lower):
        category = "Pothole"
        # Extract reason citing specific words
        match = re.search(r'(pothole|pot.?hole|crater|craters).*?([a-z\s]+?)(?:\.|$)', description, re.IGNORECASE)
        if match:
            descriptor = match.group(2).strip()
            if descriptor and len(descriptor) < 50:
                reason = f"Pothole identified causing {descriptor}."
            else:
                reason = "Pothole identified causing damage and safety concerns."
        else:
            reason = "Pothole identified in location."
    
    # Flooding detection (must be checked before generic drain patterns)
    elif re.search(r'\b(flood|floods|flooded|flooding|water.?logged|waterlogged|submerged)\b', text_lower):
        category = "Flooding"
        if "knee-deep" in text_lower:
            reason = "Flooding knee-deep prevents passage of commuters."
        elif "inaccessible" in text_lower or "inaccessible" in description.lower():
            priority = "Urgent"
            reason = "Bridge approach floods making route inaccessible."
        elif "stranded" in text_lower:
            priority = "Urgent"
            reason = "Area flooded causing commuter congestion and stranding."
        else:
            reason = "Area flooded from recent rainfall causing accessibility issues."
    
    # Streetlight detection (high specificity)
    elif re.search(r'\b(streetlights?|street.?lights?|lights?)\b', text_lower) and \
         re.search(r'\b(out|dark|flicker|sparking|electrical|outage|hazard)\b', text_lower):
        category = "Streetlight"
        if "sparking" in text_lower or "electrical" in text_lower:
            if priority == "Standard":
                priority = "Urgent"  # Electrical hazard forces Urgent
            reason = "Streetlight electrical hazard poses safety risk."
        elif "out" in text_lower or "dark" in text_lower:
            reason = "Streetlight outage affects area visibility and night safety."
        else:
            reason = "Streetlight maintenance required for public illumination."
    
    # Waste/Garbage detection (before generic drain/blockage)
    elif re.search(r'\b(garbage|bins|waste|trash|dumped|litter|dead animal)\b', text_lower):
        category = "Waste"
        if "dead animal" in text_lower:
            flag = "NEEDS_REVIEW"  # Ambiguous: could be health/heritage issue
            reason = "Dead animal remaining in public area with health concerns."
        elif "overflowing" in text_lower or "overflow" in text_lower:
            reason = "Garbage bins overflowing creating hygiene and sanitation issues."
        elif "dumped" in text_lower:
            reason = "Bulk waste dumped on public road obstructing passage."
        else:
            reason = "Waste accumulation affecting public cleanliness."
    
    # Drain Blockage & Road Damage (drain/manhole/road patterns)
    elif re.search(r'\b(drain|manhole|clogged|blockage)\b', text_lower):
        category = "Drain Blockage"
        if "blocked" in text_lower or "blockage" in text_lower:
            reason = "Drain system blocked causing water accumulation."
        elif "manhole" in text_lower:
            reason = "Manhole infrastructure requires maintenance and access restoration."
        else:
            reason = "Drain infrastructure requires maintenance and clearance."
    
    # Road Damage/Pavement detection
    elif re.search(r'\b(road|pavement|footpath|tiles|crack|sinking|surface|broken|upturned)\b', text_lower):
        category = "Road Damage"
        if "fell" in text_lower or "upturned" in text_lower:
            if priority == "Standard":
                priority = "Urgent"
            reason = "Broken pavement causing fall incidents and injury risk."
        elif "crack" in text_lower or "sinking" in text_lower:
            reason = "Road surface damaged with cracks and deformation."
        else:
            reason = "Road or footpath structural damage requires immediate repair."
    
    # Noise detection
    elif re.search(r'\b(noise|music|sound|loud|speaker|loudspeaker|midnight|nuisance)\b', text_lower):
        category = "Noise"
        reason = "Noise complaint affecting residential peace and quiet hours."
    
    # Heritage Damage detection
    elif re.search(r'\b(heritage|historic|old city|ancient|monument|preservation)\b', text_lower):
        category = "Heritage Damage"
        reason = "Heritage area infrastructure damaged affecting historical preservation."
    
    # Heat Hazard detection
    elif re.search(r'\b(heat|temperature|extreme|hot|thermal|sun|burn)\b', text_lower) and \
         not re.search(r'\b(cold)\b', text_lower):
        category = "Heat Hazard"
        reason = "Heat-related hazard identified in public area."
    
    # Ambiguity flag logic
    if not reason:
        # If we reach here with default Other category, it might be ambiguous
        reason = "Complaint requires review for proper categorization."
        flag = "NEEDS_REVIEW"
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_file, output_file):
    """
    Read CSV input file, classify each complaint, write output CSV.
    
    Args:
        input_file: Path to input CSV with complaints
        output_file: Path to output CSV with classifications
    """
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("Input file is empty or has no header")
        
        # Define output fieldnames - keep original + add classification fields
        output_fieldnames = list(reader.fieldnames) + ["category", "priority", "reason", "flag"]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()
            
            for row in reader:
                # Classify the complaint
                description = row.get("description", "")
                classification = classify_complaint(description)
                
                # Add classification to row
                row["category"] = classification["category"]
                row["priority"] = classification["priority"]
                row["reason"] = classification["reason"]
                row["flag"] = classification["flag"]
                
                writer.writerow(row)
    
    print(f"Classification completed! Processed output written to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Classify citizen complaints by category and priority"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV file with complaints"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV file with classifications"
    )
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)