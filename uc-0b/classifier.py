import re
import os
import csv


def retrieve_policy(filepath):
    if not os.path.exists(filepath):
        return {"error": "File not found"}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except (UnicodeDecodeError, IOError):
        return {"error": "Invalid file"}

    if not text.strip():
        return {"error": "Invalid file"}

    sections = {}
    lines = text.splitlines()
    current_section = None
    section_clauses = []
    pending_clause = None

    def flush_pending():
        nonlocal pending_clause
        if pending_clause is not None:
            section_clauses.append(pending_clause)
            pending_clause = None

    for line in lines:
        stripped = line.strip()
        sep_match = re.match(r"^═+$", stripped)
        section_match = re.match(r"^(\d+)\.\s+(.+)", stripped)
        clause_match = re.match(r"^(\d+\.\d+)\s+(.+)", stripped)

        if sep_match:
            continue
        if section_match:
            flush_pending()
            if current_section and section_clauses:
                sections[current_section] = section_clauses
            current_section = stripped
            section_clauses = []
        elif clause_match:
            flush_pending()
            pending_clause = stripped
        elif pending_clause and stripped:
            pending_clause += " " + stripped
        elif current_section and stripped and not re.match(r"^\d", stripped):
            pass
        elif current_section and stripped:
            section_clauses.append(stripped)

    flush_pending()
    if current_section and section_clauses:
        sections[current_section] = section_clauses

    return sections


def _extract_clause_map(sections):
    clause_map = {}
    for section, clauses in sections.items():
        for clause in clauses:
            m = re.match(r"(\d+\.\d+)", clause)
            if m:
                clause_map[m.group(1)] = clause
    return clause_map


def summarize_policy(sections):
    if not isinstance(sections, dict):
        return "ERROR: Invalid input format. Expected structured sections with numbered clauses."

    seen_clauses = _extract_clause_map(sections)
    if not seen_clauses:
        return "ERROR: Input does not contain numbered policy clauses. Cannot produce compliant summary."

    summary_parts = []

    for section, clauses in sections.items():
        summary_parts.append(section)
        for clause in clauses:
            clause_num = re.match(r"(\d+\.\d+)", clause)
            if clause_num and clause_num.group(1) in seen_clauses:
                summary_parts.append("  " + clause)

    return "\n".join(summary_parts)


def _extract_clause_numbers(text):
    return set(re.findall(r"\b(\d+\.\d+)\b", text))


def _normalize(text):
    return re.sub(r'\s+', ' ', text).strip()


def classify_summary(source_sections, summary_text):
    source_clauses = _extract_clause_map(source_sections)
    source_numbers = set(source_clauses.keys())
    summary_numbers = _extract_clause_numbers(summary_text)
    normalized = _normalize(summary_text).lower()

    issues = []

    missing = source_numbers - summary_numbers
    if missing:
        for cn in sorted(missing):
            issues.append({
                "type": "clause_omission",
                "clause": cn,
                "detail": f"Clause {cn} is missing from the summary."
            })

    condition_preservation = {
        "5.2": ["Department Head", "HR Director"],
        "2.4": ["written approval", "Verbal approval is not valid"],
        "2.3": ["14 calendar days"],
        "3.2": ["3 or more consecutive", "48 hours"],
    }

    for clause_num, conditions in condition_preservation.items():
        if clause_num in summary_numbers and clause_num in source_clauses:
            for condition in conditions:
                if condition.lower() not in normalized:
                    issues.append({
                        "type": "condition_drop",
                        "clause": clause_num,
                        "detail": f"Clause {clause_num}: condition '{condition}' not found in summary."
                    })

    bleed_patterns = [
        r"as is standard practice",
        r"typically in government",
        r"employees are generally expected",
        r"standard industry practice",
        r"in most organisations",
    ]
    for pattern in bleed_patterns:
        matches = re.findall(pattern, summary_text, re.IGNORECASE)
        if matches:
            issues.append({
                "type": "scope_bleed",
                "clause": None,
                "detail": f"Scope bleed: phrase '{matches[0]}' not present in source document."
            })

    return issues


def load_city_complaints(filepath):
    if not os.path.exists(filepath):
        return {"error": "File not found"}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                rows.append(row)
    except (IOError, csv.Error) as e:
        return {"error": f"Invalid file: {e}"}

    if not rows:
        return {"error": "Invalid file"}

    return rows


