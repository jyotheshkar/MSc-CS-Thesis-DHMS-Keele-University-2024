# upload_data.py
import tkinter as tk
from tkinter import filedialog
import json
import os
import shutil
from utils import custom_error_messagebox  # Assuming you have a custom error message function
# from visualize_uploaded_data import open_visualize_uploaded_data
from data_utils import get_uploaded_data_paths
# No need to import visualize_uploaded_data.py in upload_data.py if not absolutely necessary


CONFIG_FILE = 'upload_config.json'
SAVE_DIR = 'saved_upload_data'

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def delete_files():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    if os.path.exists(SAVE_DIR):
        shutil.rmtree(SAVE_DIR)

def get_uploaded_data_paths():
    """
    Returns the uploaded file paths for activity and temperature data.
    This function retrieves the saved paths from the configuration.
    """
    config = load_config()
    return config.get('activity_levels_file_path'), config.get('temperature_analysis_file_path')

class UploadDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Upload Data")
        self.root.configure(bg='black')

        self.config = load_config()

        self.activity_levels_file_path = self.config.get('activity_levels_file_path')
        self.temperature_analysis_file_path = self.config.get('temperature_analysis_file_path')

        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.create_upload_buttons()
        self.create_view_buttons()
        self.create_save_button()

        self.update_view_buttons_state()
        self.update_save_button_state()  # Update save button state initially

        self.center_window(600, 300, 180)

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
            'width': 20,
            'height': 2
        }

    def create_upload_buttons(self):
        self.upload_activity_button = tk.Button(self.main_frame, text="Upload Daily Activity Data", command=self.upload_activity_data, **self.button_style())
        self.upload_activity_button.grid(row=0, column=0, padx=20, pady=10)

        self.upload_temperature_button = tk.Button(self.main_frame, text="Upload Temperature Data", command=self.upload_temperature_data, **self.button_style())
        self.upload_temperature_button.grid(row=0, column=1, padx=20, pady=10)

    def create_view_buttons(self):
        self.view_activity_button = tk.Button(self.main_frame, text="View Daily Activity Data", command=self.view_activity_data, state=tk.DISABLED, **self.button_style())
        self.view_activity_button.grid(row=1, column=0, padx=20, pady=10)

        self.view_temperature_button = tk.Button(self.main_frame, text="View Temperature Data", command=self.view_temperature_data, state=tk.DISABLED, **self.button_style())
        self.view_temperature_button.grid(row=1, column=1, padx=20, pady=10)

    def create_save_button(self):
        self.save_button = tk.Button(self.main_frame, text="Continue", command=self.save_data, bg='#00254d', fg='white', font=('Helvetica', 11, 'bold'), width=10, height=2, bd=0, highlightthickness=0, state=tk.DISABLED)
        self.save_button.grid(row=2, column=0, columnspan=2, pady=20)

    def center_window(self, width, height, x_offset=0):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2) + x_offset
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def upload_activity_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.activity_levels_file_path = file_path
            self.config['activity_levels_file_path'] = file_path
            save_config(self.config)
            self.view_activity_button.config(state=tk.NORMAL)
            self.update_save_button_state()

    def upload_temperature_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.temperature_analysis_file_path = file_path
            self.config['temperature_analysis_file_path'] = file_path
            save_config(self.config)
            self.view_temperature_button.config(state=tk.NORMAL)
            self.update_save_button_state()

    def view_activity_data(self):
        if self.activity_levels_file_path:
            os.startfile(self.activity_levels_file_path)

    def view_temperature_data(self):
        if self.temperature_analysis_file_path:
            os.startfile(self.temperature_analysis_file_path)

    def update_view_buttons_state(self):
        if self.activity_levels_file_path:
            self.view_activity_button.config(state=tk.NORMAL)
        if self.temperature_analysis_file_path:
            self.view_temperature_button.config(state=tk.NORMAL)

    def update_save_button_state(self):
        if self.activity_levels_file_path and self.temperature_analysis_file_path:
            self.save_button.config(state=tk.NORMAL)
        else:
            self.save_button.config(state=tk.DISABLED)

    def save_data(self):
        os.makedirs(SAVE_DIR, exist_ok=True)
        try:
            if self.activity_levels_file_path:
                shutil.copy(self.activity_levels_file_path, os.path.join(SAVE_DIR, 'activity_levels.csv'))
            if self.temperature_analysis_file_path:
                shutil.copy(self.temperature_analysis_file_path, os.path.join(SAVE_DIR, 'temperature_data.csv'))
            custom_error_messagebox("Thank You!", "Please note that once the application is closed, your data will be automatically deleted.", self.root)
            self.root.destroy()
        except Exception as e:
            custom_error_messagebox("Error", str(e), self.root)
