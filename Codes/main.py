
# main.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt  # Importing matplotlib for global settings

# Set global style for matplotlib
plt.style.use('default')

# Update rcParams for global configuration
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'savefig.facecolor': 'white',
    'axes.edgecolor': 'black',
    'axes.labelcolor': 'black',
    'xtick.color': 'black',
    'ytick.color': 'black',
    'grid.color': 'black',
    'text.color': 'black',
    'axes.titlecolor': 'black',
})

# Continue with the rest of your imports and code...
from originalgraph import create_plot
from upload_data import UploadDataApp  # Ensure this is correctly imported
from Generic_Activity_Model import generate_activity_model_graph
from Generic_Temp_Model import generate_temperature_model_graph
from Generic_Multi_Model import generate_multi_model_graph  # Ensure this points to the multi-model file
from BeSpoke_Activity_model import generate_bespoke_activity_model_graph
from BeSpoke_Temp_Model import generate_bespoke_temp_model_graph
# from BeSpoke_Multimodel import generate_bespoke_multi_model_graph
from visualize_uploaded_data import open_visualize_uploaded_data  # Import the function for data visualization
import shutil


# Path for the config file
CONFIG_FILE = 'upload_config.json'
SAVE_DIR = 'saved_upload_data'

# Function to delete the config file
def delete_config_file_and_data():
    # Delete the config file
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    
    # Delete the saved data directory
    if os.path.exists(SAVE_DIR):
        shutil.rmtree(SAVE_DIR)

# Function to close the main application and delete the config file and data
def on_close():
    delete_config_file_and_data()  # Delete the config file and saved data before closing
    root.destroy()

# Function to display the GIF in the frame
def display_gif_in_frame(frame, gif_filename):
    gif_label = tk.Label(frame, bg='black')
    gif_label.pack(fill=tk.BOTH, expand=True)

    # Use os.path.join to construct the full path to the gif
    gif_path = os.path.join(os.path.dirname(__file__), 'photo', gif_filename)

    gif_image = Image.open(gif_path)
    gif_frames = [ImageTk.PhotoImage(img.copy().resize((384, 192), Image.LANCZOS)) for img in ImageSequence.Iterator(gif_image)]

    gif_label.frames = gif_frames
    gif_label.current_frame = 0

    def update_gif():
        gif_label.config(image=gif_label.frames[gif_label.current_frame])
        gif_label.image = gif_label.frames[gif_label.current_frame]
        gif_label.current_frame = (gif_label.current_frame + 1) % len(gif_label.frames)
        gif_label.after(100, update_gif)

    update_gif()

    return gif_label


