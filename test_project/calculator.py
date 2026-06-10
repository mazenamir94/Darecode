def add(a, b):
    """Return the sum of a and b."""
    return a + b

def subtract(a, b):
    """Return the difference of a and b."""
    return a - b

def multiply(a, b):
    """Return the product of a and b."""
    return a * b

def divide(a, b):
    """Return the quotient of a and b.
    
    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b


if __name__ == "__main__":
    # Example usage
    print("Add: 5 + 3 =", add(5, 3))
    print("Subtract: 5 - 3 =", subtract(5, 3))
    print("Multiply: 5 * 3 =", multiply(5, 3))
    print("Divide: 6 / 3 =", divide(6, 3))
