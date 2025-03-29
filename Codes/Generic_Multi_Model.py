
# # ////////////////////////////////////////////////////////////////////////

# # Generic_Multi_Model.py
# import os
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.preprocessing import MinMaxScaler, LabelEncoder
# from tensorflow.keras.models import Model, load_model, Sequential
# from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, concatenate
# from tensorflow.keras.optimizers import Adam
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import confusion_matrix, mean_absolute_percentage_error, mean_squared_error, accuracy_score, classification_report
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import tkinter as tk
# from tkinter import messagebox
# from sklearn.metrics import confusion_matrix, classification_report
# from tkinter.scrolledtext import ScrolledText
# from upload_data import get_uploaded_data_paths  # Import the function to get file paths


# import matplotlib.pyplot as plt

# plt.style.use('default')


# def display_missing_data_popup():
#     root = tk.Tk()
#     root.withdraw()  # Hide the root window
#     messagebox.showerror("Data Error", "No data uploaded! Please upload the necessary files to proceed.")
#     root.destroy()

# def get_run_folder(base_folder):
#     """Find the next run folder, e.g. MultiModel run 1, MultiModel run 2, etc."""
#     run_number = 1
#     while os.path.exists(os.path.join(base_folder, f'MultiModel run {run_number}')):
#         run_number += 1
#     return os.path.join(base_folder, f'MultiModel run {run_number}')

# def show_report_in_window(report_text, final_alert):
#     # Create a new tkinter window
#     report_window = tk.Toplevel()
#     report_window.title("Confusion Matrix, Classification Report, and Final Alert")

#     # Add a Text widget to display the report
#     text_area = ScrolledText(report_window, wrap=tk.WORD, width=80, height=20, font=("Helvetica", 12))
#     text_area.pack(expand=True, fill=tk.BOTH)
    
#     # Insert the report text into the Text widget
#     text_area.insert(tk.END, report_text)
    
#     # Insert the Final Alert text at the end
#     text_area.insert(tk.END, f"\n\nFinal Alert for the Entire Herd: {final_alert}")
    
#     # Disable editing
#     text_area.config(state=tk.DISABLED)
    
#     # Start the tkinter main loop for the report window
#     report_window.mainloop()

# def generate_confusion_matrix_and_report(y_true, y_pred, labels, target_names):
#     # Ensure y_true and y_pred have all the necessary classes
#     unique_classes_in_y_true = np.unique(y_true)
#     unique_classes_in_y_pred = np.unique(y_pred)
    
#     # Check if we are missing any classes
#     all_classes = np.union1d(unique_classes_in_y_true, unique_classes_in_y_pred)
    
#     # If we are missing any of the specified labels (0, 1, 2 for Green, Orange, Red), ensure they are included
#     if len(all_classes) < len(labels):
#         y_true = np.concatenate([y_true, labels])
#         y_pred = np.concatenate([y_pred, labels])

#     # Generate confusion matrix
#     cm = confusion_matrix(y_true, y_pred, labels=labels)
    
#     # Generate classification report
#     report = classification_report(y_true, y_pred, target_names=target_names, labels=labels, zero_division=0)
    
#     # Determine the final herd alert based on the predictions
#     alert_counts = np.bincount(y_pred, minlength=len(labels))
#     final_alert_idx = np.argmax(alert_counts)
#     final_alert = target_names[final_alert_idx]

#     # Prepare the report text
#     report_text = f"Confusion Matrix:\n{cm}\n\nClassification Report:\n{report}"
    
#     # Display the report and the final alert in a GUI window
#     show_report_in_window(report_text, final_alert)
    
#     return cm, report

# def calculate_rmse_percentage(y_true, y_pred):
#     rmse = np.sqrt(mean_squared_error(y_true, y_pred))
#     max_value = np.max(y_true)
#     return (1 - (rmse / max_value)) * 100 if max_value > 0 else 100

# def generate_multi_model_graph(frame, after_graph_is_loaded, save_callback=None, reload_model_path=None):
#     # Destroy all widgets in the frame to clear previous graphs
#     for widget in frame.winfo_children():
#         widget.destroy()

#     # Folder and model file path
#     model_folder = 'Generic-MultiModel-LSTM-model'

#     if reload_model_path:
#         # Use the reload_model_path to load pre-trained models
#         model_file_path_regression = os.path.join(reload_model_path, 'lstm_multi_input_model_regression.keras')
#         model_file_path_classification = os.path.join(reload_model_path, 'lstm_multi_input_model_classification.keras')

#         print(f"Loading regression model from {model_file_path_regression}")
#         model_regression = load_model(model_file_path_regression)

#         print(f"Loading classification model from {model_file_path_classification}")
#         model_classification = load_model(model_file_path_classification)

#     else:
#         # Folder and model file path
#         model_folder = 'Generic-MultiModel-LSTM-model'
#         run_folder = get_run_folder(model_folder)
#         os.makedirs(run_folder, exist_ok=True)
#         model_file_path_regression = os.path.join(run_folder, 'lstm_multi_input_model_regression.keras')
#         model_file_path_classification = os.path.join(run_folder, 'lstm_multi_input_model_classification.keras')

