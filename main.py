import tkinter as tk

from app import BMICalculatorApp


def main():
    """Create the Tkinter window, start the app, and run the main loop."""
    root = tk.Tk()
    app = BMICalculatorApp(root)

    # Make sure the database connection is closed when the window closes.
    root.protocol("WM_DELETE_WINDOW", app.close)

    root.mainloop()


if __name__ == "__main__":
    main()
