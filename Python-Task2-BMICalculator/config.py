import os

# -----------------------------------------------------------------------------
# Database configuration
# -----------------------------------------------------------------------------
# Store the database in the same directory as the application files.
# os.path.abspath(__file__) gives the full path to this config.py file.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "bmi_records.db")

# -----------------------------------------------------------------------------
# Window configuration
# -----------------------------------------------------------------------------
WINDOW_TITLE = "BMI Calculator - Advanced Tier"
WINDOW_SIZE = "560x740"

# -----------------------------------------------------------------------------
# Colour scheme
# -----------------------------------------------------------------------------
BACKGROUND_COLOR = "#F0F2F5"      # Light grey page background
TEXT_COLOR = "#2C3E50"            # Dark slate text
RESULT_BG_DEFAULT = "#ECF0F1"     # Default result panel background
ERROR_COLOR = "#C0392B"           # Dark red for error messages

# Visually distinct, accessible colours for each BMI category
CATEGORY_COLORS = {
    "Underweight": "#3498DB",     # Blue
    "Normal": "#2ECC71",          # Green
    "Overweight": "#F39C12",      # Orange
    "Obese": "#E74C3C",           # Red
}

# -----------------------------------------------------------------------------
# Fonts
# -----------------------------------------------------------------------------
TITLE_FONT = ("Helvetica", 16, "bold")
LABEL_FONT = ("Helvetica", 10)
RESULT_FONT = ("Helvetica", 12, "bold")