COMPLAINT_CATEGORIES = [
    {
        "name": "Potholes and Road Damage",
        "patterns": [
            r"pothole", r"road surface", r"road subsidence",
            r"road collapsed", r"road.*buckled", r"cracked.*road",
            r"bubbling", r"melting", r"tarmac", r"crater",
            r"footpath.*broken", r"paving", r"cobblestone",
            r"road dividers", r"surface.*temperature", r"tyre blowout",
            r"tyre damage",
        ],
    },
    {
        "name": "Flooding and Drainage",
        "patterns": [
            r"flood", r"drain", r"waterlog", r"underpass.*rain",
            r"bus stand.*flooded", r"bridge.*flood", r"stormwater",
            r"rainwater", r"mosquito breeding",
        ],
    },
    {
        "name": "Garbage and Sanitation",
        "patterns": [
            r"garbage", r"waste", r"overflow", r"dead animal",
            r"waste.*clear", r"bins", r"dump", r"debris",
        ],
    },
    {
        "name": "Streetlights and Electrical",
        "patterns": [
            r"streetlight", r"light.*out", r"unlit", r"substation tripped",
            r"darkness", r"sparking", r"wiring theft", r"electrical hazard",
        ],
    },
    {
        "name": "Noise and Nuisance",
        "patterns": [
            r"music", r"noise", r"amplifier", r"drilling",
            r"club music", r"wedding.*band", r"idling.*engine",
            r"delivery truck",
        ],
    },
    {
        "name": "Parks and Trees",
        "patterns": [
            r"tree", r"dead tree", r"park.*bench", r"irrigation",
            r"grass.*dying", r"bench.*broken",
        ],
    },
    {
        "name": "Heritage and Public Safety",
        "patterns": [
            r"heritage", r"heritage.*lamp", r"heritage.*stone",
            r"heritage.*building", r"billboard", r"defaced",
        ],
    },
    {
        "name": "Infrastructure and Utilities",
        "patterns": [
            r"bus shelter", r"bus stop", r"brt", r"shelter.*roof",
            r"manhole", r"gas pipeline", r"gas leak",
            r"footpath.*sink", r"subsidence", r"bench.*upturned",
        ],
    },
]


def classify_complaint(description):
    desc_lower = description.lower()
    matched = []
    for cat in COMPLAINT_CATEGORIES:
        for pattern in cat["patterns"]:
            if re.search(pattern, desc_lower):
                matched.append(cat["name"])
                break
    return matched if matched else ["Uncategorized"]


def summarize_city_complaints(complaints, city_name):
    if not complaints or isinstance(complaints, dict) and "error" in complaints:
        return f"ERROR: No valid complaint data for {city_name}."

    total = len(complaints)
    category_counts = {}
    ward_counts = {}
    channel_counts = {}
    days_by_category = {}

    for c in complaints:
        types = classify_complaint(c["description"])
        for t in types:
            category_counts[t] = category_counts.get(t, 0) + 1
            days_list = days_by_category.setdefault(t, [])
            days_list.append(int(c["days_open"]))

        ward_counts[c["ward"]] = ward_counts.get(c["ward"], 0) + 1
        channel_counts[c["reported_by"]] = channel_counts.get(c["reported_by"], 0) + 1

    top_categories = sorted(category_counts.items(), key=lambda x: -x[1])[:3]
    avg_days = {}
    for cat, days in days_by_category.items():
        avg_days[cat] = round(sum(days) / len(days), 1)

    lines = [f"{city_name.upper()} — Complaint Summary", f"Total complaints: {total}", ""]
    lines.append("Top 3 complaint categories:")
    for cat, count in top_categories:
        avg = avg_days.get(cat, 0)
        lines.append(f"  {cat}: {count} complaints (avg {avg} days open)")

    lines.append("")
    lines.append(f"Wards affected: {len(ward_counts)}")
    top_wards = sorted(ward_counts.items(), key=lambda x: -x[1])[:3]
    for ward, count in top_wards:
        lines.append(f"  {ward}: {count} complaints")

    lines.append("")
    lines.append("Reporting channels:")
    for ch, count in sorted(channel_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {ch}: {count}")

    return "\n".join(lines)


def process_city(filepath):
    data = load_city_complaints(filepath)
    if isinstance(data, dict) and "error" in data:
        return data

    city_name = data[0]["city"] if data else "Unknown"
    summary = summarize_city_complaints(data, city_name)
    return {
        "city": city_name,
        "total_complaints": len(data),
        "summary": summary,
        "complaints": data,
    }


ALL_CITIES = {
    "ahmedabad": os.path.join("..", "data", "city-test-files", "test_ahmedabad.csv"),
    "hyderabad": os.path.join("..", "data", "city-test-files", "test_hyderabad.csv"),
    "kolkata": os.path.join("..", "data", "city-test-files", "test_kolkata.csv"),
    "pune": os.path.join("..", "data", "city-test-files", "test_pune.csv"),
}


def process_all_cities():
    results = {}
    for city_name, filepath in ALL_CITIES.items():
        results[city_name] = process_city(filepath)
    return results
