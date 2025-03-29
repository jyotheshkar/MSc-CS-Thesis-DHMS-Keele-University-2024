import tkinter as tk
from tkinter import ttk

# Function to create a table with 4 rows and 70 columns
def create_table_below_graph(graph_frame):
    # Create a frame for the table inside the graph_frame
    table_frame = tk.Frame(graph_frame, bg='black')
    table_frame.pack(side=tk.TOP, fill=tk.X, padx=(10, 10), pady=(5, 5))

    # Define columns dynamically for 70 columns
    columns = [f"Column {i+1}" for i in range(70)]
    table = ttk.Treeview(table_frame, columns=columns, show='headings', height=4)

    # Configure columns
    for col in columns:
        table.column(col, width=30, anchor="center")  # Adjust column width for each column

    # Configure headings
    for col in columns:
        table.heading(col, text=col)

    # Insert 4 rows with dummy data
    for row in range(4):
        values = [f"Row {row+1}, Col {i+1}" for i in range(70)]
        table.insert("", tk.END, values=values)

    # Apply black background and white text for cells
    style = ttk.Style()
    style.configure("Treeview", 
                    background="#000000",  # Black background for cells
                    foreground="white",  # White text
                    fieldbackground="#000000",  # Black background for fields
                    rowheight=30)  # Adjust row height

    style.configure("Treeview.Heading", 
                    background="#000000",  # Black background for headings
                    foreground="white",  # White text for headings
                    relief="solid")

    # Pack the table into the frame
    table.pack(fill=tk.X)

