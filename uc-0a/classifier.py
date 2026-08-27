def classify_complaint(text):
    text = text.lower()

    if "pothole" in text or "road" in text:
        return "Pothole", "Detected road or pothole related words"

    elif "flood" in text or "waterlogging" in text:
        return "Flooding", "Detected flooding related words"

    elif "garbage" in text or "waste" in text:
        return "Garbage", "Detected sanitation related words"

    elif "water" in text or "pipeline" in text:
        return "Water", "Detected water supply related words"

    elif "electricity" in text or "power" in text or "light" in text:
        return "Electricity", "Detected electricity related words"

    else:
        return "Other", "Category unclear from description"


def main():
    complaint = input("Enter complaint: ")

    category, reason = classify_complaint(complaint)

    print("Category:", category)
    print("Reason:", reason)


if __name__ == "__main__":
    main()
