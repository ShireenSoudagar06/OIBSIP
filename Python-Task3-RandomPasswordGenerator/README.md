# Random Password Generator

A beginner-friendly Python command-line application that generates random, secure passwords based on user-specified criteria. This is the **Beginner Tier** implementation of OASIS Infobyte Internship Task 3.

## Description

The Random Password Generator is a simple console-based tool that helps users create strong, randomized passwords. The user is prompted to specify the password length and which character types to include (uppercase, lowercase, numbers, symbols). The program validates all inputs, enforces a minimum password length of 8 characters, and requires at least 2 character types to be selected. Passwords are generated using Python's built-in `random` and `string` modules.

## Objective

The objective of this project is to build a functional password generator that:

- Teaches fundamental Python concepts such as user input handling, input validation, loops, and use of standard library modules.
- Produces random passwords that meet common security recommendations.
- Provides a clean, repeatable user experience through an interactive command-line interface.

## Features

- User can specify the desired password length.
- Minimum password length of 8 characters is enforced.
- User can choose to include uppercase letters (A-Z).
- User can choose to include lowercase letters (a-z).
- User can choose to include numbers (0-9).
- User can choose to include symbols (!@#$%^&* etc.).
- At least 2 character types must be selected before a password can be generated.
- Invalid password lengths (less than 8) are rejected with a clear error message.
- Invalid numeric input (non-integer values) is rejected with a clear error message.
- A random password is generated according to the selected criteria.
- User can generate another password without restarting the program.

## Technologies Used

- **Python** - Programming language
- **`random` module** - Used to select random characters from the character pool
- **`string` module** - Provides built-in constants for uppercase, lowercase, digits, and punctuation characters

## How the Program Works

1. **Password Length Input**: The program asks the user to enter the desired password length. It validates that the input is a valid integer and is at least 8 characters long. If the input is invalid or too short, the user is prompted again.

2. **Character Type Selection**: The user is asked four yes/no questions to choose which character types to include:
   - Uppercase letters (A-Z)
   - Lowercase letters (a-z)
   - Numbers (0-9)
   - Symbols (!@#$%^&* etc.)
   
   If fewer than 2 character types are selected, the user is notified and asked again.

3. **Character Pool Construction**: Based on the user's selections, the program builds a combined character pool using the appropriate constants from the `string` module.

4. **Password Generation**: The program uses `random.choice()` to randomly select characters from the pool until the desired length is reached, then joins them into the final password string.

5. **Repeat Option**: After displaying the generated password, the program asks if the user wants to generate another. Choosing "y" restarts the process; choosing "n" exits the program gracefully.

## How to Run the Project

1. Ensure Python 3.x is installed on your system.
2. Navigate to the project directory:
   ```bash
   cd Random_Password_Generator
   ```
3. Run the script:
   ```bash
   python password_generator.py
   ```
4. Follow the on-screen prompts to generate your password.

## Example Usage

```
=== Random Password Generator ===

Enter desired password length (minimum 8): 12

Select character types to include (enter 'y' for yes, 'n' for no):
  Uppercase letters (A-Z)? y
  Lowercase letters (a-z)? y
  Numbers (0-9)? n
  Symbols (!@#$%^&*)? n

Your generated password is:
  aBcDeFgHiJkL

Generate another password? (y/n): y

Enter desired password length (minimum 8): 10

Select character types to include (enter 'y' for yes, 'n' for no):
  Uppercase letters (A-Z)? y
  Lowercase letters (a-z)? y
  Numbers (0-9)? y
  Symbols (!@#$%^&*)? y

Your generated password is:
  p@SsW0rd!2

Generate another password? (y/n): n
Goodbye!
```

## Input Validation

The program implements robust input validation to ensure correct operation:

- **Password length must be a whole number**: If the user enters text or a decimal, an error message is displayed and the user is prompted again.
- **Password length must be at least 8 characters**: Lengths of 7 or fewer are rejected with a clear message.
- **At least 2 character types must be selected**: If the user selects only 0 or 1 character type, an error message is shown and the selection process is repeated.

All validation loops continue until the user provides valid input, preventing the program from crashing or producing invalid output.

## Project Structure

```
Random_Password_Generator/
├── password_generator.py   # Main Python script containing all program logic
└── Screenshots/            # Folder containing images of the program in action
    ├── Screenshot 2026-09-15 205759.png
    └── Screenshot 2026-09-15 205941.png
```

## Screenshots

See the `Screenshots/` folder for images demonstrating the program's interface and output.

## Learning Outcome

Through this project, the learner gains hands-on experience with:

- Taking and processing user input in Python.
- Implementing input validation loops with clear, user-friendly error messages.
- Using the `random` module for generating random selections.
- Using the `string` module to access built-in character sets.
- Building a repeatable interactive command-line application with a main loop.
- Writing clean, well-commented, and beginner-friendly code.