# Function to show input window for Cow ID centered relative to the main window
def show_input_window(label_text, cow_id_callback):
    input_window = tk.Toplevel(root)
    input_window.title(f"Enter {label_text}")
    input_window.geometry("300x150")
    input_window.configure(bg='black')

    # Position the window relative to the main window
    root.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    window_width = 300
    window_height = 150

    x = root_x + (root_width // 2) - (window_width // 2)
    y = root_y + (root_height // 2) - (window_height // 2)

    input_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Label for input
    label = tk.Label(input_window, text=f"Please enter {label_text}:", font=("Helvetica", 12), bg='black', fg='white')
    label.pack(pady=10)

    # Entry field for Cow ID
    input_entry = tk.Entry(input_window, font=("Helvetica", 12), bg='#333333', fg='white', insertbackground='white', relief=tk.FLAT, borderwidth=2)
    input_entry.pack(pady=10, padx=20, fill=tk.X)

    # Continue button
    def submit_input():
        cow_id = input_entry.get()
        input_window.destroy()
        cow_id_callback(cow_id)  # Pass the cow_id to the callback function

    submit_button = tk.Button(input_window, text="Continue", command=submit_input, font=("Helvetica", 11))
    style_button(submit_button)
    submit_button.config(bg='#00254d', width=15, height=2)
    submit_button.pack(pady=10)

    input_window.protocol("WM_DELETE_WINDOW", lambda: input_window.destroy())

# Function to style buttons with active background color (for the side buttons)
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

# Function to attach the new graph to the canvas
def attach_plot_to_canvas(fig, frame):
    # Clear the frame (this removes any previous graph)
    for widget in frame.winfo_children():
        widget.destroy()

    # Attach the new graph to the tkinter frame
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Function to handle the save model pop-up after graph generation

# Function to handle the save model pop-up after graph generation
def prompt_save_model(model_folder, model):
    save_window = tk.Toplevel(root)
    save_window.title("Save Model")
    save_window.geometry("600x200")
    save_window.configure(bg='black')

    label = tk.Label(save_window, text="Would you like to save the model?", font=("Helvetica", 12), bg='black', fg='white')
    label.pack(pady=10)

    entry_label = tk.Label(save_window, text="Enter folder name:", font=("Helvetica", 12), bg='black', fg='white')
    entry_label.pack(pady=10)

    folder_name_entry = tk.Entry(save_window, font=("Helvetica", 12), bg='#333333', fg='white', insertbackground='white', relief=tk.FLAT, borderwidth=2)
    folder_name_entry.pack(pady=10, padx=20, fill=tk.X)

    def save_model():
        folder_name = folder_name_entry.get().strip()
        if not folder_name:
            messagebox.showerror("Error", "Please enter a folder name.")
            return

        new_folder_path = os.path.join(model_folder, folder_name)

        try:
            os.makedirs(new_folder_path, exist_ok=True)
            model.save(os.path.join(new_folder_path, "lstm_model.h5"))
            messagebox.showinfo("Save Model", f"Model saved successfully in:\n{new_folder_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save model: {str(e)}")

        save_window.destroy()

    save_button = tk.Button(save_window, text="Save", command=save_model, font=("Helvetica", 12))
    style_button(save_button)
    save_button.config(bg='#00254d', width=15, height=2)
    save_button.pack(pady=10)



# Generic function to handle both models
import tkinter as tk
from tkinter import messagebox, Scrollbar, Canvas

def show_model_train_or_reload_popup(model_type, generate_model_func, model_folder):
    popup_window = tk.Toplevel(root)
    popup_window.title(f"Choose Action for {model_type}")
    popup_window.geometry("600x200")  # Set the size of the window
    popup_window.configure(bg='black')

    # Center the window on the screen
    popup_window.update_idletasks()
    width = popup_window.winfo_width()
    height = popup_window.winfo_height()
    x = (popup_window.winfo_screenwidth() // 2) - (width // 2)
    y = (popup_window.winfo_screenheight() // 2) - (height // 2)
    popup_window.geometry(f'{width}x{height}+{x}+{y}')

    label = tk.Label(popup_window, text=f"Would you like to train or reload the {model_type}?", font=("Helvetica", 12), bg='black', fg='white')
    label.pack(pady=10)

    # Frame for buttons
    button_frame = tk.Frame(popup_window, bg='black')
    button_frame.pack(pady=10)

    def train_model():
        popup_window.destroy()
        gif_label = display_gif_in_frame(left_frame, 'play.gif')


        def generate_and_show_graph():
            generate_model_func(left_frame, lambda: btn.config(state=tk.NORMAL, bg='#00254d'), prompt_save_model)
            gif_label.destroy()

        left_frame.after(1000, generate_and_show_graph)

    def reload_model():
        popup_window.destroy()
        gif_label = display_gif_in_frame(left_frame, 'play.gif')


        def generate_and_show_graph():
            show_reload_model_popup(model_folder, generate_model_func)
            gif_label.destroy()

        left_frame.after(1000, generate_and_show_graph)

    # Train Button
    train_button = tk.Button(button_frame, text=f"Train {model_type}", command=train_model, font=("Helvetica", 12))
    style_button(train_button)
    train_button.config(width=25)
    train_button.grid(row=0, column=0, padx=10)

    # Reload Button
    reload_button = tk.Button(button_frame, text=f"Reload {model_type}", command=reload_model, font=("Helvetica", 12))
    style_button(reload_button)
    reload_button.config(width=25)
    reload_button.grid(row=0, column=1, padx=10)



def show_reload_model_popup(model_folder, generate_model_func):
    reload_window = tk.Toplevel(root)
    reload_window.title(f"Reload Model from {model_folder}")
    reload_window.geometry("600x400")  # Set the size of the window
    reload_window.configure(bg='black')

    # Center the window on the screen
    reload_window.update_idletasks()
    width = reload_window.winfo_width()
    height = reload_window.winfo_height()
    x = (reload_window.winfo_screenwidth() // 2) - (width // 2)
    y = (reload_window.winfo_screenheight() // 2) - (height // 2)
    reload_window.geometry(f'{width}x{height}+{x}+{y}')

    label = tk.Label(reload_window, text=f"Select a saved model to reload from {model_folder}:", font=("Helvetica", 12), bg='black', fg='white')
    label.pack(pady=10)

    # Create a frame with a scrollbar
    container = tk.Frame(reload_window, bg='black')
    container.pack(fill=tk.BOTH, expand=True)

    canvas = Canvas(container, bg='black')
    scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='black')

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    if os.path.exists(model_folder):
        folders = [folder for folder in os.listdir(model_folder) if os.path.isdir(os.path.join(model_folder, folder))]
        for folder in folders:
            folder_button = tk.Button(scrollable_frame, text=folder, command=lambda f=folder: reload_selected_model(f, model_folder, generate_model_func), font=("Helvetica", 12))
            style_button(folder_button)
            folder_button.config(width=40)
            folder_button.pack(fill=tk.X, pady=5, padx=20)
    else:
        messagebox.showerror("Error", f"Directory {model_folder} does not exist!")



def reload_selected_model(folder, model_folder, generate_model_func):
    selected_model_folder = os.path.join(model_folder, folder)
    if os.path.exists(selected_model_folder):
        print(f"Reloading model from {selected_model_folder}")
        generate_model_func(left_frame, lambda: btn.config(state=tk.NORMAL, bg='#00254d'), None, selected_model_folder)
    else:
        print(f"Model folder {selected_model_folder} does not exist!")

# Function to handle the activity model popup
def show_activity_model_popup():
    show_model_train_or_reload_popup(
        "Activity Model",
        generate_activity_model_graph,
        "Generic-Activity-inputs LSTM-model"
    )

# Function to handle the temperature model popup
def show_temperature_model_popup():
    show_model_train_or_reload_popup(
        "Temperature Model",
        generate_temperature_model_graph,
        "Generic-Temperature-inputs LSTM-model"
    )

# Function to handle the multi model popup
def show_multi_model_popup():
    show_model_train_or_reload_popup(
        "Multi Model",
        generate_multi_model_graph,
        "Generic-MultiModel-LSTM-model"
    )

# Bespoke Graph Generation Functions
def start_bespoke_activity_graph(button, frame, cow_id):
    for widget in frame.winfo_children():
        widget.destroy()

    gif_label = display_gif_in_frame(left_frame, 'play.gif')


    def generate_and_show_graph():
        generate_bespoke_activity_model_graph(frame, cow_id, button)
        gif_label.destroy()

    frame.after(1000, generate_and_show_graph)
    button.config(state=tk.NORMAL, bg='#00254d')

def start_bespoke_temp_model_graph(button, frame, temp_id):
    for widget in frame.winfo_children():
        widget.destroy()

    gif_label = display_gif_in_frame(left_frame, 'play.gif')


    def generate_and_show_graph():
        generate_bespoke_temp_model_graph(frame, temp_id, button)
        gif_label.destroy()

    frame.after(1000, generate_and_show_graph)
    button.config(state=tk.NORMAL, bg='#00254d')

# def start_bespoke_multi_model_graph(button, frame, cow_id):
#     for widget in frame.winfo_children():
#         widget.destroy()

#     gif_label = display_gif_in_frame(frame, 'photo/play.gif')

#     def generate_and_show_graph():
#         generate_bespoke_multi_model_graph(frame, cow_id, button)
#         gif_label.destroy()

#     frame.after(1000, generate_and_show_graph)
#     button.config(state=tk.NORMAL, bg='#00254d')

# Function to open the Upload Data window
def open_upload_data():
    upload_data_window = tk.Toplevel(root)
    app = UploadDataApp(upload_data_window)
    upload_data_window.transient(root)
    upload_data_window.grab_set()
    root.wait_window(upload_data_window)

# Main application window
root = tk.Tk()
root.title("Time-series Neural Network Software Suite & App Development For Dairy Herd Monitoring")
root.configure(bg='black')

# Set the application icon
icon_image_path = os.path.join(os.path.dirname(__file__), 'photo', 'cowmain.png')
if os.path.exists(icon_image_path):
    icon_image = ImageTk.PhotoImage(file=icon_image_path)
    root.iconphoto(True, icon_image)
else:
    print(f"Icon image not found at path: {icon_image_path}")


root.state('zoomed')

# Top Navbar Frame
top_frame = tk.Frame(root, bg='black')
top_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 10), padx=(10, 10))

# Add an image and label to the navbar
if os.path.exists(icon_image_path):
    image = Image.open(icon_image_path).convert("RGBA")
    image = image.resize((50, 50), Image.LANCZOS)
    image_tk = ImageTk.PhotoImage(image)
    image_label = tk.Label(top_frame, image=image_tk, bg='black')
    image_label.image = image_tk
    image_label.grid(row=0, column=0, padx=(10, 0), pady=(6, 0))

# Navbar Heading
heading_label = tk.Label(top_frame, text="Dairy Herd Monitoring System", bg='black', fg='white', font=("Helvetica", 15))
heading_label.grid(row=0, column=1, padx=(20, 10), pady=(6, 0), sticky='w')

cd1_canvas = tk.Canvas(top_frame, width=80, height=50, bg='black', highlightthickness=0)
cd1_canvas.grid(row=0, column=2, padx=(10, 0), pady=(6, 0), sticky='e')
cd1_canvas.create_rectangle(10, 10, 70, 40, fill='white', outline='black', width=2)
cd1_canvas.create_text(40, 25, text="CD 1", fill='black', font=("Helvetica", 16))

top_frame.grid_columnconfigure(1, weight=1)
top_frame.grid_columnconfigure(2, weight=1)

# Main content frame that holds the graph and buttons
main_frame = tk.Frame(root, bg='black')
main_frame.pack(fill=tk.BOTH, expand=True, padx=(10, 10), pady=(10, 0))

# Left frame for the graph
left_frame = tk.Frame(main_frame, bg='black')
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Right frame for the buttons
right_frame = tk.Frame(main_frame, bg='black')
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, pady=(0, 10))

# Create the dummy graph in the left frame initially
fig, ax = create_plot()
canvas = FigureCanvasTkAgg(fig, master=left_frame)
fig.set_size_inches(8, 6)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Inner frame inside the right_frame to center the buttons vertically using pack
button_container = tk.Frame(right_frame, bg='black')
button_container.pack(expand=True)

# Add buttons with functionality, separated by type
# First group: Visualize + Generic Models
button_labels_generic = [
    ("Upload Data", open_upload_data),
    ("Visualize Uploaded Data", lambda: open_visualize_uploaded_data(root, left_frame)),
    ("Generic Activity ", show_activity_model_popup),
    ("Generic Temperature ", show_temperature_model_popup),  # Use the new temperature popup
    ("Generic Combined", show_multi_model_popup)
]

for label, callback in button_labels_generic:
    frame = tk.Frame(button_container, bg='black')
    frame.pack(fill=tk.X, padx=60, pady=8)

    btn = tk.Button(frame, text=label)
    btn.config(command=callback)  # Assign callback function to button
    
    style_button(btn)
    btn.pack(side=tk.LEFT)

# Add the bespoke buttons with MVP tag to the right_frame
button_labels_bespoke = [
    ("Bespoke Activity Model", "MVP"),
    ("Bespoke Temperature Model", "MVP"),
    # ("Bespoke Multi Model", "MVP"),
]

for label, tag in button_labels_bespoke:
    frame = tk.Frame(button_container, bg='black')
    frame.pack(fill=tk.X, padx=60, pady=8)

    btn = tk.Button(frame, text=label)
    
    if label == "Bespoke Activity Model":
        btn.config(command=lambda: show_input_window("Cow ID", lambda cow_id: start_bespoke_activity_graph(btn, left_frame, cow_id)))
    elif label == "Bespoke Temperature Model":
        btn.config(command=lambda: show_input_window("Temperature Column", lambda temp_id: start_bespoke_temp_model_graph(btn, left_frame, temp_id)))
    # elif label == "Bespoke Multi Model":
    #     btn.config(command=lambda: show_input_window("Cow ID", lambda cow_id: start_bespoke_multi_model_graph(btn, left_frame, cow_id)))
    
    style_button(btn)
    btn.pack(side=tk.LEFT)

    # Add the MVP tag with the original size and darker red color
    if tag:
        tag_label = tk.Label(frame, text=tag, font=("Helvetica", 8, "bold"), fg="white", bg="#8B0000", padx=5, pady=2)
        tag_label.pack(side=tk.LEFT, padx=(10, 0))

# Set the protocol for closing the window
root.protocol("WM_DELETE_WINDOW", on_close)

# Run the main application loop
root.mainloop()




