from utils import get_message
from helpers import capitalize_text

def main():
    message = get_message()
    print(capitalize_text(message))

if __name__ == "__main__":
    main()