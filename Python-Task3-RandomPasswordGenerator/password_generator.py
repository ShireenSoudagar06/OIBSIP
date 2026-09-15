# Random Password Generator - Beginner Tier
# A simple password generator that asks the user for preferences
# and generates a random password using Python's built-in modules.

import random
import string


def get_password_length():
    """
    Ask the user for the desired password length.
    The minimum length is 8 characters.
    Keeps asking until a valid integer >= 8 is entered.
    """
    while True:
        try:
            length_input = input("Enter desired password length (minimum 8): ")
            length = int(length_input)
            if length < 8:
                print("Password length must be at least 8 characters. Please try again.")
                continue
            return length
        except ValueError:
            print("Invalid input. Please enter a whole number.")


def get_character_types():
    """
    Let the user choose which character types to include:
    - Uppercase letters (A-Z)
    - Lowercase letters (a-z)
    - Numbers (0-9)
    - Symbols (!@#$... etc.)
    At least 2 character types must be selected.
    """
    print("\nSelect character types to include (enter 'y' for yes, 'n' for no):")
    use_upper = input("  Uppercase letters (A-Z)? ").strip().lower() == 'y'
    use_lower = input("  Lowercase letters (a-z)? ").strip().lower() == 'y'
    use_numbers = input("  Numbers (0-9)? ").strip().lower() == 'y'
    use_symbols = input("  Symbols (!@#$%^&*)? ").strip().lower() == 'y'

    # Count how many types were selected
    selected_count = sum([use_upper, use_lower, use_numbers, use_symbols])

    if selected_count < 2:
        print("Error: You must select at least 2 character types.")
        return get_character_types()  # Ask again

    return use_upper, use_lower, use_numbers, use_symbols


def build_character_pool(use_upper, use_lower, use_numbers, use_symbols):
    """
    Build a pool of characters based on the user's selections.
    Combines the appropriate character sets from the string module.
    """
    pool = ""
    if use_upper:
        pool += string.ascii_uppercase  # A-Z
    if use_lower:
        pool += string.ascii_lowercase  # a-z
    if use_numbers:
        pool += string.digits           # 0-9
    if use_symbols:
        pool += string.punctuation      # !@#$%^&* etc.
    return pool


def generate_password(length, char_pool):
    """
    Generate a random password by picking characters from the pool.
    Uses random.choice() to select each character.
    """
    password = "".join(random.choice(char_pool) for _ in range(length))
    return password


def main():
    print("=== Random Password Generator ===\n")

    while True:
        # Step 1: Ask for password length
        length = get_password_length()

        # Step 2: Ask for character type preferences
        use_upper, use_lower, use_numbers, use_symbols = get_character_types()

        # Step 3: Build the character pool from selected types
        char_pool = build_character_pool(use_upper, use_lower, use_numbers, use_symbols)

        # Step 4: Generate the password
        password = generate_password(length, char_pool)

        # Step 5: Show the result
        print(f"\nYour generated password is:\n  {password}\n")

        # Step 6: Ask if the user wants another password
        again = input("Generate another password? (y/n): ").strip().lower()
        if again != 'y':
            print("Goodbye!")
            break


# Run the program
if __name__ == "__main__":
    main()