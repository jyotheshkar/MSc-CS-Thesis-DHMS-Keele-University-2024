import tkinter as tk
from tkinter import Toplevel

def center_window(window, width, height):
    # Get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate x and y coordinates for the window to be centered
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Set the window size and position
    window.geometry(f'{width}x{height}+{x}+{y}')

def show_message(button_name):
    # Create a new top-level window
    message_window = Toplevel()
    message_window.title(button_name)
    
    # Center the window on the screen
    center_window(message_window, 300, 150)
    
    # Display the button name and a Continue button
    label = tk.Label(message_window, text=button_name, font=("Helvetica", 14))
    label.pack(pady=10)
    
    continue_button = tk.Button(message_window, text="Continue", command=message_window.destroy)
    continue_button.pack(pady=10)

def create_buttons(parent_frame):
    # Create a frame for the buttons
    button_frame = tk.Frame(parent_frame, bg='black')
    button_frame.pack(side=tk.BOTTOM, anchor='se', padx=10, pady=5)

    # Button configuration
    button_config = {
        'bg': '#555555',  # Button background color
        'fg': 'white',    # Button text color
        'font': ("Helvetica", 11),  # Reduced font size
        'width': 16,  # Reduced width
        'height': 2,  # Reduced height
        'bd': 0,
        'highlightthickness': 2,
        'highlightcolor': 'blue',
        'highlightbackground': 'blue',
        'activebackground': '#777777',
        'activeforeground': 'white'
    }

    # Create the buttons
    upload_button = tk.Button(button_frame, text="Daily Activity levels", **button_config, command=lambda: show_message("Daily Activity levels"))
    visualize_button = tk.Button(button_frame, text="Temperature Analysis", **button_config, command=lambda: show_message("Temperature Analysis"))
    extra_button = tk.Button(button_frame, text="Overall Analysis", **button_config, command=lambda: show_message("Overall Analysis"))

    # Arrange the buttons in a grid
    upload_button.grid(row=0, column=0, padx=10, pady=10)
    visualize_button.grid(row=0, column=1, padx=10, pady=10)
    extra_button.grid(row=1, column=0, padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Main Window")

    # Center the main window on the screen
    center_window(root, 600, 400)  # Adjust width and height as needed

    create_buttons(root)

    root.mainloop()
