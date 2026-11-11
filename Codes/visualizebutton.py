from data_utils import SAVE_DIR
# # visualizebutton.py



import tkinter as tk
from tkinter import messagebox
from utils import custom_error_messagebox, custom_visualize_messagebox
from activity import plot_activity_levels
from temperature import plot_temperature_levels
from leftgraphmain import update_plot
from rightgraphmain import update_right_plot

class VisualizeDataApp:
    def __init__(self, root, left_plot_ax, right_plot_ax):
        self.root = root
        self.left_plot_ax = left_plot_ax
        self.right_plot_ax = right_plot_ax
        self.root.title("Visualize Data")
        self.root.configure(bg='black')

        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.create_visualize_interface()

        self.center_window(600, 300, 180)
        
        self.annotations = []

    def button_style(self):
        return {
            'bg': '#555555',
            'fg': 'white',
            'font': ('Helvetica', 11),
            'activebackground': '#777777',
            'activeforeground': 'white',
            'bd': 0,
            'highlightthickness': 2,
            'highlightcolor': 'blue',
            'highlightbackground': 'blue',
            'width': 25,
            'height': 2
        }

    def create_visualize_interface(self):
        label = tk.Label(self.main_frame, text="Cow ID Number:", bg='black', fg='white', font=('Helvetica', 11))
        label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)

        vcmd = (self.root.register(self.validate_cow_id), '%P')
        self.cow_id_entry = tk.Entry(self.main_frame, font=('Helvetica', 11), width=20, validate='key', validatecommand=vcmd)
        self.cow_id_entry.grid(row=0, column=1, padx=10, pady=10, ipady=5, sticky=tk.W)

        self.visualize_activity_button = tk.Button(self.main_frame, text="Visualize Daily Activity Data", command=self.visualize_activity_data, **self.button_style())
        self.visualize_activity_button.grid(row=1, column=0, padx=10, pady=(10, 0))

        self.visualize_temperature_button = tk.Button(self.main_frame, text="Visualize Temperature Data", command=self.visualize_temperature_data, **self.button_style())
        self.visualize_temperature_button.grid(row=1, column=1, padx=10, pady=(10, 0))

        self.visualize_button = tk.Button(self.main_frame, text="Visualize", command=self.visualize_data_and_close, bg='#2e8b57', fg='white', font=('Helvetica', 11, 'bold'), width=10, height=2, bd=0, highlightthickness=0)
        self.visualize_button.grid(row=2, column=0, columnspan=2, pady=(20, 10))

        self.data_type = None
        self.compare_id = None
        self.compare_window = None

    def validate_cow_id(self, P):
        if P.isdigit() and len(P) <= 4:
            return True
        elif P == "":
            return True
        else:
            return False

    def visualize_activity_data(self):
        cow_id = self.cow_id_entry.get()
        if not cow_id:
            custom_error_messagebox("Error", "Please enter a Cow ID number.", self.root)
            return
        self.data_type = "activity"
        self.show_compare_dialog()

    def visualize_temperature_data(self):
        cow_id = self.cow_id_entry.get()
        if not cow_id:
            custom_error_messagebox("Error", "Please enter a Cow ID number.", self.root)
            return
        self.data_type = "temperature"
        self.show_compare_dialog()

    def show_compare_dialog(self):
        cow_id = self.cow_id_entry.get()
        if not cow_id:
            custom_error_messagebox("Error", "Please enter a Cow ID number.", self.root)
            return
        self.compare_window = custom_visualize_messagebox("Visualize", f"Visualizing {self.data_type} data for Cow ID: {cow_id}", self.root, self.set_compare_id_and_close)

    def set_compare_id_and_close(self, compare_id=None):
        self.compare_id = compare_id
        if self.compare_window:
            self.compare_window.destroy()

    def visualize_data_and_close(self):
        cow_id = self.cow_id_entry.get()
        if not cow_id:
            custom_error_messagebox("Error", "Please enter a Cow ID number.", self.root)
            return
        self.visualize_data()
        self.root.destroy()

    def visualize_data(self):
        cow_id = self.cow_id_entry.get()
        data_type = self.data_type
        compare_id = self.compare_id

        if not data_type:
            custom_error_messagebox("Error", "Please select a data type to visualize.", self.root)
            return

        if not cow_id:
            custom_error_messagebox("Error", "Please enter a Cow ID number.", self.root)
            return

        self.clear_tooltips()  # Clear existing tooltips before plotting new data

        if data_type == "activity":
            file_path = str(SAVE_DIR / 'activity_levels.csv')
            cow_data = plot_activity_levels(cow_id, compare_with_cow_id=compare_id, file_path=file_path)
            update_plot(self.left_plot_ax, cow_data, cow_id, data_type, self.annotations)
            if compare_id:
                update_right_plot(self.right_plot_ax, cow_data, cow_id, compare_id, data_type, self.annotations)
        elif data_type == "temperature":
            file_path = str(SAVE_DIR / 'temperature_data.csv')
            cow_data = plot_temperature_levels(cow_id, compare_with_cow_id=compare_id, file_path=file_path)
            update_plot(self.left_plot_ax, cow_data, cow_id, data_type, self.annotations)
            if compare_id:
                update_right_plot(self.right_plot_ax, cow_data, cow_id, compare_id, data_type, self.annotations)

        self.left_plot_ax.figure.canvas.draw()
        self.right_plot_ax.figure.canvas.draw()

    def clear_tooltips(self):
        # Clear existing annotations
        for annotation in self.annotations:
            annotation.remove()
        self.annotations.clear()

    def center_window(self, width, height, x_offset=0):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2) + x_offset
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

def open_visualize_data(parent_frame, left_plot_ax, right_plot_ax):
    visualize_data_window = tk.Toplevel(parent_frame)
    app = VisualizeDataApp(visualize_data_window, left_plot_ax, right_plot_ax)
    visualize_data_window.transient(parent_frame)
    visualize_data_window.grab_set()
    parent_frame.wait_window(visualize_data_window)