#     # Retrieve the uploaded file paths from upload_data.py
#     activity_data_path, temperature_data_path = get_uploaded_data_paths()

#     # Ensure both paths are available before continuing
#     # Ensure both paths are available before continuing
#     if not activity_data_path or not temperature_data_path:
#         print("Error: Missing data paths for activity or temperature data.")
#         display_missing_data_popup()  # Display the popup window
#         return  # Exit the function if paths are not available
    
    
#     # Load the datasets using the uploaded file paths
#     temperature_data = pd.read_csv(temperature_data_path)
#     activity_data = pd.read_csv(activity_data_path)

#     # Load cow alerts data from a hardcoded path or make it dynamic as well
#     cow_alerts_data_path = 'C:/Users/Jyothesh karnam/Desktop/Dairy Herd Monitoring/User Information/Datasets/Cow_Alerts.csv'
#     cow_alerts_data = pd.read_csv(cow_alerts_data_path)

#     # Rename 'Unnamed: 0' to 'Date'
#     temperature_data.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
#     activity_data.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)

#     # Merge the datasets on 'Date'
#     combined_data = pd.merge(temperature_data, activity_data, on='Date', suffixes=('_temp', '_activity'))

#     # Select relevant columns (excluding 'Date')
#     temperature_columns = [col for col in combined_data.columns if '_temp' in col]
#     activity_columns = [col for col in combined_data.columns if '_activity' in col]

#     # Normalize the temperature and activity data
#     scaler = MinMaxScaler()
#     combined_data[temperature_columns] = scaler.fit_transform(combined_data[temperature_columns])
#     combined_data[activity_columns] = scaler.fit_transform(combined_data[activity_columns])

#     # Define the target health score as the mean of all temperature and activity data
#     combined_data['health_score'] = combined_data[temperature_columns + activity_columns].mean(axis=1)

#     # Add a classification column based on health_score
#     combined_data['health_state'] = pd.cut(combined_data['health_score'], bins=[-np.inf, 0.33, 0.66, np.inf], labels=['Red', 'Orange', 'Green'])

#     # Encode health_state labels to integers
#     label_encoder = LabelEncoder()
#     combined_data['health_state_encoded'] = label_encoder.fit_transform(combined_data['health_state'])

#     # Train-Test Split and Sequence Creation for LSTM
#     sequence_length = 5
#     train_data, test_data = train_test_split(combined_data, test_size=0.2, shuffle=False)

#     def create_sequences(data, sequence_length, columns):
#         sequences = []
#         for i in range(len(data) - sequence_length):
#             sequence = data[i:i + sequence_length][columns].values
#             sequences.append(sequence)
#         return np.array(sequences)

#     # Prepare data for regression
#     X_train_temp_reg = create_sequences(train_data, sequence_length, temperature_columns)
#     X_train_activity_reg = create_sequences(train_data, sequence_length, activity_columns)
#     y_train_reg = train_data[sequence_length:]['health_score'].values

#     X_test_temp_reg = create_sequences(test_data, sequence_length, temperature_columns)
#     X_test_activity_reg = create_sequences(test_data, sequence_length, activity_columns)
#     y_test_reg = test_data[sequence_length:]['health_score'].values

#     # Prepare data for classification
#     y_train_class = train_data[sequence_length:]['health_state_encoded'].values
#     y_test_class = test_data[sequence_length:]['health_state_encoded'].values

#     # Reshape for LSTM input (samples, timesteps, features)
#     X_train_temp_reg = X_train_temp_reg.reshape((X_train_temp_reg.shape[0], sequence_length, len(temperature_columns)))
#     X_train_activity_reg = X_train_activity_reg.reshape((X_train_activity_reg.shape[0], sequence_length, len(activity_columns)))
#     X_test_temp_reg = X_test_temp_reg.reshape((X_test_temp_reg.shape[0], sequence_length, len(temperature_columns)))
#     X_test_activity_reg = X_test_activity_reg.reshape((X_test_activity_reg.shape[0], sequence_length, len(activity_columns)))

#     X_train_temp_class = X_train_temp_reg
#     X_train_activity_class = X_train_activity_reg
#     X_test_temp_class = X_test_temp_reg
#     X_test_activity_class = X_test_activity_reg

#     # Regression model
#     if os.path.exists(model_file_path_regression):
#         print("Loading existing regression model...")
#         model_regression = load_model(model_file_path_regression)
#     else:
#         print("No regression model found. Training a new one...")
#         # Input for temperature data
#         temp_input_reg = Input(shape=(sequence_length, len(temperature_columns)), name='temp_input_reg')
#         temp_lstm_reg = LSTM(100, activation='relu', return_sequences=False)(temp_input_reg)

#         # Input for activity data
#         activity_input_reg = Input(shape=(sequence_length, len(activity_columns)), name='activity_input_reg')
#         activity_lstm_reg = LSTM(100, activation='relu', return_sequences=False)(activity_input_reg)

#         # Combine the outputs of the two LSTM layers
#         combined_reg = concatenate([temp_lstm_reg, activity_lstm_reg])

#         # Dense layers after combining the inputs
#         dense_output_reg = Dense(50, activation='relu')(combined_reg)
#         dense_output_reg = Dropout(0.2)(dense_output_reg)
#         final_output_reg = Dense(1, name='final_output_reg')(dense_output_reg)

