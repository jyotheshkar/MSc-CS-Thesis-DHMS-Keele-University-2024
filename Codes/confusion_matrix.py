import tkinter as tk
from main import style_button


def style_button(button):
    button.config(
        bg='#222222',  # Set the main background color
        fg='white',  # Set the text color to white
        font=('Helvetica', 11),  # Normal font size for side buttons
        activebackground='#00254d',  # Set the active background color
        activeforeground='white',  # Set the active text color
        bd=0,  # No border
        highlightthickness=2,  # Highlight thickness
        highlightcolor='blue',  # Highlight color
        highlightbackground='blue',  # Highlight border color
        width=25,  # Normal width for side buttons
        height=2  # Normal height for side buttons
    )


def display_table(right_frame):
    # Create a new frame for the button inside the right_frame (under the buttons)
    table_frame = tk.Frame(right_frame, bg='black')
    table_frame.pack(side=tk.BOTTOM, pady=(5, 5), padx=(10, 10))  # Adjust padding as needed

    # Create the "View Results" button
    view_results_btn = tk.Button(table_frame, text="View Results")

    # Use the existing style_button function to apply the same styling as the other buttons
    style_button(view_results_btn)

    # Attach the button to the frame
    view_results_btn.pack(fill=tk.X)

    # Optionally, you can add functionality for the button
    def on_view_results_click():
        print("View Results button clicked!")
        # Add your logic here for viewing results

    # Set the command for the button
    view_results_btn.config(command=on_view_results_click)
