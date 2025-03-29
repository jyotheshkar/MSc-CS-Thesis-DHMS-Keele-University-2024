
import tkinter as tk
from tkinter import StringVar, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import mplcursors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data_utils import get_uploaded_data_paths  # Assuming get_uploaded_data_paths is defined in upload_data.py


# Function to style the buttons with a fixed color for both enabled and disabled states
def style_button(button, state='normal', active_color='#555555', disabled_color='#222222'):
    button.config(
        bg=active_color if state == 'normal' else disabled_color,
        fg='white',
        font=('Helvetica', 11),
        activebackground=active_color,
        activeforeground='white',
        bd=0,
        highlightthickness=2,
        highlightcolor='blue',
        highlightbackground='blue',
        width=int(20 * 1.2),
        height=2,  # Normal button height
        state=state
    )

# Function to style the "Continue" button separately with increased height
def style_continue_button(button, state='disabled'):
    button.config(
        bg='#00254d',  # Continue button background color
        fg='white',
        font=('Helvetica', 11, 'bold'),
        width=10,
        height=3,  # Increased height for the "Continue" button only
        bd=0,
        highlightthickness=0,
        state=state
    )

# Function to center the window on the screen with a right offset of 11.5%
def center_window(window):
    window.update_idletasks()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width // 2) - (window_width // 2)
    x += int(screen_width * 0.115)
    y = (screen_height // 2) - (window_height // 2)

    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Function to normalize the data when "Preprocessed Data" is selected
def normalize_data(df):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df)
    normalized_df = pd.DataFrame(scaled_data, columns=df.columns, index=df.index)
    return normalized_df

# Function to visualize the selected data on the main frame
def visualize_data_on_canvas(frame, data_type, cow_id=None, preprocessed=False):
    # Retrieve uploaded file paths from the configuration
    activity_data_path, temperature_data_path = get_uploaded_data_paths()

    # Check if the appropriate data file is available
    if data_type == "activity":
        data_path = activity_data_path
        title = "Activity Data"
    else:
        data_path = temperature_data_path
        title = "Temperature Data"

    if not data_path:
        messagebox.showerror("Error", f"Please upload the {data_type} CSV file.")
        return

    # Load the data
    try:
        df = pd.read_csv(data_path)
        df.set_index('Unnamed: 0', inplace=True)
        df.index = pd.to_datetime(df.index)

        if preprocessed:
            df = normalize_data(df)

        # Convert index to sequential numbers for x-axis
        df.index = range(len(df))

        plt.style.use('dark_background')

        fig, ax = plt.subplots(figsize=(8, 6))

        if cow_id and cow_id.lower() == "herd":
            group_column = 'Group mean' if data_type == "activity" else ' Group mean'
            if group_column in df.columns:
                ax = df[[group_column]].plot(
                    ax=ax,
                    title=f"{title} - Group Mean",
                    color='red',
                    linewidth=0.5,
                    marker='o',
                    markersize=4
                )
            else:
                messagebox.showinfo("Column Not Found", f"'{group_column}' column not found in the dataset.")
                return
        elif cow_id and cow_id in df.columns:
            ax = df[[cow_id]].plot(
                ax=ax,
                title=f"{title} for Cow ID: {cow_id}",
                color='cyan',
                linewidth=0.5,
                marker='o',
                markersize=4
            )
        else:
            messagebox.showinfo("No Data", f"No data found for Cow ID: {cow_id}")
            return

        # Customize the tooltip
        cursor = mplcursors.cursor(ax, hover=True)
        cursor.connect(
            "add",
            lambda sel: (
                sel.annotation.set_text(f"Index: {int(sel.index)}\nValue: {sel.target[1]:.2f}"),
                sel.annotation.get_bbox_patch().set(fc="black", ec="white", lw=1.5, alpha=1.0),  # Fully opaque black background and white border
                sel.annotation.arrow_patch.set(arrowstyle="simple", fc="white", ec="white", lw=1.5),  # Arrow as white
                sel.annotation.set_color('white')  # Set text to white
            )
        )

        # Clear the left_frame and attach the graph to the frame
        for widget in frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    except Exception as e:
        messagebox.showerror("Error", f"Error loading data: {e}")