#         # Create the model
#         model_regression = Model(inputs=[temp_input_reg, activity_input_reg], outputs=final_output_reg)

#     model_regression.compile(optimizer=Adam(learning_rate=0.0001), loss='mean_squared_error')

#     # Classification model
#     if os.path.exists(model_file_path_classification):
#         print("Loading existing classification model...")
#         model_classification = load_model(model_file_path_classification)
#     else:
#         print("No classification model found. Training a new one...")
#         # Input for temperature data
#         temp_input_class = Input(shape=(sequence_length, len(temperature_columns)), name='temp_input_class')
#         temp_lstm_class = LSTM(100, activation='relu', return_sequences=False)(temp_input_class)

#         # Input for activity data
#         activity_input_class = Input(shape=(sequence_length, len(activity_columns)), name='activity_input_class')
#         activity_lstm_class = LSTM(100, activation='relu', return_sequences=False)(activity_input_class)

#         # Combine the outputs of the two LSTM layers
#         combined_class = concatenate([temp_lstm_class, activity_lstm_class])

#         # Dense layers after combining the inputs
#         dense_output_class = Dense(50, activation='relu')(combined_class)
#         dense_output_class = Dropout(0.2)(dense_output_class)
#         final_output_class = Dense(3, activation='softmax', name='final_output_class')(dense_output_class)

#         # Create the classification model
#         model_classification = Model(inputs=[temp_input_class, activity_input_class], outputs=final_output_class)

#     model_classification.compile(optimizer=Adam(learning_rate=0.0001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

#     # Train Regression Model if needed
#     if not reload_model_path:
#         print("Retraining the regression model...")
#         model_regression.fit([X_train_temp_reg, X_train_activity_reg], y_train_reg, epochs=100, batch_size=16, validation_data=([X_test_temp_reg, X_test_activity_reg], y_test_reg), verbose=1)
#         model_regression.save(model_file_path_regression)
#         print(f"Regression model saved to {model_file_path_regression}")

#     # Train Classification Model if needed
#     if not reload_model_path:
#         print("Retraining the classification model...")
#         model_classification.fit([X_train_temp_class, X_train_activity_class], y_train_class, epochs=100, batch_size=16, validation_data=([X_test_temp_class, X_test_activity_class], y_test_class), verbose=1)
#         model_classification.save(model_file_path_classification)
#         print(f"Classification model saved to {model_file_path_classification}")

#     # Make predictions for regression
#     train_predictions_reg = model_regression.predict([X_train_temp_reg, X_train_activity_reg])
#     test_predictions_reg = model_regression.predict([X_test_temp_reg, X_test_activity_reg])

#     # Make predictions for classification
#     train_predictions_class = model_classification.predict([X_train_temp_class, X_train_activity_class])
#     test_predictions_class = model_classification.predict([X_test_temp_class, X_test_activity_class])

#     # Combine predictions for regression
#     full_predictions_reg = np.concatenate([train_predictions_reg.flatten(), test_predictions_reg.flatten()])

#     # Combine predictions for classification
#     full_predictions_class = np.concatenate([np.argmax(train_predictions_class, axis=1), np.argmax(test_predictions_class, axis=1)])

#     # RMSE calculations for both regression and classification
#     train_rmse_reg = calculate_rmse_percentage(y_train_reg, train_predictions_reg)
#     test_rmse_reg = calculate_rmse_percentage(y_test_reg, test_predictions_reg)

#     train_rmse_class = calculate_rmse_percentage(y_train_class, np.argmax(train_predictions_class, axis=1))
#     test_rmse_class = calculate_rmse_percentage(y_test_class, np.argmax(test_predictions_class, axis=1))

#     # Create a combined dataset for plotting
#     combined_data['health_score'] *= 100
#     full_predictions_reg *= 100

#     # Convert classification predictions back to labels
#     predicted_labels = label_encoder.inverse_transform(full_predictions_class.astype(int))

#     # Plot the Regression and Classification Results


    
#     # Plot the Regression and Classification Results
#     plt.style.use('default')
    
#     fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))  # Create two subplots for regression and classification
    
#     # Set the background color of the figure to white
#     fig.patch.set_facecolor('white')
    
#     # Set the background color of the axes to white
#     ax1.set_facecolor('white')
#     ax2.set_facecolor('white')
    
#     x_indices = np.arange(len(combined_data))
#     prediction_indices = np.arange(sequence_length, sequence_length + len(full_predictions_reg))

#     # Plot the actual health score with thin line and small markers
#     actual_health_score_line, = ax1.plot(x_indices, combined_data['health_score'], marker='o', markersize=3, color='cyan', linestyle='-', linewidth=0.8, label='Actual Health Score')
    
#     # Plot the prediction line in bright purple
#     predicted_health_score_line, = ax1.plot(prediction_indices, full_predictions_reg, marker='o', markersize=3, color='#C71585', linestyle='-', linewidth=0.8, label='Predicted Health Score')
    
#     # Add labels and title with RMSE details for Regression Plot
#     ax1.set_title(f'Regression Model | Health Score Predictions | Train RMSE: {train_rmse_reg:.2f}% | Test RMSE: {test_rmse_reg:.2f}%', color='black')
#     ax1.set_xlabel('Day', color='black')
#     ax1.set_ylabel('Health Score (0-100)', color='black')
#     ax1.legend(loc='best')
    
