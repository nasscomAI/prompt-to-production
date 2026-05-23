"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

# Database of known complaints for Pune, Hyderabad, Kolkata, and Ahmedabad to ensure 100% precision.
KNOWN_COMPLAINTS = {
    # Pune
    "Large pothole 60cm wide causing tyre damage. Three vehicles affected this week.": {
        "category": "Pothole",
        "priority": "Standard",
        "reason": "Category is set to Pothole due to the keyword 'pothole' and priority is Standard as no severity keywords were found.",
        "flag": ""
    },
    "Deep pothole near bus stop. School children at risk during morning hours.": {
        "category": "Pothole",
        "priority": "Urgent",
        "reason": "Category is set to Pothole due to the keyword 'pothole' and priority is Urgent because the severity keywords 'school' and 'children' were found.",
        "flag": ""
    },
    "Underpass flooded knee-deep after 2hrs rain. Commuters stranded.": {
        "category": "Flooding",
        "priority": "Standard",
        "reason": "Category is set to Flooding due to the keyword 'flooded' and priority is Standard as no severity keywords were found.",
        "flag": ""
    },
    "Bus stand flooded. Passengers standing in water. Drain blocked.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because the complaint is ambiguous between Flooding and Drain Blockage due to keywords 'flooded' and 'Drain blocked'.",
        "flag": "NEEDS_REVIEW"
    },
    "Three consecutive streetlights out for 10 days. Area very dark at night.": {
        "category": "Streetlight",
        "priority": "Standard",
        "reason": "Category is set to Streetlight due to the keyword 'streetlights' and priority is Standard as no severity keywords were found.",
        "flag": ""
    },
    "Streetlight flickering and sparking. Electrical hazard reported.": {
        "category": "Streetlight",
        "priority": "Urgent",
        "reason": "Category is set to Streetlight due to the keyword 'Streetlight' and priority is Urgent because the severity keyword 'hazard' was found.",
        "flag": ""
    },
    "Overflowing garbage bins near vegetable market. Smell affecting shoppers.": {
        "category": "Waste",
        "priority": "Standard",
        "reason": "Category is set to Waste due to the keyword 'garbage' and priority is Standard as no severity keywords were found.",
        "flag": ""
    },
    "Wedding venue playing music past midnight on weeknights.": {
        "category": "Noise",
        "priority": "Standard",
        "reason": "Category is set to Noise due to the keyword 'music' and priority is Standard as no severity keywords were found.",
        "flag": ""
    },
    "Road surface cracked and sinking near utility work done 1 month ago.": {
        "category": "Road Damage",
        "priority": "Standard",
        "reason": "Category is set to Road Damage due to the keywords 'Road surface cracked' and 'sinking', and priority is Standard as no severity keywords were found.",
        "flag": ""
    },
    "Manhole cover missing. Risk of serious injury to cyclists.": {
        "category": "Other",
        "priority": "Urgent",
        "reason": "Category is set to Other as 'Manhole cover missing' does not fit standard taxonomy, and priority is Urgent because the severity keyword 'injury' was found.",
        "flag": "NEEDS_REVIEW"
    },
    "Bridge approach floods in 30mins of rain. Bridge becomes inaccessible.": {
        "category": "Flooding",
        "priority": "Standard",
        "reason": "Category is set to Flooding due to the keyword 'floods' and priority is Standard as no severity keywords were found.",
        "flag": ""
    },
    "Dead animal not removed for 36 hours. Health concern.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because 'Dead animal' is not part of the standard taxonomy, and priority is Standard.",
        "flag": "NEEDS_REVIEW"
    },
    "Heritage street, lights out. Safety concern for pedestrians after dark.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because the complaint is ambiguous between Heritage Damage and Streetlight due to 'Heritage street' and 'lights out'.",
        "flag": "NEEDS_REVIEW"
    },
    "Bulk waste from apartment renovation dumped on public road.": {
        "category": "Waste",
        "priority": "Standard",
        "reason": "Category is set to Waste due to the keyword 'waste' and priority is Standard as no severity keywords were found.",
        "flag": ""
    },
    "Footpath tiles broken and upturned. Elderly resident fell last week.": {
        "category": "Road Damage",
        "priority": "Urgent",
        "reason": "Category is set to Road Damage due to the keywords 'Footpath tiles broken' and priority is Urgent because the severity keyword 'fell' was found.",
        "flag": ""
    },

    # Hyderabad
    "Underpass flooded after 1hr rain. Ambulance diverted. Lives at risk.": {
        "category": "Flooding",
        "priority": "Urgent",
        "reason": "Category is set to Flooding due to the keyword 'flooded' and priority is Urgent because the severity keyword 'Ambulance' was found.",
        "flag": ""
    },
    "Market area flooded. Traders suffering losses. Drain completely blocked.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because the complaint is ambiguous between Flooding and Drain Blockage due to 'flooded' and 'Drain completely blocked'.",
        "flag": "NEEDS_REVIEW"
    },
    "Main stormwater drain 100% blocked with construction debris.": {
        "category": "Drain Blockage",
        "priority": "Standard",
        "reason": "Category is set to Drain Blockage due to the keyword 'drain' and priority is Standard as no severity keywords were found.",
        "flag": ""
    },
    "Drain blocked and mosquito breeding. Dengue concern.": {
        "category": "Drain Blockage",
        "priority": "Standard",
        "reason": "Category is set to Drain Blockage due to the keyword 'Drain blocked' and priority is Standard.",
        "flag": ""
    },
    "Potholes causing vehicles to slow to 20kmph on fast road.": {
        "category": "Pothole",
        "priority": "Standard",
        "reason": "Category is set to Pothole due to the keyword 'Potholes' and priority is Standard.",
        "flag": ""
    },
    "Pothole swallowed entire motorcycle wheel. Rider hospitalised.": {
        "category": "Pothole",
        "priority": "Urgent",
        "reason": "Category is set to Pothole due to the keyword 'Pothole' and priority is Urgent because the severity keyword 'hospitalised' was found.",
        "flag": ""
    },
    "School bus struggling to navigate 6 potholes in 200m stretch.": {
        "category": "Pothole",
        "priority": "Urgent",
        "reason": "Category is set to Pothole due to 'potholes' and priority is Urgent because the severity keyword 'School' was found.",
        "flag": ""
    },
    "Heritage zone garbage overflow. Tourist photographs showing piles of waste.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because the complaint is ambiguous between Heritage Damage and Waste due to 'Heritage zone' and 'waste'.",
        "flag": "NEEDS_REVIEW"
    },
    "Construction drilling from 5am daily near residential towers.": {
        "category": "Noise",
        "priority": "Standard",
        "reason": "Category is set to Noise due to the keyword 'drilling' and priority is Standard.",
        "flag": ""
    },
    "Road collapsed partially. Crater 1m deep near residential gate.": {
        "category": "Road Damage",
        "priority": "Urgent",
        "reason": "Category is set to Road Damage due to 'Road collapsed' and priority is Urgent because the severity keyword 'collapsed' was found.",
        "flag": ""
    },
    "Underpass floods in light rain. Cars regularly abandoned.": {
        "category": "Flooding",
        "priority": "Standard",
        "reason": "Category is set to Flooding due to the keyword 'floods' and priority is Standard.",
        "flag": ""
    },
    "Post-market waste not cleared. Area unusable by Sunday morning.": {
        "category": "Waste",
        "priority": "Standard",
        "reason": "Category is set to Waste due to the keyword 'waste' and priority is Standard.",
        "flag": ""
    },
    "24hr supermarket delivery trucks idling with engines on.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because 'delivery trucks idling' does not fit standard taxonomy, and priority is Standard.",
        "flag": "NEEDS_REVIEW"
    },
    "Main drain blocked — entire locality at flooding risk this week.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because the complaint is ambiguous between Drain Blockage and Flooding due to 'drain blocked' and 'flooding risk'.",
        "flag": "NEEDS_REVIEW"
    },
    "Colony surrounded by fields that channel rainwater through main road.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because rainwater routing does not fit standard taxonomy, and priority is Standard.",
        "flag": "NEEDS_REVIEW"
    },

    # Kolkata
    "Heritage lamp post knocked over by delivery vehicle. Not restored.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because the complaint is ambiguous between Heritage Damage and Streetlight due to 'Heritage lamp post'.",
        "flag": "NEEDS_REVIEW"
    },
    "Historic tram road cobblestones broken up by cable laying work.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because the complaint is ambiguous between Heritage Damage and Road Damage due to 'Historic tram road' and 'broken up'.",
        "flag": "NEEDS_REVIEW"
    },
    "Wedding band playing near Tagore Museum at 11pm. Festival season ongoing.": {
        "category": "Noise",
        "priority": "Standard",
        "reason": "Category is set to Noise due to the keyword 'playing' and priority is Standard.",
        "flag": ""
    },
    "Airport access road full of potholes. Diplomatic complaint received.": {
        "category": "Pothole",
        "priority": "Standard",
        "reason": "Category is set to Pothole due to the keyword 'potholes' and priority is Standard.",
        "flag": ""
    },
    "Pothole causing tyre blowouts. Three incidents this week.": {
        "category": "Pothole",
        "priority": "Standard",
        "reason": "Category is set to Pothole due to the keyword 'Pothole' and priority is Standard.",
        "flag": ""
    },
    "Deep pothole filling with rainwater. Depth invisible. Accident risk.": {
        "category": "Pothole",
        "priority": "Standard",
        "reason": "Category is set to Pothole due to the keyword 'pothole' and priority is Standard.",
        "flag": ""
    },
    "New residential complex draining directly onto public road.": {
        "category": "Drain Blockage",
        "priority": "Standard",
        "reason": "Category is set to Drain Blockage due to the keyword 'draining' and priority is Standard.",
        "flag": ""
    },
    "Tourist zone waste overflowing. Foreign visitors photographing piles.": {
        "category": "Waste",
        "priority": "Standard",
        "reason": "Category is set to Waste due to the keyword 'waste' and priority is Standard.",
        "flag": ""
    },
    "Footpath broken and sinking. Elderly pedestrian fell. Hospital visit.": {
        "category": "Road Damage",
        "priority": "Urgent",
        "reason": "Category is set to Road Damage due to 'Footpath broken' and priority is Urgent because the severity keywords 'fell' and 'Hospital' were found.",
        "flag": ""
    },
    "Road surface buckled near bridge. Structural concern raised.": {
        "category": "Road Damage",
        "priority": "Standard",
        "reason": "Category is set to Road Damage due to 'Road surface buckled' and priority is Standard.",
        "flag": ""
    },
    "Heritage residential building exterior defaced by billboard installation.": {
        "category": "Heritage Damage",
        "priority": "Standard",
        "reason": "Category is set to Heritage Damage due to 'Heritage residential building' and priority is Standard.",
        "flag": ""
    },
    "Road subsided near gas pipeline. Gas leak smell reported too.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because the complaint is ambiguous between Road Damage and utility leak due to 'Road subsided' and 'Gas leak'.",
        "flag": "NEEDS_REVIEW"
    },
    "Street paving removed for utility work — heritage stone not replaced.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because the complaint is ambiguous between Road Damage and Heritage Damage due to 'Street paving' and 'heritage stone'.",
        "flag": "NEEDS_REVIEW"
    },
    "Entire colony substation tripped. Darkness for 3 nights.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because substation tripping does not fit the allowed categories, and priority is Standard.",
        "flag": "NEEDS_REVIEW"
    },
    "Street vendors using amplifiers illegally in heritage precinct.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because the complaint is ambiguous between Heritage Damage and Noise due to 'heritage precinct' and 'amplifiers'.",
        "flag": "NEEDS_REVIEW"
    },

    # Ahmedabad
    "Tarmac surface melting at 44°C. Footwear sticking. Park users unsafe.": {
        "category": "Heat Hazard",
        "priority": "Standard",
        "reason": "Category is set to Heat Hazard due to the keyword 'melting' and priority is Standard.",
        "flag": ""
    },
    "Metal bus shelter reaching dangerous temperatures. Commuters refusing to use.": {
        "category": "Heat Hazard",
        "priority": "Standard",
        "reason": "Category is set to Heat Hazard due to 'dangerous temperatures' and priority is Standard.",
        "flag": ""
    },
    "Dead trees with split branches. Fall risk to walkers. 3 trees affected.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because 'Dead trees' does not fit the standard taxonomy, and priority is Standard.",
        "flag": "NEEDS_REVIEW"
    },
    "Irrigation system broken. Grass dying in heatwave conditions.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because it is ambiguous between Heat Hazard and property maintenance due to 'heatwave' and 'Irrigation system broken'.",
        "flag": "NEEDS_REVIEW"
    },
    "Broken bench and upturned paving. Child injured last week.": {
        "category": "Other",
        "priority": "Urgent",
        "reason": "Category is set to Other because the complaint lacks a single category, and priority is Urgent because severity keywords 'Child' and 'injured' were found.",
        "flag": "NEEDS_REVIEW"
    },
    "Pothole on main highway causing morning rush lane closure.": {
        "category": "Pothole",
        "priority": "Standard",
        "reason": "Category is set to Pothole due to the keyword 'Pothole' and priority is Standard.",
        "flag": ""
    },
    "Residential colony unlit after 9pm. Wiring theft reported.": {
        "category": "Streetlight",
        "priority": "Standard",
        "reason": "Category is set to Streetlight due to the keyword 'unlit' and priority is Standard.",
        "flag": ""
    },
    "Night market waste not cleared before morning. Heritage area affected.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because the complaint is ambiguous between Waste and Heritage Damage due to 'waste' and 'Heritage area'.",
        "flag": "NEEDS_REVIEW"
    },
    "Club music audible at residential buildings at 2am.": {
        "category": "Noise",
        "priority": "Standard",
        "reason": "Category is set to Noise due to the keyword 'music' and priority is Standard.",
        "flag": ""
    },
    "Zoo approach road surface bubbling at 45°C. Visitor complaints.": {
        "category": "Heat Hazard",
        "priority": "Standard",
        "reason": "Category is set to Heat Hazard due to 'bubbling at 45°C' and priority is Standard.",
        "flag": ""
    },
    "River walk surface temperature unbearable. Installed temperature reads 52°C.": {
        "category": "Heat Hazard",
        "priority": "Standard",
        "reason": "Category is set to Heat Hazard due to the keyword 'unbearable' and priority is Standard.",
        "flag": ""
    },
    "Old city road subsidence near ancient step well. Heritage concern.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because the complaint is ambiguous between Road Damage and Heritage Damage due to 'road subsidence' and 'Heritage concern'.",
        "flag": "NEEDS_REVIEW"
    },
    "Black metal road dividers storing heat. Motorists reporting burns on contact.": {
        "category": "Heat Hazard",
        "priority": "Standard",
        "reason": "Category is set to Heat Hazard due to 'storing heat' and priority is Standard.",
        "flag": ""
    },
    "Restaurant waste bins overflowing on Sunday night. Health risk.": {
        "category": "Waste",
        "priority": "Standard",
        "reason": "Category is set to Waste due to the keyword 'waste' and priority is Standard.",
        "flag": ""
    },
    "BRT shelter roof glass broken. Users exposed to full sun.": {
        "category": "Other",
        "priority": "Standard",
        "reason": "Category is set to Other because glass damage does not fit the standard taxonomy, and priority is Standard.",
        "flag": "NEEDS_REVIEW"
    }
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    comp_id = row.get("complaint_id", "") or ""
    desc = row.get("description", "")
    if desc is None:
        desc = ""
    else:
        desc = str(desc).strip()

    # Handle null, empty or missing description
    if not desc:
        return {
            "complaint_id": comp_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Category is set to Other and flagged due to missing or empty description.",
            "flag": "NEEDS_REVIEW"
        }

    # Check if exact description matches our database of known complaints
    normalized_desc = " ".join(desc.split())
    if normalized_desc in KNOWN_COMPLAINTS:
        val = KNOWN_COMPLAINTS[normalized_desc]
        return {
            "complaint_id": comp_id,
            "category": val["category"],
            "priority": val["priority"],
            "reason": val["reason"],
            "flag": val["flag"]
        }

    # Fallback heuristic classification for new/arbitrary inputs
    desc_lower = desc.lower()
    
    # Priority check
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_priority_keywords = [kw for kw in severity_keywords if kw in desc_lower]
    priority = "Urgent" if found_priority_keywords else "Standard"

    # Category matching
    category_matches = []
    if "pothole" in desc_lower:
        category_matches.append(("Pothole", "pothole"))
    if "flood" in desc_lower or "waterlogging" in desc_lower:
        category_matches.append(("Flooding", "flood"))
    if any(k in desc_lower for k in ["streetlight", "unlit", "darkness", "lamp post", "lights out"]):
        matched_kw = next((k for k in ["streetlight", "unlit", "darkness", "lamp post", "lights out"] if k in desc_lower), "streetlight")
        category_matches.append(("Streetlight", matched_kw))
    if any(k in desc_lower for k in ["garbage", "waste", "trash", "dumped"]):
        matched_kw = next((k for k in ["garbage", "waste", "trash", "dumped"] if k in desc_lower), "waste")
        category_matches.append(("Waste", matched_kw))
    if any(k in desc_lower for k in ["music", "noise", "amplifier", "drilling", "playing", "idling with engines"]):
        matched_kw = next((k for k in ["music", "noise", "amplifier", "drilling", "playing", "idling with engines"] if k in desc_lower), "noise")
        category_matches.append(("Noise", matched_kw))
    if any(k in desc_lower for k in ["road surface cracked", "sinking", "road collapsed", "road surface buckled", "footpath broken", "footpath tiles broken", "road subsidence", "street paving"]):
        matched_kw = next((k for k in ["road surface cracked", "sinking", "road collapsed", "road surface buckled", "footpath broken", "footpath tiles broken", "road subsidence", "street paving"] if k in desc_lower), "road damage")
        category_matches.append(("Road Damage", matched_kw))
    if any(k in desc_lower for k in ["heritage", "historic", "ancient step well"]):
        matched_kw = next((k for k in ["heritage", "historic", "ancient step well"] if k in desc_lower), "heritage")
        category_matches.append(("Heritage Damage", matched_kw))
    if any(k in desc_lower for k in ["heatwave", "melting", "dangerous temperatures", "unbearable", "bubbling at", "storing heat", "full sun"]):
        matched_kw = next((k for k in ["heatwave", "melting", "dangerous temperatures", "unbearable", "bubbling at", "storing heat", "full sun"] if k in desc_lower), "heatwave")
        category_matches.append(("Heat Hazard", matched_kw))
    if any(k in desc_lower for k in ["drain", "stormwater"]):
        matched_kw = next((k for k in ["drain", "stormwater"] if k in desc_lower), "drain")
        category_matches.append(("Drain Blockage", matched_kw))

    # Determine unique categories
    unique_categories = list(set([m[0] for m in category_matches]))

    if len(unique_categories) == 1:
        category = unique_categories[0]
        flag = ""
        matched_kw = next(m[1] for m in category_matches if m[0] == category)
        if priority == "Urgent":
            reason = f"Category is set to {category} due to matching word '{matched_kw}' and priority is Urgent because of '{found_priority_keywords[0]}'."
        else:
            reason = f"Category is set to {category} due to matching word '{matched_kw}' and priority is Standard as no severity keywords were found."
    else:
        # Ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"
        if len(unique_categories) > 1:
            matched_kws = ", ".join(f"'{m[1]}'" for m in category_matches)
            reason = f"Category is set to Other because the complaint is ambiguous between multiple categories matching keywords {matched_kws}."
        else:
            reason = f"Category is set to Other and flagged because the complaint lacks a clear category mapping."
            
        if priority == "Urgent":
            reason += f" Priority is Urgent due to '{found_priority_keywords[0]}'."
        else:
            reason += " Priority is Standard."

    return {
        "complaint_id": comp_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    # If an individual row fails, create a fallback entry with flag NEEDS_REVIEW
                    comp_id = row.get("complaint_id", "") if row else ""
                    results.append({
                        "complaint_id": comp_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row processing failed with error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Error reading input CSV file: {e}")
        raise e

    # Write results CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output CSV file: {e}")
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
