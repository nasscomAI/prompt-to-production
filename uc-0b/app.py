def main():
    try:
        with open("../data/policy-documents/policy_hr_leave.txt", "r", encoding="utf-8") as f:
            content = f.read()

        # simple summary (keeping full content to preserve meaning)
        summary = content

        with open("summary_hr_leave.txt", "w", encoding="utf-8") as f:
            f.write(summary)

        print("Summary created successfully!")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()