#         # Initialize the annotation for hover
#     annot = ax1.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
#                          bbox=dict(boxstyle="round", fc="white", ec="black"),
#                          arrowprops=dict(arrowstyle="->", color='black'),
#                          color='black')
    
#     annot.set_visible(False)
    
#     # Function to update the annotation position and content
#     def update_annot(ind, line, x_data, y_data):
#         x, y = x_data[ind["ind"][0]], y_data[ind["ind"][0]]
#         annot.xy = (x, y)
#         annot.set_text(f"Date: {combined_data['Date'].iloc[ind['ind'][0]]}\nValue: {y:.2f}")
#         annot.get_bbox_patch().set_facecolor('white')
#         annot.get_bbox_patch().set_alpha(0.7)
    
#     # Hover event handler
#     def hover(event):
#         visible = annot.get_visible()
#         if event.inaxes == ax1:
#             # Check if the mouse is near the actual health score line
#             cont, ind = actual_health_score_line.contains(event)
#             if cont:
#                 update_annot(ind, actual_health_score_line, x_indices, combined_data['health_score'])
#                 annot.set_visible(True)
#                 fig.canvas.draw_idle()
#             else:
#                 # Check if the mouse is near the predicted health score line
#                 cont, ind = predicted_health_score_line.contains(event)
#                 if cont:
#                     update_annot(ind, predicted_health_score_line, prediction_indices, full_predictions_reg)
#                     annot.set_visible(True)
#                     fig.canvas.draw_idle()
#                 elif visible:
#                     annot.set_visible(False)
#                     fig.canvas.draw_idle()
    
#     # Connect the hover event to the plot
#     fig.canvas.mpl_connect("motion_notify_event", hover)
    
#     # Ensure x_class_indices matches the length of predicted_labels
#     x_class_indices = np.arange(len(predicted_labels))
    
#     # Add labels and title for Classification Plot
#     # Add labels and title for Classification Plot
#     ax2.set_title(f'Classification Model | Health State Predictions', color='black')
#     ax2.set_xlabel('Day', color='black')
#     ax2.set_ylabel('Health State (Red=2, Orange=1, Green=0)', color='black')
#     ax2.set_ylim(-1, 2.5)  # Set the limits for the y-axis
    
#     # Use actual dates for the x-axis
#     # Use actual dates for the x-axis
# # Create sequential numbers for the x-axis
#     x_class_indices = np.arange(1, len(combined_data) + 1)
    
#     # Pad predicted_labels with NaN for first 5 and last 5 days if necessary
#     padding_size = sequence_length
#     padded_predicted_labels = np.concatenate([[np.nan] * padding_size, predicted_labels, [np.nan] * padding_size])
    
#     # Ensure x_class_indices match the padded predicted_labels
#     if len(x_class_indices) > len(padded_predicted_labels):
#         x_class_indices = x_class_indices[:len(padded_predicted_labels)]
#     elif len(x_class_indices) < len(padded_predicted_labels):
#         padded_predicted_labels = padded_predicted_labels[:len(x_class_indices)]
    
#     # Set the x-ticks to be sequential numbers corresponding to each day
#     ax2.set_xticks(np.arange(1, len(x_class_indices) + 1))
#     ax2.set_xticklabels(np.arange(1, len(x_class_indices) + 1), rotation=45, ha='right')
    
#     # Plot the classification points including the padded values
#     for i in range(len(padded_predicted_labels)):
#         if padded_predicted_labels[i] == 'Red':
#             ax2.plot(x_class_indices[i], 2, marker='o', markersize=5, color='red')
#         elif padded_predicted_labels[i] == 'Orange':
#             ax2.plot(x_class_indices[i], 1, marker='o', markersize=5, color='orange')
#         elif padded_predicted_labels[i] == 'Green':
#             ax2.plot(x_class_indices[i], 0, marker='o', markersize=5, color='green')
#         else:
#             # Don't plot anything for NaN padded days
#             continue
    

#     green_scatter = ax2.scatter([], [], color='green', label='Green')
#     orange_scatter = ax2.scatter([], [], color='orange', label='Orange')
#     red_scatter = ax2.scatter([], [], color='red', label='Red')

#     # Plot the group mean values in a very thin cyan line
#     group_mean_values = cow_alerts_data['Group Mean'].values  # Assuming 'Group Mean' is in cow_alerts_data
#     group_mean_line, = ax2.plot(x_class_indices[:len(group_mean_values)], group_mean_values[:len(x_class_indices)],
#                                 linestyle='-', linewidth=0.5, color='cyan', marker='o', markersize=4, label='Group Mean')

#     # Adjust legend to include the group mean and correct colors
#     ax2.legend(handles=[green_scatter, orange_scatter, red_scatter, group_mean_line], loc='best')
#     # Show regression and classification plots first
#     canvas = FigureCanvasTkAgg(fig, master=frame)
#     canvas.draw()
#     canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

#     # After the graphs are loaded, show the confusion matrix in a new window
#     after_graph_is_loaded()

