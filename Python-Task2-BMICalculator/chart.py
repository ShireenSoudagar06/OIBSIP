import tkinter as tk
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class BMIChart:
    """
    Manages the Matplotlib line chart embedded inside the Tkinter window.

    The chart is drawn into a plain tkinter.Frame supplied by the GUI layer.
    The chart never talks to the database directly; it only receives the data
    it needs (dates and BMI values) from the application controller.
    """

    def __init__(self):
        self.figure = None
        self.canvas = None

    def plot_bmi_trend(self, dates, bmi_values, parent_frame):
        """
        Create or refresh the BMI trend chart inside parent_frame.

        Args:
            dates: List of record_date strings from SQLite
                   (format: "YYYY-MM-DD HH:MM:SS").
            bmi_values: List of BMI floats, one per date.
            parent_frame: The tkinter.Frame that holds the chart.
        """
        # Remove any previously drawn chart widgets.
        for widget in parent_frame.winfo_children():
            widget.destroy()

        self.figure = Figure(figsize=(6, 3.5), dpi=100)
        ax = self.figure.add_subplot(111)

        if bmi_values:
            # Convert SQLite date strings into datetime objects so Matplotlib
            # can space the points correctly on the x-axis.
            date_objs = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S") for d in dates]

            ax.plot(date_objs, bmi_values, marker="o", color="#2C3E50",
                    linewidth=2, markersize=6)
            ax.set_title("BMI Trend Over Time", fontsize=13, fontweight="bold")
            ax.set_xlabel("Date")
            ax.set_ylabel("BMI")
            ax.grid(True, alpha=0.3)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            ax.tick_params(axis="x", rotation=45)
        else:
            # Empty state shown when the user has no history yet.
            ax.text(0.5, 0.5, "No history available yet",
                    ha="center", va="center", fontsize=12,
                    transform=ax.transAxes)
            ax.set_title("BMI Trend Over Time", fontsize=13, fontweight="bold")
            ax.set_xticks([])
            ax.set_yticks([])

        self.figure.tight_layout()

        # Embed the Matplotlib figure into the Tkinter frame.
        self.canvas = FigureCanvasTkAgg(self.figure, parent_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
