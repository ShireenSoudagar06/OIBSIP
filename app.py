from bmi_logic import (
    validate_inputs,
    calculate_bmi,
    classify_bmi,
    get_category_color,
)
from database import DatabaseManager
from chart import BMIChart
from gui import BMICalculatorGUI


class BMICalculatorApp:
    """
    Central controller that connects the GUI, BMI logic, database, and chart.

    This is the only class that knows about all the other components. The GUI,
    database, logic, and chart modules never import each other directly, which
    keeps the architecture clean and easy to understand.
    """

    def __init__(self, root):
        self.root = root

        # 1. Open (or create) the SQLite database.
        self.db = DatabaseManager()

        # 2. Create the Matplotlib chart manager.
        self.chart = BMIChart()

        # 3. Build the Tkinter interface and register this app as its
        #    controller, so button clicks reach the methods below.
        self.gui = BMICalculatorGUI(root, self)

        # 4. Fill the user-name drop-down with names already in the database.
        self.refresh_user_list()

        # 5. Show the current user's history and chart on startup.
        self.view_history_handler()

    def calculate_handler(self):
        """
        Handle a click of the "Calculate BMI" button.

        Flow:
        1. Read the three input fields.
        2. Validate them with bmi_logic.validate_inputs.
        3. If invalid, show the error and stop.
        4. Calculate BMI, classify it, and show the colour-coded result.
        5. Save the record to SQLite.
        6. Refresh the user list, history, and chart.
        """
        name = self.gui.get_name().strip()
        weight_str = self.gui.get_weight()
        height_str = self.gui.get_height()

        # Step 2: validate all inputs at once.
        is_valid, error_msg = validate_inputs(name, weight_str, height_str)
        if not is_valid:
            self.gui.show_error(error_msg)
            return

        # Step 4: convert, calculate, classify, and display.
        weight = float(weight_str)
        height = float(height_str)
        bmi = calculate_bmi(weight, height)
        category = classify_bmi(bmi)
        color = get_category_color(category)
        self.gui.show_result(bmi, category, color)

        # Step 5: persist the record.
        if not self.db.save_record(name, weight, height, bmi, category):
            self.gui.show_error(
                "Could not save the BMI record. Please check that the "
                "database is accessible and try again."
            )
            return

        # Step 6: refresh everything that depends on the new record.
        self.refresh_user_list()
        self.view_history_handler()

    def view_history_handler(self):
        """
        Handle a click of the "View History" button.

        Fetches the selected user's records from SQLite, updates the history
        listbox, and redraws the BMI trend chart.
        """
        name = self.gui.get_name().strip()
        if not name or not name.strip():
            self.gui.show_error("Please enter a user name to view history.")
            return

        # Read errors are handled inside DatabaseManager and return an empty
        # list, which the GUI displays as a friendly "no records" message.
        records = self.db.get_history(name)
        self.gui.update_history(records)

        # The chart receives only the data it needs: dates and BMI values.
        dates = [record[4] for record in records]
        bmi_values = [record[2] for record in records]
        self.chart.plot_bmi_trend(dates, bmi_values, self.gui.get_chart_frame())

    def refresh_user_list(self):
        """Refresh the user-name drop-down from the database."""
        users = self.db.get_unique_users()
        self.gui.update_user_list(users)

    def close(self):
        """Clean up resources when the window is closed."""
        self.db.close()
        self.root.destroy()