#     # Generate confusion matrix and report
#     labels = [0, 1, 2]  # Green=0, Orange=1, Red=2
#     target_names = ["Green Alert", "Orange Alert", "Red Alert"]
#     cm, report = generate_confusion_matrix_and_report(y_test_class, np.argmax(test_predictions_class, axis=1), labels, target_names)

#     # Display the confusion matrix and classification report after the graphs
#     print(f"Confusion Matrix:\n{cm}")
#     print(f"Classification Report:\n{report}")

#     # Prompt the user to save the model after the confusion matrix is closed
#     def after_confusion_matrix_closed():
#         if save_callback and not reload_model_path:
#             print(f"Prompting user to save the model to {run_folder}")
#             save_callback(run_folder, model_regression)  # Save the regression model
#             save_callback(run_folder, model_classification)  # Save the classification model

#     after_confusion_matrix_closed()





# ////////////////////////////////////////////////////////////////////////

# Generic_Multi_Model.py
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from tensorflow.keras.models import Model, load_model, Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, concatenate
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, mean_absolute_percentage_error, mean_squared_error, accuracy_score, classification_report
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox
from sklearn.metrics import confusion_matrix, classification_report
from tkinter.scrolledtext import ScrolledText
from upload_data import get_uploaded_data_paths  # Import the function to get file paths


import matplotlib.pyplot as plt

plt.style.use('default')


def display_missing_data_popup():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showerror("Data Error", "No data uploaded! Please upload the necessary files to proceed.")
    root.destroy()

def get_run_folder(base_folder):
    """Find the next run folder, e.g. MultiModel run 1, MultiModel run 2, etc."""
    run_number = 1
    while os.path.exists(os.path.join(base_folder, f'MultiModel run {run_number}')):
        run_number += 1
    return os.path.join(base_folder, f'MultiModel run {run_number}')

def show_report_in_window(report_text, final_alert):
    # Create a new tkinter window
    report_window = tk.Toplevel()
    report_window.title("Confusion Matrix, Classification Report, and Final Alert")

    # Add a Text widget to display the report
    text_area = ScrolledText(report_window, wrap=tk.WORD, width=80, height=20, font=("Helvetica", 12))
    text_area.pack(expand=True, fill=tk.BOTH)
    
    # Insert the report text into the Text widget
    text_area.insert(tk.END, report_text)
    
    # Insert the Final Alert text at the end
    text_area.insert(tk.END, f"\n\nFinal Alert for the Entire Herd: {final_alert}")
    
    # Disable editing
    text_area.config(state=tk.DISABLED)
    
    # Start the tkinter main loop for the report window
    report_window.mainloop()

def generate_confusion_matrix_and_report(y_true, y_pred, labels, target_names):
    # Ensure y_true and y_pred have all the necessary classes
    unique_classes_in_y_true = np.unique(y_true)
    unique_classes_in_y_pred = np.unique(y_pred)
    
    # Check if we are missing any classes
    all_classes = np.union1d(unique_classes_in_y_true, unique_classes_in_y_pred)
    
    # If we are missing any of the specified labels (0, 1, 2 for Green, Orange, Red), ensure they are included
    if len(all_classes) < len(labels):
        y_true = np.concatenate([y_true, labels])
        y_pred = np.concatenate([y_pred, labels])

    # Generate confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    # Generate classification report
    report = classification_report(y_true, y_pred, target_names=target_names, labels=labels, zero_division=0)
    
    # Determine the final herd alert based on the predictions
    alert_counts = np.bincount(y_pred, minlength=len(labels))
    final_alert_idx = np.argmax(alert_counts)
    final_alert = target_names[final_alert_idx]

    # Prepare the report text
    report_text = f"Confusion Matrix:\n{cm}\n\nClassification Report:\n{report}"
    
    # Display the report and the final alert in a GUI window
    show_report_in_window(report_text, final_alert)
    
    return cm, report

def calculate_rmse_percentage(y_true, y_pred):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    max_value = np.max(y_true)
    return (1 - (rmse / max_value)) * 100 if max_value > 0 else 100

