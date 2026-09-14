import tkinter as tk
from tkinter import ttk

from config import (
    WINDOW_TITLE,
    WINDOW_SIZE,
    BACKGROUND_COLOR,
    TEXT_COLOR,
    TITLE_FONT,
    LABEL_FONT,
    RESULT_FONT,
    ERROR_COLOR,
    RESULT_BG_DEFAULT,
)


class BMICalculatorGUI:
    """
    Builds and manages all Tkinter widgets for the BMI Calculator.

    This class is responsible only for the visual interface. It knows nothing
    about BMI math or SQLite; it simply exposes getter/setter methods that the
    application controller (BMICalculatorApp) uses to read inputs and update
    the display.
    """

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        # String variables bound to the input fields and result label.
        self.name_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.result_var = tk.StringVar(value="Enter your details and click Calculate")
        self.error_var = tk.StringVar(value="")

        # Widget references used by the controller.
        self.chart_frame = None

        self._setup_window()
        self._create_widgets()

    def _setup_window(self):
        """Configure the main application window."""
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=BACKGROUND_COLOR)

    def _create_widgets(self):
        """Create and place every widget in the window."""
        # --- Title ----------------------------------------------------------
        title_label = tk.Label(
            self.root, text="BMI Calculator",
            font=TITLE_FONT, bg=BACKGROUND_COLOR, fg=TEXT_COLOR
        )
        title_label.pack(pady=(15, 5))

        # --- Input frame ----------------------------------------------------
        input_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        input_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(input_frame, text="User Name:", font=LABEL_FONT,
                 bg=BACKGROUND_COLOR).grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Combobox(
            input_frame, textvariable=self.name_var, width=30, state="normal"
        )
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.name_entry.focus()
        # Refresh history/chart immediately when user selects from dropdown
        self.name_entry.bind("<<ComboboxSelected>>", self._on_name_selected)
        # Also refresh when user presses Enter after typing a name
        self.name_entry.bind("<Return>", self._on_name_selected)

        tk.Label(input_frame, text="Weight (kg):", font=LABEL_FONT,
                 bg=BACKGROUND_COLOR).grid(row=1, column=0, sticky="w", pady=5)
        self.weight_entry = ttk.Entry(
            input_frame, textvariable=self.weight_var, width=30
        )
        self.weight_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(input_frame, text="Height (m):", font=LABEL_FONT,
                 bg=BACKGROUND_COLOR).grid(row=2, column=0, sticky="w", pady=5)
        self.height_entry = ttk.Entry(
            input_frame, textvariable=self.height_var, width=30
        )
        self.height_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # --- Buttons ---------------------------------------------------------
        button_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        button_frame.pack(pady=10)

        self.calculate_button = ttk.Button(
            button_frame, text="Calculate BMI",
            command=self.controller.calculate_handler
        )
        self.calculate_button.grid(row=0, column=0, padx=5)

        self.history_button = ttk.Button(
            button_frame, text="View History",
            command=self.controller.view_history_handler
        )
        self.history_button.grid(row=0, column=1, padx=5)

        # --- Error label -----------------------------------------------------
        self.error_label = tk.Label(
            self.root, textvariable=self.error_var,
            font=LABEL_FONT, bg=BACKGROUND_COLOR, fg=ERROR_COLOR,
            wraplength=480, justify="left"
        )
        self.error_label.pack(pady=(0, 5), padx=20)

        # --- Result frame ----------------------------------------------------
        result_frame = tk.LabelFrame(
            self.root, text="Result", font=LABEL_FONT,
            bg=BACKGROUND_COLOR, fg=TEXT_COLOR
        )
        result_frame.pack(pady=10, padx=20, fill=tk.X)

        self.result_label = tk.Label(
            result_frame, textvariable=self.result_var,
            font=RESULT_FONT, bg=RESULT_BG_DEFAULT, fg=TEXT_COLOR,
            pady=12, anchor="center"
        )
        self.result_label.pack(fill=tk.X, padx=10, pady=10)

        # --- History frame ---------------------------------------------------
        history_frame = tk.LabelFrame(
            self.root, text="BMI History", font=LABEL_FONT,
            bg=BACKGROUND_COLOR, fg=TEXT_COLOR
        )
        history_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.history_listbox = tk.Listbox(
            history_frame, height=6, font=LABEL_FONT
        )
        self.history_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # --- Chart frame -----------------------------------------------------
        chart_frame = tk.LabelFrame(
            self.root, text="BMI Trend Chart", font=LABEL_FONT,
            bg=BACKGROUND_COLOR, fg=TEXT_COLOR
        )
        chart_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        self.chart_frame = chart_frame

    # ------------------------------------------------------------------
    # Getter methods - the controller reads input values through these.
    # ------------------------------------------------------------------
    def get_name(self):
        """Return the current user name text."""
        return self.name_var.get()

    def get_weight(self):
        """Return the current weight text."""
        return self.weight_var.get()

    def get_height(self):
        """Return the current height text."""
        return self.height_var.get()

    # ------------------------------------------------------------------
    # Setter methods - the controller updates the display through these.
    # ------------------------------------------------------------------
    def show_result(self, bmi, category, color):
        """Show a calculated BMI and its category with colour feedback."""
        self.result_var.set("BMI: {:.2f}  |  Category: {}".format(bmi, category))
        self.result_label.configure(bg=color)
        self.error_var.set("")

    def show_error(self, message):
        """Display a validation or system error message in red."""
        self.error_var.set(message)
        self.result_label.configure(bg=RESULT_BG_DEFAULT)

    def update_history(self, records):
        """
        Populate the history listbox with BMI records for one user.

        Args:
            records: List of tuples (weight, height, bmi, category, date).
        """
        self.history_listbox.delete(0, tk.END)
        if not records:
            self.history_listbox.insert(tk.END, "No records found for this user.")
            return
        for weight, height, bmi, category, record_date in records:
            line = "{} | BMI: {:.2f} | {} | Weight: {} kg | Height: {} m".format(
                record_date, bmi, category, weight, height
            )
            self.history_listbox.insert(tk.END, line)

    def update_user_list(self, users):
        """Refresh the drop-down list of known user names."""
        self.name_entry["values"] = users

    def get_chart_frame(self):
        """Return the frame that holds the Matplotlib chart."""
        return self.chart_frame

    def _on_name_selected(self, event=None):
        """Called when user selects a name from the combobox or presses Enter."""
        self.controller.view_history_handler()
