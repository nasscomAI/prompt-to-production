def add(x, y):
    """Adds two numbers."""
    return x + y

def subtract(x, y):
    """Subtracts second number from first."""
    return x - y

def multiply(x, y):
    """Multiplies two numbers."""
    return x * y

def divide(x, y):
    """Divides first number by second."""
    if y == 0:
        return "Error! Division by zero."
    return x / y

def calculator():
    print("Welcome to Simple Calculator")
    print("Select an operation:")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")

    while True:
        choice = input("\nEnter choice(1/2/3/4) or 'q' to quit: ")

        if choice.lower() == 'q':
            print("Exiting calculator. Goodbye!")
            break

        if choice in ('1', '2', '3', '4'):
            try:
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))
            except ValueError:
                print("Invalid input. Please enter numerical values.")
                continue

            if choice == '1':
                print(f"Result: {num1} + {num2} = {add(num1, num2)}")
            elif choice == '2':
                print(f"Result: {num1} - {num2} = {subtract(num1, num2)}")
            elif choice == '3':
                print(f"Result: {num1} * {num2} = {multiply(num1, num2)}")
            elif choice == '4':
                print(f"Result: {num1} / {num2} = {divide(num1, num2)}")
            
            print("-" * 25)
        else:
            print("Invalid Input. Please select a valid operation (1/2/3/4) or 'q'.")

if __name__ == "__main__":
    calculator()