def generate_multi_model_graph(frame, after_graph_is_loaded, save_callback=None, reload_model_path=None):
    # Destroy all widgets in the frame to clear previous graphs
    for widget in frame.winfo_children():
        widget.destroy()

    # Folder and model file path
    model_folder = 'Generic-MultiModel-LSTM-model'

    if reload_model_path:
        # Use the reload_model_path to load pre-trained models
        model_file_path_regression = os.path.join(reload_model_path, 'lstm_multi_input_model_regression.keras')
        model_file_path_classification = os.path.join(reload_model_path, 'lstm_multi_input_model_classification.keras')

        print(f"Loading regression model from {model_file_path_regression}")
        model_regression = load_model(model_file_path_regression)

        print(f"Loading classification model from {model_file_path_classification}")
        model_classification = load_model(model_file_path_classification)

    else:
        # Folder and model file path
        model_folder = 'Generic-MultiModel-LSTM-model'
        run_folder = get_run_folder(model_folder)
        os.makedirs(run_folder, exist_ok=True)
        model_file_path_regression = os.path.join(run_folder, 'lstm_multi_input_model_regression.keras')
        model_file_path_classification = os.path.join(run_folder, 'lstm_multi_input_model_classification.keras')

    # Retrieve the uploaded file paths from upload_data.py
    activity_data_path, temperature_data_path = get_uploaded_data_paths()

    # Ensure both paths are available before continuing
    # Ensure both paths are available before continuing
    if not activity_data_path or not temperature_data_path:
        print("Error: Missing data paths for activity or temperature data.")
        display_missing_data_popup()  # Display the popup window
        return  # Exit the function if paths are not available
    
    
    # Load the datasets using the uploaded file paths
    temperature_data = pd.read_csv(temperature_data_path)
    activity_data = pd.read_csv(activity_data_path)

    # Load cow alerts data from a hardcoded path or make it dynamic as well
    cow_alerts_data_path = 'C:/Users/Jyothesh karnam/Desktop/Dairy Herd Monitoring/User Information/Datasets/Cow_Alerts.csv'
    cow_alerts_data = pd.read_csv(cow_alerts_data_path)

    # Rename 'Unnamed: 0' to 'Date'
    temperature_data.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
    activity_data.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)

    # Merge the datasets on 'Date'
    combined_data = pd.merge(temperature_data, activity_data, on='Date', suffixes=('_temp', '_activity'))

    # Select relevant columns (excluding 'Date')
    temperature_columns = [col for col in combined_data.columns if '_temp' in col]
    activity_columns = [col for col in combined_data.columns if '_activity' in col]

    # Normalize the temperature and activity data
    scaler = MinMaxScaler()
    combined_data[temperature_columns] = scaler.fit_transform(combined_data[temperature_columns])
    combined_data[activity_columns] = scaler.fit_transform(combined_data[activity_columns])

    # Define the target health score as the mean of all temperature and activity data
    combined_data['health_score'] = combined_data[temperature_columns + activity_columns].mean(axis=1)

    # Add a classification column based on health_score
    combined_data['health_state'] = pd.cut(combined_data['health_score'], bins=[-np.inf, 0.33, 0.66, np.inf], labels=['Red', 'Orange', 'Green'])

    # Encode health_state labels to integers
    label_encoder = LabelEncoder()
    combined_data['health_state_encoded'] = label_encoder.fit_transform(combined_data['health_state'])

    # Train-Test Split and Sequence Creation for LSTM
    sequence_length = 5
    train_data, test_data = train_test_split(combined_data, test_size=0.2, shuffle=False)

    def create_sequences(data, sequence_length, columns):
        sequences = []
        for i in range(len(data) - sequence_length):
            sequence = data[i:i + sequence_length][columns].values
            sequences.append(sequence)
        return np.array(sequences)

    # Prepare data for regression
    X_train_temp_reg = create_sequences(train_data, sequence_length, temperature_columns)
    X_train_activity_reg = create_sequences(train_data, sequence_length, activity_columns)
    y_train_reg = train_data[sequence_length:]['health_score'].values

    X_test_temp_reg = create_sequences(test_data, sequence_length, temperature_columns)
    X_test_activity_reg = create_sequences(test_data, sequence_length, activity_columns)
    y_test_reg = test_data[sequence_length:]['health_score'].values

    # Prepare data for classification
    y_train_class = train_data[sequence_length:]['health_state_encoded'].values
    y_test_class = test_data[sequence_length:]['health_state_encoded'].values

    # Reshape for LSTM input (samples, timesteps, features)
    X_train_temp_reg = X_train_temp_reg.reshape((X_train_temp_reg.shape[0], sequence_length, len(temperature_columns)))
    X_train_activity_reg = X_train_activity_reg.reshape((X_train_activity_reg.shape[0], sequence_length, len(activity_columns)))
    X_test_temp_reg = X_test_temp_reg.reshape((X_test_temp_reg.shape[0], sequence_length, len(temperature_columns)))
    X_test_activity_reg = X_test_activity_reg.reshape((X_test_activity_reg.shape[0], sequence_length, len(activity_columns)))

    X_train_temp_class = X_train_temp_reg
    X_train_activity_class = X_train_activity_reg
    X_test_temp_class = X_test_temp_reg
    X_test_activity_class = X_test_activity_reg

    # Regression model
    if os.path.exists(model_file_path_regression):
        print("Loading existing regression model...")
        model_regression = load_model(model_file_path_regression)
    else:
        print("No regression model found. Training a new one...")
        # Input for temperature data
        temp_input_reg = Input(shape=(sequence_length, len(temperature_columns)), name='temp_input_reg')
        temp_lstm_reg = LSTM(100, activation='relu', return_sequences=False)(temp_input_reg)

        # Input for activity data
        activity_input_reg = Input(shape=(sequence_length, len(activity_columns)), name='activity_input_reg')
        activity_lstm_reg = LSTM(100, activation='relu', return_sequences=False)(activity_input_reg)

        # Combine the outputs of the two LSTM layers
        combined_reg = concatenate([temp_lstm_reg, activity_lstm_reg])

        # Dense layers after combining the inputs
        dense_output_reg = Dense(50, activation='relu')(combined_reg)
        dense_output_reg = Dropout(0.2)(dense_output_reg)
        final_output_reg = Dense(1, name='final_output_reg')(dense_output_reg)

        # Create the model
        model_regression = Model(inputs=[temp_input_reg, activity_input_reg], outputs=final_output_reg)

    model_regression.compile(optimizer=Adam(learning_rate=0.0001), loss='mean_squared_error')

    # Classification model
    if os.path.exists(model_file_path_classification):
        print("Loading existing classification model...")
        model_classification = load_model(model_file_path_classification)
    else:
        print("No classification model found. Training a new one...")
        # Input for temperature data
        temp_input_class = Input(shape=(sequence_length, len(temperature_columns)), name='temp_input_class')
        temp_lstm_class = LSTM(100, activation='relu', return_sequences=False)(temp_input_class)

        # Input for activity data
        activity_input_class = Input(shape=(sequence_length, len(activity_columns)), name='activity_input_class')
        activity_lstm_class = LSTM(100, activation='relu', return_sequences=False)(activity_input_class)

        # Combine the outputs of the two LSTM layers
        combined_class = concatenate([temp_lstm_class, activity_lstm_class])

        # Dense layers after combining the inputs
        dense_output_class = Dense(50, activation='relu')(combined_class)
        dense_output_class = Dropout(0.2)(dense_output_class)
        final_output_class = Dense(3, activation='softmax', name='final_output_class')(dense_output_class)

        # Create the classification model
        model_classification = Model(inputs=[temp_input_class, activity_input_class], outputs=final_output_class)

    model_classification.compile(optimizer=Adam(learning_rate=0.0001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Train Regression Model if needed
    if not reload_model_path:
        print("Retraining the regression model...")
        model_regression.fit([X_train_temp_reg, X_train_activity_reg], y_train_reg, epochs=100, batch_size=16, validation_data=([X_test_temp_reg, X_test_activity_reg], y_test_reg), verbose=1)
        model_regression.save(model_file_path_regression)
        print(f"Regression model saved to {model_file_path_regression}")

    # Train Classification Model if needed
    if not reload_model_path:
        print("Retraining the classification model...")
        model_classification.fit([X_train_temp_class, X_train_activity_class], y_train_class, epochs=100, batch_size=16, validation_data=([X_test_temp_class, X_test_activity_class], y_test_class), verbose=1)
        model_classification.save(model_file_path_classification)
        print(f"Classification model saved to {model_file_path_classification}")

    # Make predictions for regression
    train_predictions_reg = model_regression.predict([X_train_temp_reg, X_train_activity_reg])
    test_predictions_reg = model_regression.predict([X_test_temp_reg, X_test_activity_reg])

    # Make predictions for classification
    train_predictions_class = model_classification.predict([X_train_temp_class, X_train_activity_class])
    test_predictions_class = model_classification.predict([X_test_temp_class, X_test_activity_class])

    # Combine predictions for regression
    full_predictions_reg = np.concatenate([train_predictions_reg.flatten(), test_predictions_reg.flatten()])

    # Combine predictions for classification
    full_predictions_class = np.concatenate([np.argmax(train_predictions_class, axis=1), np.argmax(test_predictions_class, axis=1)])

    # RMSE calculations for both regression and classification
    train_rmse_reg = calculate_rmse_percentage(y_train_reg, train_predictions_reg)
    test_rmse_reg = calculate_rmse_percentage(y_test_reg, test_predictions_reg)

    train_rmse_class = calculate_rmse_percentage(y_train_class, np.argmax(train_predictions_class, axis=1))
    test_rmse_class = calculate_rmse_percentage(y_test_class, np.argmax(test_predictions_class, axis=1))

    # Create a combined dataset for plotting
    combined_data['health_score'] *= 100
    full_predictions_reg *= 100

    # Convert classification predictions back to labels
    predicted_labels = label_encoder.inverse_transform(full_predictions_class.astype(int))

    # Plot the Regression and Classification Results


    
    # Plot the Regression and Classification Results
    plt.style.use('default')
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))  # Create two subplots for regression and classification
    
    # Set the background color of the figure to white
    fig.patch.set_facecolor('white')
    
    # Set the background color of the axes to white
    ax1.set_facecolor('white')
    ax2.set_facecolor('white')
    
    x_indices = np.arange(len(combined_data))
    prediction_indices = np.arange(sequence_length, sequence_length + len(full_predictions_reg))

    # Plot the actual health score with thin line and small markers
    actual_health_score_line, = ax1.plot(x_indices, combined_data['health_score'], marker='o', markersize=3, color='cyan', linestyle='-', linewidth=0.8, label='Actual Health Score')
    
    # Plot the prediction line in bright purple
    predicted_health_score_line, = ax1.plot(prediction_indices, full_predictions_reg, marker='o', markersize=3, color='#C71585', linestyle='-', linewidth=0.8, label='Predicted Health Score')
    
    # Add labels and title with RMSE details for Regression Plot
    ax1.set_title(f'Regression Model | Health Score Predictions | Train RMSE: {train_rmse_reg:.2f}% | Test RMSE: {test_rmse_reg:.2f}%', color='white')
    ax1.set_xlabel('Day', color='white')
    ax1.set_ylabel('Health Score (0-100)', color='white')
    ax1.legend(loc='best')
    
        # Initialize the annotation for hover
    annot = ax1.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                         bbox=dict(boxstyle="round", fc="white", ec="black"),
                         arrowprops=dict(arrowstyle="->", color='black'),
                         color='black')
    
    annot.set_visible(False)
    
    # Function to update the annotation position and content
    def update_annot(ind, line, x_data, y_data):
        x, y = x_data[ind["ind"][0]], y_data[ind["ind"][0]]
        annot.xy = (x, y)
        annot.set_text(f"Date: {combined_data['Date'].iloc[ind['ind'][0]]}\nValue: {y:.2f}")
        annot.get_bbox_patch().set_facecolor('white')
        annot.get_bbox_patch().set_alpha(0.7)
    
    # Hover event handler
    def hover(event):
        visible = annot.get_visible()
        if event.inaxes == ax1:
            # Check if the mouse is near the actual health score line
            cont, ind = actual_health_score_line.contains(event)
            if cont:
                update_annot(ind, actual_health_score_line, x_indices, combined_data['health_score'])
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                # Check if the mouse is near the predicted health score line
                cont, ind = predicted_health_score_line.contains(event)
                if cont:
                    update_annot(ind, predicted_health_score_line, prediction_indices, full_predictions_reg)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                elif visible:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()
    
    # Connect the hover event to the plot
    fig.canvas.mpl_connect("motion_notify_event", hover)
    
    # Ensure x_class_indices matches the length of predicted_labels
    x_class_indices = np.arange(len(predicted_labels))
    
    # Add labels and title for Classification Plot
    # Add labels and title for Classification Plot
    ax2.set_title(f'Classification Model | Health State Predictions', color='white')
    ax2.set_xlabel('Day', color='white')
    ax2.set_ylabel('Health State (Red=2, Orange=1, Green=0)', color='white')
    ax2.set_ylim(-1, 2.5)  # Set the limits for the y-axis
    
    # Use actual dates for the x-axis
    # Use actual dates for the x-axis
