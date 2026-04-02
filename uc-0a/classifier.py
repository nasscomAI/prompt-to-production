def classify_complaint(row):
    description = row.get('description', '').lower()

    # --- CATEGORY KEYWORDS ---
    category_keywords = {
        'Pothole': ['pothole', 'hole in road'],
        'Flooding': ['flood', 'water logging', 'drain overflow'],
        'Streetlight': ['streetlight', 'light not working', 'no light'],
        'Waste': ['waste', 'garbage', 'dump', 'trash'],
        'Noise': ['noise', 'loud', 'disturbance'],
        'Road Damage': ['road damage', 'crack', 'pavement', 'broken road'],
        'Heritage Damage': ['heritage', 'monument damage'],
        'Heat Hazard': ['heat', 'hot', 'temperature'],
        'Drain Blockage': ['drain block', 'clogged drain', 'sewage'],
    }

    # --- SEVERITY KEYWORDS ---
    severity_keywords = [
        'injury', 'child', 'school', 'hospital',
        'ambulance', 'fire', 'hazard', 'fell', 'collapse'
    ]

    # --- RICE: RELEVANCE ---
    match_scores = {}
    for cat, keywords in category_keywords.items():
        score = sum(1 for keyword in keywords if keyword in description)
        if score > 0:
            match_scores[cat] = score

    # --- RICE: CONFIDENCE ---
    if match_scores:
        category = max(match_scores, key=match_scores.get)
        confidence = match_scores[category] / len(category_keywords[category])
    else:
        category = 'Other'
        confidence = 0

    # --- RICE: IMPACT ---
    is_severe = any(word in description for word in severity_keywords)

    # --- PRIORITY LOGIC ---
    if is_severe and confidence > 0:
        priority = 'Urgent'
    elif confidence >= 0.5:
        priority = 'High'
    else:
        priority = 'Standard'

    # --- RICE: EXPLAINABILITY ---
    matched_words = [
        kw for kw in category_keywords.get(category, [])
        if kw in description
    ]

    reason = (
        f"Matched keywords {matched_words} → category '{category}'. "
        f"Confidence={confidence:.2f}, Severity={'Yes' if is_severe else 'No'}."
    )

    # --- RICE: UNCERTAINTY FLAG ---
    flag = 'NEEDS_REVIEW' if confidence < 0.3 else ''

    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }
