def get_number(prompt):
    """Get a valid float number from the user."""
    while True:
        user_input = input(prompt)
        try:
            return float(user_input)
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_operation():
    """Get a valid operation from the user."""
    valid_operations = {"+", "-", "*", "/"}
    while True:
        op = input("Choose an operation (+, -, *, /): ")
        if op in valid_operations:
            return op
        print("Invalid operation. Please choose one of +, -, *, /.")


def calculate(num1, num2, operation):
    """Perform the chosen arithmetic operation."""
    if operation == "+":
        return num1 + num2
    elif operation == "-":
        return num1 - num2
    elif operation == "*":
        return num1 * num2
    elif operation == "/":
        if num2 == 0:
            print("Error: Division by zero is not allowed.")
            return None
        return num1 / num2


def main():
    print("Simple Calculator")
    print("-----------------")

    first_number = get_number("Enter the first number: ")
    second_number = get_number("Enter the second number: ")
    operation = get_operation()

    result = calculate(first_number, second_number, operation)

    if result is not None:
        print(f"Result: {first_number} {operation} {second_number} = {result}")


if __name__ == "__main__":
    main()