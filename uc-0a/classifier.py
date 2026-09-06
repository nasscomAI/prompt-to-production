import csv


def classify_complaint(description, days_open):
    desc = description.lower()

    # ---------------------------------------------------------
    # 1. CATEGORY CLASSIFICATION
    # ---------------------------------------------------------

    if "manhole" in desc or "missing cover" in desc:
        category = "Roads"
        cat_reason = "missing manhole cover"

    elif any(word in desc for word in [
        "drain", "drainage", "flood", "flooding",
        "waterlogging", "sewer", "gutter"
    ]):
        category = "Drainage/Flooding"
        cat_reason = "drainage or flooding issue"

    elif any(word in desc for word in [
        "garbage", "waste", "trash", "dumping",
        "dump", "bin", "litter"
    ]):
        category = "Garbage/Waste"
        cat_reason = "garbage or waste issue"

    elif any(word in desc for word in [
        "footpath", "sidewalk", "paver block",
        "pedestrian walk", "pavement"
    ]):
        category = "Footpath"
        cat_reason = "footpath issue"

    elif any(word in desc for word in [
        "streetlight", "street light", "lights out",
        "light out", "lamp", "darkness", "light pole"
    ]):
        category = "Streetlights"
        cat_reason = "streetlight issue"

    elif any(word in desc for word in [
        "stray", "dog", "animal", "cow",
        "cattle", "dung", "animal waste",
        "dead animal"
    ]):
        category = "Animal/Waste"
        cat_reason = "animal or animal-waste issue"

    elif any(word in desc for word in [
        "noise", "loudspeaker", "music", "sound", "blaring"
    ]):
        category = "Noise Complaint"
        cat_reason = "noise complaint"

    else:
        category = "Roads"
        cat_reason = "general public infrastructure issue"


    # ---------------------------------------------------------
    # 2. HIGH PRIORITY CONDITIONS
    # ---------------------------------------------------------

    high_priority = any(indicator in desc for indicator in [
        "missing manhole",
        "sparking",
        "electrical hazard",
        "electric shock",
        "live wire",
        "bare wire",
        "accident",
        "injury",
        "injured",
        "fell",
        "vehicle damage",
        "tyre damage",
        "tire damage",
        "damage car",
        "broken axle",
        "school children at risk",
        "children at risk",
        "risk to children",
        "serious injury risk",
        "hazard to pedestrians",
        "pedestrian risk",
        "cyclist",
        "inaccessible",
        "stranded"
    ])

    # Severe flooding + accessibility problem = High
    if (
        any(word in desc for word in ["flood", "flooding", "waterlogging"])
        and any(word in desc for word in [
            "inaccessible", "stranded", "bridge", "underpass"
        ])
    ):
        high_priority = True


    # ---------------------------------------------------------
    # 3. MEDIUM PRIORITY CONDITIONS
    # ---------------------------------------------------------

    medium_priority = any(indicator in desc for indicator in [
        "smell",
        "odor",
        "foul",
        "overflow",
        "garbage",
        "dumping",
        "dead animal",
        "health concern",
        "inconvenience",
        "three consecutive",
        "lights out",
        "light out",
        "dark",
        "blocked"
    ])

    # A complaint open for a considerable time supports Medium,
    # but does NOT automatically make every complaint Medium.
    if days_open >= 10:
        medium_priority = True


    # ---------------------------------------------------------
    # 4. PRIORITY DECISION
    # ---------------------------------------------------------

    if high_priority:
        priority = "High Priority"

        if "vehicle damage" in desc:
            pri_reason = "vehicle damage has already occurred"
        elif "fell" in desc or "injury" in desc or "injured" in desc:
            pri_reason = "an injury or fall has already occurred"
        elif "sparking" in desc or "electrical" in desc:
            pri_reason = "immediate electrical hazard reported"
        elif "missing manhole" in desc:
            pri_reason = "missing manhole cover creates serious injury risk"
        elif "school children" in desc or "children at risk" in desc:
            pri_reason = "serious safety risk to children"
        elif "inaccessible" in desc or "stranded" in desc:
            pri_reason = "flooding is making the area inaccessible"
        else:
            pri_reason = "serious safety or accessibility risk"

    elif medium_priority:
        priority = "Medium Priority"

        if "dead animal" in desc or "health concern" in desc:
            pri_reason = "health or environmental concern reported"
        elif days_open >= 10:
            pri_reason = f"persistent public-service problem open for {days_open} days"
        elif "overflow" in desc or "garbage" in desc or "dumping" in desc:
            pri_reason = "significant waste or public-environment concern"
        elif "blocked" in desc or "passengers" in desc:
            pri_reason = "significant public inconvenience"
        else:
            pri_reason = "significant public inconvenience or service concern"

    else:
        priority = "Low Priority"
        pri_reason = "minor issue with limited impact and no serious safety risk"


    reason = f"{cat_reason.capitalize()} - {pri_reason}."

    return category, priority, reason


def main():
    input_file = "../data/city-test-files/test_pune.csv"

    try:
        with open(input_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                complaint_id = row.get("complaint_id", "").strip()
                description = row.get("description", "").strip()

                try:
                    days_open = int(row.get("days_open", 0))
                except ValueError:
                    days_open = 0

                category, priority, reason = classify_complaint(
                    description,
                    days_open
                )

                print(
                    f"{complaint_id} | {category} | "
                    f"{priority} | {reason}"
                )

    except FileNotFoundError:
        print(
            f"Error: Could not open file '{input_file}'. "
            "Please check if the file exists."
        )


if __name__ == "__main__":
    main()