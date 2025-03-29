
# # leftbuttons.py

import tkinter as tk
from tkinter import filedialog
import json
import os
import shutil
from utils import custom_error_messagebox
from visualizebutton import open_visualize_data  


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
        self.save_button = tk.Button(self.main_frame, text="Save", command=self.save_data, bg='#2e8b57', fg='white', font=('Helvetica', 11, 'bold'), width=10, height=2, bd=0, highlightthickness=0, state=tk.DISABLED)
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
            self.update_save_button_state()  # Update save button state

    def upload_temperature_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.temperature_analysis_file_path = file_path
            self.config['temperature_analysis_file_path'] = file_path
            save_config(self.config)
            self.view_temperature_button.config(state=tk.NORMAL)
            self.update_save_button_state()  # Update save button state

    def view_activity_data(self):
        if self.activity_levels_file_path is not None:
            os.startfile(self.activity_levels_file_path)

    def view_temperature_data(self):
        if self.temperature_analysis_file_path is not None:
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
            custom_error_messagebox("Save", "Data saved successfully!", self.root)
            self.root.destroy()
        except ValueError as e:
            custom_error_messagebox("Error", str(e), self.root)

def create_buttons(parent_frame, left_plot_frame, right_plot_frame):
    button_frame = tk.Frame(parent_frame, bg='black')
    button_frame.pack(side=tk.BOTTOM, anchor='sw', padx=10, pady=5)

    button_config = {
        'bg': '#555555',
        'fg': 'white',
        'font': ("Helvetica", 11),
        'width': 16,
        'height': 2,
        'bd': 0,
        'highlightthickness': 2,
        'highlightcolor': 'blue',
        'highlightbackground': 'blue',
        'activebackground': '#777777',
        'activeforeground': 'white'
    }

    def open_upload_data():
        upload_data_window = tk.Toplevel(parent_frame)
        app = UploadDataApp(upload_data_window)
        upload_data_window.transient(parent_frame)
        upload_data_window.grab_set()
        parent_frame.wait_window(upload_data_window)

    upload_button = tk.Button(button_frame, text="Upload Data", command=open_upload_data, **button_config)
    visualize_button = tk.Button(button_frame, text="Visualize Data", command=lambda: open_visualize_data(parent_frame, left_plot_frame, right_plot_frame), **button_config)
    download_button = tk.Button(button_frame, text="Download Report", **button_config)

    upload_button.grid(row=0, column=0, padx=10, pady=10)
    visualize_button.grid(row=0, column=1, padx=10, pady=10)
    download_button.grid(row=1, column=1, padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: [delete_files(), root.destroy()])
    create_buttons(root, None, None)
    root.mainloop()