# Main application window setup
def open_visualize_uploaded_data(root, left_frame):
    # Create a new window
    visualize_window = tk.Toplevel(root)
    visualize_window.title("Visualize Data")
    visualize_window.configure(bg='black')

    # Set a default window size first
    visualize_window.geometry("600x320")

    # Create a container frame with padding to manage the inner content
    content_frame = tk.Frame(visualize_window, bg='black')
    content_frame.pack(expand=True, pady=(20, 20))

    # Cow ID and Entire Herd buttons and input field
    cow_id_var = StringVar()

    cow_id_frame = tk.Frame(content_frame, bg='black')
    cow_id_frame.pack(pady=10)

    cow_id_label = tk.Label(cow_id_frame, text="Cow ID:", fg='white', bg='#000000', font=('Helvetica', 11), height=2, width=9)
    cow_id_label.grid(row=0, column=0, padx=5)

    # Validate that only numbers can be entered into the Cow ID field
    def validate_input(P):
        if P.isdigit() or P == "":
            return True
        return False

    vcmd = (root.register(validate_input), '%P')

    cow_id_entry = tk.Entry(
        cow_id_frame,
        textvariable=cow_id_var,
        font=('Helvetica', 11),
        validate='key',
        validatecommand=vcmd,
        width=15,
        bd=3,
        insertwidth=2,
    )
    cow_id_entry.grid(row=0, column=1, padx=10, pady=10, ipady=8)

    # Bind the event inside the valid scope of the entry widget
    cow_id_entry.bind("<KeyRelease>", lambda event: enable_buttons("cow_id"))

    entire_herd_button = tk.Button(cow_id_frame, text="Entire Herd", command=lambda: reset_all("herd"))
    style_button(entire_herd_button, 'normal')
    entire_herd_button.grid(row=0, column=2, padx=10)

    button_frame = tk.Frame(content_frame, bg='black')
    button_frame.pack()

    raw_data_button = tk.Button(button_frame, text="Visualize Raw Data", state='disabled', command=lambda: select_top_button("raw"))
    preprocessed_data_button = tk.Button(button_frame, text="Visualize Preprocessed Data", state='disabled', command=lambda: select_top_button("preprocessed"))

    style_button(raw_data_button, 'disabled')
    style_button(preprocessed_data_button, 'disabled')

    raw_data_button.grid(row=0, column=0, padx=10, pady=10)
    preprocessed_data_button.grid(row=0, column=1, padx=10, pady=10)

    activity_data_button = tk.Button(button_frame, text="Activity Data", state='disabled', command=lambda: select_bottom_button("activity"))
    temperature_data_button = tk.Button(button_frame, text="Temperature Data", state='disabled', command=lambda: select_bottom_button("temperature"))

    style_button(activity_data_button, 'disabled')
    style_button(temperature_data_button, 'disabled')

    activity_data_button.grid(row=1, column=0, padx=10, pady=10)
    temperature_data_button.grid(row=1, column=1, padx=10, pady=10)

    continue_button = tk.Button(content_frame, text="Continue", state='disabled', command=lambda: execute_visualization_and_close())

    style_continue_button(continue_button, 'disabled')
    continue_button.pack(pady=(20, 20))  # Adjusted padding for visibility

    def reset_all(selection):
        cow_id_var.set("")
        style_button(raw_data_button, 'disabled')
        style_button(preprocessed_data_button, 'disabled')
        style_button(activity_data_button, 'disabled')
        style_button(temperature_data_button, 'disabled')
        style_continue_button(continue_button, 'disabled')

        if selection == "herd":
            cow_id_var.set("herd")
            enable_buttons("herd")

    def enable_buttons(selection):
        if selection == "herd":
            cow_id_var.set("herd")
            cow_id_entry.config(state='disabled')
        else:
            cow_id_entry.config(state='normal')

        if selection == "herd" or (len(cow_id_var.get()) == 4 and cow_id_var.get().isdigit()):
            style_button(raw_data_button, 'normal')
            style_button(preprocessed_data_button, 'normal')
        else:
            style_button(raw_data_button, 'disabled')
            style_button(preprocessed_data_button, 'disabled')
            style_button(activity_data_button, 'disabled')
            style_button(temperature_data_button, 'disabled')
            style_continue_button(continue_button, 'disabled')

    def select_top_button(data_type):
        # Reset both buttons to normal state before selecting one
        raw_data_button.config(bg='#555555')
        preprocessed_data_button.config(bg='#555555')

        # Highlight the selected button
        if data_type == "raw":
            raw_data_button.config(bg='#00254d')  # Active color for selected
            preprocessed_data_button.config(bg='#555555')  # Reset color for the other
        else:
            preprocessed_data_button.config(bg='#6f0000')
            raw_data_button.config(bg='#555555')

        enable_bottom_buttons()

    def enable_bottom_buttons():
        style_button(activity_data_button, 'normal')
        style_button(temperature_data_button, 'normal')

    def select_bottom_button(data_type):
        style_button(activity_data_button, 'normal')
        style_button(temperature_data_button, 'normal')

        if data_type == "activity":
            activity_data_button.config(bg='#00254d')
            temperature_data_button.config(bg='#555555')
        else:
            temperature_data_button.config(bg='#6f0000')
            activity_data_button.config(bg='#555555')

        enable_continue_button()

    def enable_continue_button():
        style_continue_button(continue_button, 'normal')

    def execute_visualization_and_close():
        # Check which button was selected based on the background color
        data_type = "raw" if raw_data_button.cget("bg") == '#00254d' else "preprocessed"
        selected_data_type = "activity" if activity_data_button.cget("bg") == '#00254d' else "temperature"

        # Call the function to visualize data on the canvas
        visualize_data_on_canvas(left_frame, selected_data_type, cow_id_var.get(), preprocessed=(data_type == "preprocessed"))

        # Close the window after visualization
        visualize_window.destroy()

    visualize_window.after(0, lambda: center_window(visualize_window))

# Example usage in a standalone mode
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Main Window")
    root.geometry("600x320")
    root.configure(bg='black')

    button_container = tk.Frame(root, bg='black')
    button_container.pack(pady=20)

    left_frame = tk.Frame(root, bg='black')
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    btn = tk.Button(button_container, text="Open Visualize Window", command=lambda: open_visualize_uploaded_data(root, left_frame))
    style_button(btn, 'normal')
    btn.pack(pady=20)

    root.mainloop()
