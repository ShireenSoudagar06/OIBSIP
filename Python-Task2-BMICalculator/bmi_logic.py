from config import CATEGORY_COLORS


def validate_inputs(name, weight_str, height_str):
    """
    Validate the three BMI input values.

    Args:
        name: User name entered as text.
        weight_str: Weight in kilograms, entered as text.
        height_str: Height in meters, entered as text.

    Returns:
        A tuple (is_valid, error_message).
        - is_valid is True when all inputs are acceptable.
        - error_message is an empty string when valid, otherwise a helpful
          message explaining the first problem found.
    """
    # --- User name ---------------------------------------------------------
    if not name or not name.strip():
        return False, "Please enter a user name."

    # --- Weight ------------------------------------------------------------
    if not weight_str or not weight_str.strip():
        return False, "Please enter a weight."
    try:
        weight = float(weight_str)
    except ValueError:
        return False, "Weight must be a numeric value."
    if weight <= 0:
        return False, "Weight must be greater than zero."

    # --- Height ------------------------------------------------------------
    if not height_str or not height_str.strip():
        return False, "Please enter a height."
    try:
        height = float(height_str)
    except ValueError:
        return False, "Height must be a numeric value."
    if height <= 0:
        return False, "Height must be greater than zero."

    return True, ""


def calculate_bmi(weight, height):
    """
    Calculate Body Mass Index.

    Formula: BMI = weight / (height ** 2)

    Args:
        weight: Weight in kilograms.
        height: Height in meters.

    Returns:
        The calculated BMI as a floating point number.
    """
    return weight / (height ** 2)


def classify_bmi(bmi):
    """
    Classify a BMI value into a category.

    Categories (standard adult BMI ranges):
    - Underweight: BMI < 18.5
    - Normal:      18.5 <= BMI < 25
    - Overweight:  25   <= BMI < 30
    - Obese:       BMI >= 30

    Note: The requirement states Normal as 18.5-24.9 and Overweight as
    25-29.9. Using < 25 and < 30 is the standard continuous interpretation
    and covers every possible BMI value without gaps (e.g. 24.95).

    Args:
        bmi: The calculated BMI value.

    Returns:
        A category string: "Underweight", "Normal", "Overweight", or "Obese".
    """
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def get_category_color(category):
    """
    Return the colour assigned to a BMI category.

    Args:
        category: One of the four BMI category strings.

    Returns:
        The hex colour code for the category, or a neutral grey if the
        category is not recognised.
    """
    return CATEGORY_COLORS.get(category, "#7F8C8D")
