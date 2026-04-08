# app.py (inside uc-0a)

from classifier import classify_policy


def retrieve_data():
    # sample test clauses
    clauses = [
        "14-day advance notice required",
        "Written approval required before leave",
        "Unapproved absence leads to LOP",
        "Medical emergency in hospital",
        "Child care leave request"
    ]
    return clauses


def main():
    clauses = retrieve_data()

    results = classify_policy(clauses)

    for r in results:
        print(r)


if __name__ == "__main__":
    main()