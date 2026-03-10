import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, required=True)
    args = parser.parse_args()
    user_input = args.text.lower()

    # Simple complaint routing logic (replaceable by full RICE workflow)
    if "street light" in user_input or "lamp" in user_input:
        category = "Public Infrastructure"
        action = "Electric maintenance team assigned."
    elif "garbage" in user_input or "trash" in user_input:
        category = "Sanitation"
        action = "Waste collection team assigned."
    elif "water leak" in user_input or "pipe" in user_input:
        category = "Water Supply"
        action = "Water maintenance team assigned."
    else:
        category = "Other"
        action = "Manual review required."

    print(f"Category: {category} | Action: {action}")

if __name__ == "__main__":
    main()