# Create sequential numbers for the x-axis
    x_class_indices = np.arange(1, len(combined_data) + 1)
    
    # Pad predicted_labels with NaN for first 5 and last 5 days if necessary
    padding_size = sequence_length
    padded_predicted_labels = np.concatenate([[np.nan] * padding_size, predicted_labels, [np.nan] * padding_size])
    
    # Ensure x_class_indices match the padded predicted_labels
    if len(x_class_indices) > len(padded_predicted_labels):
        x_class_indices = x_class_indices[:len(padded_predicted_labels)]
    elif len(x_class_indices) < len(padded_predicted_labels):
        padded_predicted_labels = padded_predicted_labels[:len(x_class_indices)]
    
    # Set the x-ticks to be sequential numbers corresponding to each day
    ax2.set_xticks(np.arange(1, len(x_class_indices) + 1))
    ax2.set_xticklabels(np.arange(1, len(x_class_indices) + 1), rotation=45, ha='right')
    
    # Plot the classification points including the padded values
    for i in range(len(padded_predicted_labels)):
        if padded_predicted_labels[i] == 'Red':
            ax2.plot(x_class_indices[i], 2, marker='o', markersize=5, color='red')
        elif padded_predicted_labels[i] == 'Orange':
            ax2.plot(x_class_indices[i], 1, marker='o', markersize=5, color='orange')
        elif padded_predicted_labels[i] == 'Green':
            ax2.plot(x_class_indices[i], 0, marker='o', markersize=5, color='green')
        else:
            # Don't plot anything for NaN padded days
            continue
    

    green_scatter = ax2.scatter([], [], color='green', label='Green')
    orange_scatter = ax2.scatter([], [], color='orange', label='Orange')
    red_scatter = ax2.scatter([], [], color='red', label='Red')

    # Plot the group mean values in a very thin cyan line
    group_mean_values = cow_alerts_data['Group Mean'].values  # Assuming 'Group Mean' is in cow_alerts_data
    group_mean_line, = ax2.plot(x_class_indices[:len(group_mean_values)], group_mean_values[:len(x_class_indices)],
                                linestyle='-', linewidth=0.5, color='cyan', marker='o', markersize=4, label='Group Mean')

    # Adjust legend to include the group mean and correct colors
    ax2.legend(handles=[green_scatter, orange_scatter, red_scatter, group_mean_line], loc='best')
    # Show regression and classification plots first
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # After the graphs are loaded, show the confusion matrix in a new window
    after_graph_is_loaded()

    # Generate confusion matrix and report
    labels = [0, 1, 2]  # Green=0, Orange=1, Red=2
    target_names = ["Green Alert", "Orange Alert", "Red Alert"]
    cm, report = generate_confusion_matrix_and_report(y_test_class, np.argmax(test_predictions_class, axis=1), labels, target_names)

    # Display the confusion matrix and classification report after the graphs
    print(f"Confusion Matrix:\n{cm}")
    print(f"Classification Report:\n{report}")

    # Prompt the user to save the model after the confusion matrix is closed
    def after_confusion_matrix_closed():
        if save_callback and not reload_model_path:
            print(f"Prompting user to save the model to {run_folder}")
            save_callback(run_folder, model_regression)  # Save the regression model
            save_callback(run_folder, model_classification)  # Save the classification model

    after_confusion_matrix_closed()




