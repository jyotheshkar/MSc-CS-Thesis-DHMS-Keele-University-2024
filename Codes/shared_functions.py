import tkinter as tk
from tkinter import filedialog
import os

# Function to show a loading window
def show_loading_window():
    loading_window = tk.Toplevel()
    loading_window.title("Loading")
    loading_window.geometry("200x100")
    loading_window.configure(bg='black')

    label = tk.Label(loading_window, text="Please wait...", font=("Helvetica", 12), bg='black', fg='white')
    label.pack(pady=20)

    # Disable closing of the window
    loading_window.protocol("WM_DELETE_WINDOW", lambda: None)

    # Center the loading window on the screen
    loading_window.update_idletasks()
    width = loading_window.winfo_width()
    height = loading_window.winfo_height()
    x = (loading_window.winfo_screenwidth() // 2) - (width // 2)
    y = (loading_window.winfo_screenheight() // 2) - (height // 2)
    loading_window.geometry(f'{width}x{height}+{x}+{y}')

    return loading_window

# Function to style buttons in a consistent way
def style_button(button):
    button.config(
        bg='#222222',  # Set the main background color
        fg='white',  # Set the text color to white
        font=('Helvetica', 11),  # Font size
        activebackground='#00254d',  # Active background color
        activeforeground='white',  # Active text color
        bd=0,  # No border
        highlightthickness=2,  # Highlight thickness
        highlightcolor='blue',  # Highlight color
        highlightbackground='blue',  # Highlight border color
        width=15,  # Width
        height=2  # Height
    )

# Function to show a window where users can enter a Cow ID and select an action (Reload or Retrain)
def show_input_window_with_choices(title, callback):
    input_window = tk.Toplevel()
    input_window.title(title)
    input_window.geometry("400x200")
    input_window.configure(bg='black')

    # Label for instructions
    label = tk.Label(input_window, text="Enter Cow ID", font=("Helvetica", 12), bg='black', fg='white')
    label.pack(pady=10)

    # Entry field for Cow ID
    cow_id_entry = tk.Entry(input_window, font=("Helvetica", 12), bg='#333333', fg='white', insertbackground='white')
    cow_id_entry.pack(pady=10)

    # Radio buttons for action selection (Reload or Retrain)
    action_selected = tk.StringVar(value="reload")

    reload_button = tk.Radiobutton(input_window, text="Reload Model", variable=action_selected, value="reload", bg='black', fg='white', selectcolor='#333333', font=("Helvetica", 11))
    reload_button.pack(pady=5)

    retrain_button = tk.Radiobutton(input_window, text="Retrain Model", variable=action_selected, value="retrain", bg='black', fg='white', selectcolor='#333333', font=("Helvetica", 11))
    retrain_button.pack(pady=5)

    # Continue button
    def submit_input():
        cow_id = cow_id_entry.get()
        action = action_selected.get()
        if cow_id:
            input_window.destroy()
            callback(cow_id, action)  # Pass cow_id and action to callback
        else:
            print("Please enter a valid Cow ID")

    continue_button = tk.Button(input_window, text="Continue", command=submit_input, font=("Helvetica", 12), bg='#00254d', fg='white')
    continue_button.pack(pady=10)

    # Style the button
    style_button(continue_button)

    return input_window

# Function to open the input window for uploading a new dataset and entering Cow ID
def open_input_window_upload(root, title, cow_id_callback):
    input_window = tk.Toplevel(root)
    input_window.title(title)
    input_window.geometry("400x200")
    input_window.configure(bg='black')

    # Label for instructions
    label = tk.Label(input_window, text="Upload Dataset and Enter Cow ID", font=("Helvetica", 12), bg='black', fg='white')
    label.pack(pady=10)

    # Button to upload dataset
    def upload_file():
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            uploaded_file_label.config(text=f"Uploaded: {os.path.basename(file_path)}")
            upload_file.file_path = file_path  # Store the file path in the function attribute

    upload_button = tk.Button(input_window, text="Upload Dataset", command=upload_file, font=("Helvetica", 12), bg='#00254d', fg='white')
    upload_button.pack(pady=10)

    uploaded_file_label = tk.Label(input_window, text="No file uploaded", font=("Helvetica", 10), bg='black', fg='white')
    uploaded_file_label.pack(pady=5)

    # Entry field for Cow ID
    cow_id_label = tk.Label(input_window, text="Enter Cow ID:", font=("Helvetica", 12), bg='black', fg='white')
    cow_id_label.pack(pady=10)

    cow_id_entry = tk.Entry(input_window, font=("Helvetica", 12), bg='#333333', fg='white', insertbackground='white')
    cow_id_entry.pack(pady=10)

    # Continue button
    def submit_input():
        cow_id = cow_id_entry.get()
        if hasattr(upload_file, 'file_path') and cow_id:
            input_window.destroy()
            cow_id_callback(cow_id, "retrain", upload_file.file_path)  # Pass cow_id and file path to callback
        else:
            print("Please upload a dataset and enter a valid Cow ID")

    continue_button = tk.Button(input_window, text="Continue", command=submit_input, font=("Helvetica", 12), bg='#00254d', fg='white')
    continue_button.pack(pady=10)

    # Style the button
    style_button(continue_button)

    return input_window
