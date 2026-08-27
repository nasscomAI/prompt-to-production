def is_valid_number(text):
    return text.isdigit()


def main():
    value = input("Enter a number: ")

    if is_valid_number(value):
        print("Valid number")
    else:
        print("Invalid input")


if __name__ == "__main__":
    main()