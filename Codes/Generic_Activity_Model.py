# # # Generic_Activity_model.py
# import numpy as np
# import os
# import pandas as pd
# import tkinter as tk
# import matplotlib.pyplot as plt
# from sklearn.preprocessing import MinMaxScaler
# from tensorflow.keras.models import Sequential, load_model
# from tensorflow.keras.layers import LSTM, Dense, Dropout
# from sklearn.model_selection import train_test_split
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from tensorflow.keras.utils import to_categorical
# from sklearn.metrics import mean_squared_error, accuracy_score, confusion_matrix, classification_report
# from tkinter import messagebox
# from upload_data import get_uploaded_data_paths
# import mplcursors
# import sys
# from fpdf import FPDF

# plt.style.use('default')

# def display_missing_data_popup():
#     root = tk.Tk()
#     root.withdraw()  # Hide the root window
#     messagebox.showerror("Data Error", "No data uploaded! Please upload the necessary files to proceed.")
#     root.destroy()

# def generate_activity_model_graph(frame, after_graph_is_loaded, save_callback=None, reload_model_path=None):
#     # Destroy all widgets in the frame to clear previous graphs
#     for widget in frame.winfo_children():
#         widget.destroy()

#     # Define constants
#     base_model_folder = "Generic-Activity-inputs LSTM-model"
#     report_folder = "Entire Herd Activity Report"

#     # Function to create a new folder for the current run
#     def create_new_folder(base_folder, prefix):
#         existing_folders = [folder for folder in os.listdir(base_folder) 
#                             if os.path.isdir(os.path.join(base_folder, folder)) and folder.startswith(prefix)]
        
#         if existing_folders:
#             existing_numbers = []
#             for folder in existing_folders:
#                 try:
#                     # Extract the number at the end of the folder name and convert to int
#                     existing_numbers.append(int(folder.split(" ")[-1]))
#                 except ValueError:
#                     # If the folder name doesn't end with a number, skip it
#                     continue
#             next_number = max(existing_numbers) + 1 if existing_numbers else 1
#         else:
#             next_number = 1
    
#         new_folder_name = f"{prefix} {next_number}"
#         new_folder_path = os.path.join(base_folder, new_folder_name)
#         os.makedirs(new_folder_path, exist_ok=True)
#         return new_folder_path

#     # If reloading the model
#     if reload_model_path:
#         model_path = os.path.join(reload_model_path, "lstm_model.h5")
#         classification_model_path = os.path.join(reload_model_path, "classification_model.h5")
#     else:
#         # Train a new model and create a new folder for the current run
#         current_run_folder = create_new_folder(base_model_folder, "Entire Herd")
#         model_path = os.path.join(current_run_folder, "lstm_model.h5")
#         classification_model_path = os.path.join(current_run_folder, "classification_model.h5")

#     # Load the activity dataset (replace hardcoded path)
#     activity_file_path, _ = get_uploaded_data_paths()
    
#     if not activity_file_path:
#         messagebox.showerror("Error", "Please upload the activity CSV file.")
#         return
    
#     data = pd.read_csv(activity_file_path)
#         # Load the Cow_Alerts.csv file

#     if getattr(sys, 'frozen', False):
#         # If running as a compiled executable
#         base_dir = os.path.dirname(sys.executable)
#     else:
#         base_dir = os.path.dirname(os.path.abspath(__file__))

#     print(f"Base directory: {base_dir}")  # This will print the correct base directory for verification

#     # Use the base directory to find the Cow_Alerts.csv file
#     cow_alerts_path = 'C:/Users/Jyothesh karnam/Desktop/Dairy Herd Monitoring/User Information/Datasets/Cow_Alerts.csv'

#     # Check if the file exists
#     if not os.path.exists(cow_alerts_path):
#         messagebox.showerror("Error", f"Cow Alerts file not found at {cow_alerts_path}. Please ensure the file exists.")
#         return
    
#     cow_alerts = pd.read_csv(cow_alerts_path)
#     cow_alerts['Date'] = pd.to_datetime(cow_alerts['Date'])
#     cow_alerts = pd.read_csv(cow_alerts_path)
#     cow_alerts['Date'] = pd.to_datetime(cow_alerts['Date'])

#     # Extract the 'Group mean' column for comparison
#     group_mean = data['Group mean'].values

#     # Extract the dates for future usage
#     dates = pd.to_datetime(data['Unnamed: 0']).values

#     # Drop the 'Group mean' and 'Unnamed: 0' (date) columns
#     data_without_group_mean = data.drop(columns=['Group mean', 'Unnamed: 0'])

#     # Normalize the data
#     scaler = MinMaxScaler()
#     data_scaled = scaler.fit_transform(data_without_group_mean)

#     # Split the data into training and testing sets (80/20 split)
#     train_data, test_data = train_test_split(data_scaled, test_size=0.2, shuffle=False)

#     # Define the sequence length
#     sequence_length = 5

#     # Function to create sequences for LSTM input
#     def create_sequences(data, sequence_length):
#         sequences = []
#         for i in range(len(data) - sequence_length):
#             sequence = data[i:i + sequence_length]
#             sequences.append(sequence)
#         return np.array(sequences)

#     # Create sequences for training and testing data
#     X_train = create_sequences(train_data, sequence_length)
#     X_test = create_sequences(test_data, sequence_length)

#     # Use the next time step as the target for prediction
#     y_train = train_data[sequence_length:]
#     y_test = test_data[sequence_length:]

#     # Reshape X_train and X_test for LSTM input
#     X_train = X_train.reshape((X_train.shape[0], sequence_length, X_train.shape[2]))
#     X_test = X_test.reshape((X_test.shape[0], sequence_length, X_test.shape[2]))

#     # If we are reloading the model
#     if reload_model_path and os.path.exists(model_path):
#         print("Loading saved regression model...")
#         model = load_model(model_path)
#         # Recompile the model to reset the optimizer
#         model.compile(optimizer='adam', loss='mean_squared_error')
#     else:
#         print("Training a new model...")
#         # Build and train a new LSTM model for regression
#         model = Sequential([
#             LSTM(100, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=False),
#             Dropout(0.2),
#             Dense(28)  # Predicting the next activity for each of the 28 cows
#         ])
#         # Compile the model
#         model.compile(optimizer='adam', loss='mean_squared_error')

#         # Train the model
#         model.fit(X_train, y_train, epochs=100, batch_size=16, validation_data=(X_test, y_test), verbose=1)

#         # Save the regression model
#         model.save(model_path)

#     # Continue with the rest of the code (predictions, plotting, PDF generation, etc.)

#     # Call after_graph_is_loaded callback when done
#     after_graph_is_loaded()

#     # If save_callback exists and we're not reloading, prompt for saving the model
#     if not reload_model_path and save_callback:
#         save_callback(current_run_folder, model)



#     # Make predictions for training and testing sets
#     train_predictions_scaled = model.predict(X_train)
#     test_predictions_scaled = model.predict(X_test)

#     # Inverse transform the predictions to get them back to the original scale
#     train_predictions = scaler.inverse_transform(train_predictions_scaled)
#     test_predictions = scaler.inverse_transform(test_predictions_scaled)
#     y_train_actual = scaler.inverse_transform(y_train)
#     y_test_actual = scaler.inverse_transform(y_test)

#     # ======= RMSE Calculation =======
#     rmse_train = np.sqrt(mean_squared_error(y_train_actual, train_predictions))
#     rmse_test = np.sqrt(mean_squared_error(y_test_actual, test_predictions))

#     train_rmse_percentage = (1 - (rmse_train / np.max(y_train_actual))) * 100
#     test_rmse_percentage = (1 - (rmse_test / np.max(y_test_actual))) * 100

#     # Generate predictions for the entire dataset (train + test combined)
#     full_data = np.vstack([train_data, test_data])
#     X_full = create_sequences(full_data, sequence_length)
#     predictions_full = model.predict(X_full)

#     # Inverse transform the predictions to the original scale
#     predictions_full_inverse = scaler.inverse_transform(predictions_full)

#     # Averaging the predictions across all cows to get a single prediction line representing the entire herd
#     herd_full_prediction = predictions_full_inverse.mean(axis=1)

#     # Inverse transform to get actual values for the full dataset (train + test combined)
#     actual_train_values = scaler.inverse_transform(train_data[sequence_length:]).mean(axis=1)
#     actual_test_values = scaler.inverse_transform(test_data).mean(axis=1)

#     # Combine actual values for the full dataset
#     actual_values = np.concatenate([actual_train_values, actual_test_values])

#     # Ensure the lengths match for comparison
#     comparison_length = min(len(actual_values), len(herd_full_prediction))

#     # Forecasting: Predict future values (15 days) based on the last available data
#     last_sequence = full_data[-sequence_length:].reshape(1, sequence_length, 28)
#     forecast = []
#     for _ in range(15):
#         forecast_pred = model.predict(last_sequence)
#         forecast.append(forecast_pred)
#         last_sequence = np.roll(last_sequence, -1, axis=1)  # Shift data
#         last_sequence[0, -1, :] = forecast_pred  # Replace the last entry with the new prediction

#     # Inverse transform the forecast to the original scale
#     forecast_inverse = scaler.inverse_transform(np.array(forecast).reshape(-1, 28))
#     forecast_line = forecast_inverse.mean(axis=1)

#     # ======= Extend Dates for Forecast =======
#     forecast_dates = pd.date_range(start=dates[-1] + pd.Timedelta(days=1), periods=15).values
#     extended_dates = np.concatenate([dates, forecast_dates])


#     # ======= LSTM Classification Model =======
#     def preprocess_data_classification(data, lag=2):
#         data_cleaned = data.apply(pd.to_numeric, errors='coerce').ffill()  # Fill missing values forward
#         data_lagged = data_cleaned.copy()

#         selected_columns = data_cleaned.iloc[:, :28]  # Select the first 28 columns only
#         for col in selected_columns.columns:
#             for i in range(1, lag + 1):
#                 data_lagged[f'{col}_lag{i}'] = selected_columns[col].shift(i, fill_value=selected_columns[col].iloc[0])

#         # Ensure we're left with only 28 features for LSTM input
#         final_lagged_data = data_lagged.iloc[:, :28]

#         return final_lagged_data

#     # Prepare data for classification
#     lagged_data = preprocess_data_classification(pd.DataFrame(data_scaled))

#     # Ensure lagged data has the correct shape (samples, timesteps, features)
#     X_class = lagged_data.values
#     X_class = X_class.reshape((X_class.shape[0], 1, X_class.shape[1]))

#     # Check if the classification model exists
#     if not os.path.exists(classification_model_path):
#         classification_model = Sequential([
#             LSTM(150, return_sequences=True, input_shape=(1, X_class.shape[2])),
#             Dropout(0.3),
#             LSTM(150, return_sequences=False),
#             Dropout(0.3),
#             Dense(50),
#             Dense(3, activation='softmax')  # 3 classes for alerts: 0, 1, 2
#         ])

#         classification_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

#         y_class = np.mean(lagged_data.values, axis=1)
#         max_activity = np.max(y_class)
#         y_class_labels = np.array([classify_alert(activity, max_activity)[0] for activity in y_class])
#         y_class_labels = to_categorical(y_class_labels, num_classes=3)

#         # Train the classification model
#         classification_model.fit(X_class, y_class_labels, batch_size=4, epochs=100, verbose=1)

#         # Save the classification model
#         classification_model.save(classification_model_path)
#     else:
#         classification_model = load_model(classification_model_path)

#     # Make predictions for classification
#     class_predictions = classification_model.predict(X_class)
#     combined_classification_classes = np.argmax(class_predictions, axis=1)

#     # Generate forecast for classification
#     last_class_sequence = X_class[-1]
#     class_forecast = []
#     for _ in range(15):
#         next_class_pred = classification_model.predict(last_class_sequence.reshape(1, 1, -1))
#         class_forecast.append(np.argmax(next_class_pred))
#         last_class_sequence = np.roll(last_class_sequence, -1)
#         last_class_sequence[0, -1] = np.argmax(next_class_pred)

#     # ======= Classification Accuracy and RMSE Calculation =======
#     def calculate_classification_accuracy(y_true, y_pred):
#         accuracy = accuracy_score(y_true, y_pred) * 100
#         mse = mean_squared_error(y_true, y_pred)
#         rmse = np.sqrt(mse)
#         max_value = np.max(y_true)
#         classification_rmse_percentage = (1 - (rmse / max_value)) * 100 if max_value > 0 else 100
#         return accuracy, classification_rmse_percentage

#     classification_accuracy, classification_rmse_percentage = calculate_classification_accuracy(
#         np.concatenate([combined_classification_classes, class_forecast]),
#         np.concatenate([combined_classification_classes, class_forecast])
#     )

#     # ======= Generate Alert Table =======
#     def generate_alert_table(predictions, classification_preds, dates, cow_alerts):
#         table_data = []
#         max_activity = np.max(predictions)

#         for i, (activity, classification_pred) in enumerate(zip(predictions, classification_preds)):
#             alert_num, alert_desc = classify_alert(activity, max_activity)
#             date_str = pd.to_datetime(dates[i]).strftime('%Y-%m-%d')

#             classification_desc = ["Green Alert", "Orange Alert", "Red Alert"][classification_pred]

#             cow_alert_row = cow_alerts[cow_alerts['Date'] == pd.to_datetime(date_str)]
#             cow_alert_val = "-" if cow_alert_row.empty else cow_alert_row['Group Mean'].values[0]

#             table_data.append({
#                 'date': date_str,
#                 'actual_activity': activity,
#                 'classification_alert_number': alert_num,
#                 'classification_alert': classification_desc,
#                 'cow_alert': cow_alert_val
#             })

#         return table_data

#     # Collect table data
#     table_data = generate_alert_table(
#         np.concatenate([herd_full_prediction, forecast_line]),
#         np.concatenate([combined_classification_classes, class_forecast]),
#         extended_dates, cow_alerts
#     )

#     # ======= Generate Confusion Matrix and Final Herd Alert =======
#     def generate_confusion_matrix_and_herd_alert(predictions, classification_preds, cow_alerts, dates):
#         true_labels = []
#         pred_labels = []

#         for i, date in enumerate(dates):
#             cow_alert_row = cow_alerts[cow_alerts['Date'] == pd.to_datetime(date)]
#             if not cow_alert_row.empty:
#                 true_alert = cow_alert_row['Group Mean'].values[0]
#                 true_labels.append(true_alert)
#                 if i < len(classification_preds):
#                     pred_labels.append(classification_preds[i])

#         all_possible_labels = [0, 1, 2]
#         cm = confusion_matrix(true_labels, pred_labels, labels=all_possible_labels)

#         target_names = ["Green Alert", "Orange Alert", "Red Alert"]
#         report = classification_report(true_labels, pred_labels, target_names=target_names, zero_division=0)

#         alert_counts = np.bincount(pred_labels, minlength=len(all_possible_labels))
#         final_herd_alert = np.argmax(alert_counts)
#         alert_map = {0: "Green Alert", 1: "Orange Alert", 2: "Red Alert"}
#         final_alert_text = f"\nFinal Alert for the Entire Herd: {alert_map[final_herd_alert]}"

#         report_text = f"Confusion Matrix:\n{cm}\n\nClassification Report:\n{report}\n{final_alert_text}"
#         print(report_text)
#         return report_text

#     # Generate report text
#     report_text = generate_confusion_matrix_and_herd_alert(
#         np.concatenate([herd_full_prediction, forecast_line]),
#         np.concatenate([combined_classification_classes, class_forecast]),
#         cow_alerts, extended_dates
#     )



#     # ======= PDF Report Generation =======
#     def save_report_to_pdf(report_text, folder, report_number, table_data):
#         pdf_path = os.path.join(folder, f"Report {report_number}.pdf")
        
#         # Create instance of FPDF class
#         pdf = FPDF()
#         pdf.set_auto_page_break(auto=True, margin=15)
#         pdf.add_page()

#         # Add title
#         pdf.set_font("Arial", 'B', 16)
#         pdf.cell(200, 10, "Entire Herd Activity Report", ln=True, align='C')

#         # Add report text (Confusion Matrix and Classification Report)
#         pdf.set_font("Arial", '', 12)
#         for line in report_text.splitlines():
#             pdf.multi_cell(0, 10, line)

#         # Add some space before the table
#         pdf.ln(10)

#         # Add table header
#         pdf.set_font("Arial", 'B', 12)
#         pdf.cell(40, 10, 'Date', 1, 0, 'C')
#         pdf.cell(50, 10, 'Actual Activity', 1, 0, 'C')
#         pdf.cell(60, 10, 'Classification Alert Number', 1, 0, 'C')
#         pdf.cell(60, 10, 'Classification Alert', 1, 0, 'C')
#         pdf.cell(40, 10, 'Cow Alert', 1, 1, 'C')

#         # Add table content
#         pdf.set_font("Arial", '', 12)
#         for row in table_data:
#             pdf.cell(40, 10, str(row['date']), 1)
#             pdf.cell(50, 10, f"{row['actual_activity']:.2f}", 1)
#             pdf.cell(60, 10, str(row['classification_alert_number']), 1)
#             pdf.cell(60, 10, str(row['classification_alert']), 1)
#             pdf.cell(40, 10, str(row['cow_alert']), 1, 1)

#         # Save the pdf with the specified path
#         pdf.output(pdf_path)

#     # Ensure the report folder exists
#     if not os.path.exists(report_folder):
#         os.makedirs(report_folder)

#     # Create a new report folder and determine the next report number
#     current_report_folder = create_new_folder(report_folder, "Report")
#     report_number = current_report_folder.split()[-1]

#     # Save the report to PDF with the table data
#     save_report_to_pdf(report_text, report_folder, report_number, table_data)



#     # Final Alert Calculation

#     final_alert_text = generate_confusion_matrix_and_herd_alert(
#         np.concatenate([herd_full_prediction, forecast_line]),
#         np.concatenate([combined_classification_classes, class_forecast]),
#         cow_alerts, extended_dates
#     )

# # Display a pop-up window showing the final alert result
#     messagebox.showinfo("Final Alert Result", final_alert_text)

#     # Now, after the user has seen the alert, prompt them to save the model
#     if not reload_model_path and save_callback:  # Only do this if the model was trained (not reloaded)
#         save_callback(current_run_folder, model)
    

#     # Return the final alert text
   

#     # ======= Plotting Phase =======
#     fig = plt.figure(figsize=(10, 14))
    
#     # First plot (Regression Model)
#     ax1 = fig.add_axes([0.1, 0.45, 0.8, 0.45])
    
#     train_end_index = len(train_data) - sequence_length
#     forecast_start_index = comparison_length
    
#     # Plot the data
#     line1, = ax1.plot(np.arange(5) + 1, actual_values[:5], 'go-', label='Actual Data (First 5 Days)', markersize=4, linewidth=0.5)
#     line2, = ax1.plot(np.arange(5, comparison_length + 5) + 1, actual_values[:comparison_length], 'co-', label='Actual Data (Average)', markersize=4, linewidth=0.5)
#     line3, = ax1.plot(np.arange(5, comparison_length + 5) + 1, herd_full_prediction[:comparison_length], 'ro-', label='LSTM Predictions', markersize=4, linewidth=0.5)
#     line4, = ax1.plot(np.arange(forecast_start_index + 5, forecast_start_index + 20) + 1, forecast_line, 'yo-', label='Forecast (Next 15 Days)', markersize=4, linewidth=0.5)
    
#     # Add vertical lines for split points
#     ax1.axvline(x=forecast_start_index + 5, color='black', linewidth=1, linestyle='--')
#     ax1.axvline(x=train_end_index + 5, color='black', linewidth=1, linestyle='--')
    
#     ylim = ax1.get_ylim()
#     ax1.text(train_end_index + 5.5, ylim[1] * 0.95, 'Train-Test Split', rotation=90, verticalalignment='top', color='black', fontsize=10)
#     ax1.text(forecast_start_index + 5.5, ylim[1] * 0.95, 'Forecast Start', rotation=90, verticalalignment='top', color='black', fontsize=10)
    
#     ax1.set_title(f'LSTM Regression Model\nTrain RMSE Accuracy: {train_rmse_percentage:.2f}% | Test RMSE Accuracy: {test_rmse_percentage:.2f}%', color='black')
#     ax1.set_xlabel('Days', color='black')
#     ax1.set_ylabel('Activity (Normalized)', color='white')
#     ax1.legend(loc='lower left')
    
#     # Second plot (Classification Model)
#     ax2 = fig.add_axes([0.1, 0.12, 0.8, 0.22])
    
#     ax2.set_title(f'LSTM Classification Model\nClassification Accuracy: {classification_accuracy:.2f}% | Classification RMSE Accuracy: {classification_rmse_percentage:.2f}%', color='black')
#     ax2.set_xlabel('Days', color='black')
#     ax2.set_ylabel('Alert Level (0: Green, 1: Orange, 2: Red)', color='white')
#     ax2.set_ylim(0, 2.5)
#     ax2.set_yticks([-1, 0, 1, 2, 2.5])
#     ax2.set_yticklabels(["", 0, 1, 2, ""])
    
#     # Plot classification lines and points
#     for i in range(len(combined_classification_classes) - 1):
#         color = 'green' if combined_classification_classes[i] == 0 else 'orange' if combined_classification_classes[i] == 1 else 'red'
#         ax2.plot([i + 1, i + 2], [combined_classification_classes[i], combined_classification_classes[i + 1]], color=color, linewidth=0.5)
    
#     for i, classification in enumerate(combined_classification_classes):
#         color = 'green' if classification == 0 else 'orange' if classification == 1 else 'red'
#         ax2.scatter(i + 1, classification, color=color, s=21)
    
#     for i in range(len(class_forecast) - 1):
#         color = 'green' if class_forecast[i] == 0 else 'orange' if class_forecast[i] == 1 else 'red'
#         ax2.plot([forecast_start_index + i + 6, forecast_start_index + i + 7], [class_forecast[i], class_forecast[i + 1]], color=color, linewidth=0.5)
    
#     for i, classification in enumerate(class_forecast):
#         color = 'green' if classification == 0 else 'orange' if classification == 1 else 'red'
#         ax2.scatter(forecast_start_index + i + 6, classification, color=color, s=21)
    
#     # Cow alert plotting on the classification model
#     prev_x, prev_y = None, None
#     for i, date in enumerate(dates):
#         cow_alert_row = cow_alerts[cow_alerts['Date'] == pd.to_datetime(date)]
#         if not cow_alert_row.empty:
#             cow_alert_val = cow_alert_row['Group Mean'].values[0]
#             ax2.scatter(i + 1, cow_alert_val, color='cyan', s=21, label='Cow Alert' if prev_x is None else "")
#             if prev_x is not None and i == prev_x + 1:
#                 ax2.plot([prev_x + 1, i + 1], [prev_y, cow_alert_val], color='cyan', linewidth=0.3)
#             prev_x, prev_y = i, cow_alert_val
#         else:
#             prev_x, prev_y = None, None
    
#     ax2.axvline(x=train_end_index + 5, color='black', linewidth=1, linestyle='--')
#     ax2.axvline(x=forecast_start_index + 5, color='black', linewidth=1, linestyle='--')
    
#     # Apply mplcursors to both graphs
    
#     # Cursor for ax1 (Regression plot)
#     cursor1 = mplcursors.cursor([line1, line2, line3, line4], hover=True)
#     @cursor1.connect("add")
#     def on_add(sel):
#         idx = int(sel.index)
#         date = pd.to_datetime(extended_dates[idx]).strftime('%Y-%m-%d') if idx < len(extended_dates) else 'Forecast'
#         value = sel.target[1]
#         sel.annotation.set(text=f'Date: {date}\nValue: {value:.2f}', fontsize=8, color='black')
#         sel.annotation.get_bbox_patch().set(facecolor='white', alpha=0.8)
#         sel.annotation.arrow_patch.set(arrowstyle="->", fc="black", edgecolor="black", alpha=0.8)
    
#     # Cursor for ax2 (Classification plot)
#     cursor2 = mplcursors.cursor(ax2.collections, hover=True)
#     @cursor2.connect("add")
#     def on_add_classification(sel):
#         idx = int(sel.index)
#         date = pd.to_datetime(extended_dates[idx]).strftime('%Y-%m-%d') if idx < len(extended_dates) else 'Forecast'
#         value = sel.target[1]
#         sel.annotation.set(text=f'Date: {date}\nAlert Level: {int(value)}', fontsize=8, color='black')
#         sel.annotation.get_bbox_patch().set(facecolor='white', alpha=0.8)
#         sel.annotation.arrow_patch.set(arrowstyle="->", fc="black", edgecolor="black", alpha=0.8)
    
#     # Apply white background to axes and customize tick colors
# # Apply white background to axes and customize tick colors
# # Apply white background to axes and customize tick colors
#     for ax in [ax1, ax2]:
#         ax.set_facecolor('white')  # Change background to white
#         ax.xaxis.label.set_color('black')  # Change label color to black
#         ax.yaxis.label.set_color('black')  # Change label color to black
#         ax.tick_params(axis='x', colors='black')  # Change tick color to black
#         ax.tick_params(axis='y', colors='black')  # Change tick color to black
#         ax.grid(True, color='gray', linestyle='--', linewidth=0.5)  # Optional: Add gridlines if needed
    
        
        
#     # Draw the figure in tkinter frame
#     canvas = FigureCanvasTkAgg(fig, master=frame)
#     canvas.draw()
#     canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
#     after_graph_is_loaded()
    
    

#     return final_alert_text  
    
# # Helper function to classify alerts
# def classify_alert(activity, max_activity):
#     if activity < 0.4 * max_activity:
#         return 0, "Green Alert"
#     elif 0.4 * max_activity <= activity < 0.7 * max_activity:
#         return 1, "Orange Alert"
#     else:
#         return 2, "Red Alert"



# # Generic_Activity_model.py
import numpy as np
import os
import pandas as pd
import tkinter as tk
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import mean_squared_error, accuracy_score, confusion_matrix, classification_report
from tkinter import messagebox
from upload_data import get_uploaded_data_paths
import mplcursors

from fpdf import FPDF

plt.style.use('default')

def display_missing_data_popup():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showerror("Data Error", "No data uploaded! Please upload the necessary files to proceed.")
    root.destroy()

def generate_activity_model_graph(frame, after_graph_is_loaded, save_callback=None, reload_model_path=None):
    # Destroy all widgets in the frame to clear previous graphs
    for widget in frame.winfo_children():
        widget.destroy()

    # Define constants
    base_model_folder = "Generic-Activity-inputs LSTM-model"
    report_folder = "Entire Herd Activity Report"

    # Function to create a new folder for the current run
    def create_new_folder(base_folder, prefix):
        existing_folders = [folder for folder in os.listdir(base_folder) 
                            if os.path.isdir(os.path.join(base_folder, folder)) and folder.startswith(prefix)]
        
        if existing_folders:
            existing_numbers = []
            for folder in existing_folders:
                try:
                    # Extract the number at the end of the folder name and convert to int
                    existing_numbers.append(int(folder.split(" ")[-1]))
                except ValueError:
                    # If the folder name doesn't end with a number, skip it
                    continue
            next_number = max(existing_numbers) + 1 if existing_numbers else 1
        else:
            next_number = 1
    
        new_folder_name = f"{prefix} {next_number}"
        new_folder_path = os.path.join(base_folder, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)
        return new_folder_path

    # If reloading the model
    if reload_model_path:
        model_path = os.path.join(reload_model_path, "lstm_model.h5")
        classification_model_path = os.path.join(reload_model_path, "classification_model.h5")
    else:
        # Train a new model and create a new folder for the current run
        current_run_folder = create_new_folder(base_model_folder, "Entire Herd")
        model_path = os.path.join(current_run_folder, "lstm_model.h5")
        classification_model_path = os.path.join(current_run_folder, "classification_model.h5")

    # Load the activity dataset (replace hardcoded path)
    activity_file_path, _ = get_uploaded_data_paths()
    
    if not activity_file_path:
        messagebox.showerror("Error", "Please upload the activity CSV file.")
        return
    
    data = pd.read_csv(activity_file_path)
        # Load the Cow_Alerts.csv file
    cow_alerts_path = 'C:/Users/Jyothesh karnam/Desktop/Dairy Herd Monitoring/User Information/Datasets/Cow_Alerts.csv'
    #     cow_alerts_path = 'C:/Users/Jyothesh karnam/Desktop/Dairy Herd Monitoring/User Information/Datasets/Cow_Alerts.csv'
    cow_alerts = pd.read_csv(cow_alerts_path)
    cow_alerts['Date'] = pd.to_datetime(cow_alerts['Date'])

    # Extract the 'Group mean' column for comparison
    group_mean = data['Group mean'].values

    # Extract the dates for future usage
    dates = pd.to_datetime(data['Unnamed: 0']).values

    # Drop the 'Group mean' and 'Unnamed: 0' (date) columns
    data_without_group_mean = data.drop(columns=['Group mean', 'Unnamed: 0'])

    # Normalize the data
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data_without_group_mean)

    # Split the data into training and testing sets (80/20 split)
    train_data, test_data = train_test_split(data_scaled, test_size=0.2, shuffle=False)

    # Define the sequence length
    sequence_length = 5

    # Function to create sequences for LSTM input
    def create_sequences(data, sequence_length):
        sequences = []
        for i in range(len(data) - sequence_length):
            sequence = data[i:i + sequence_length]
            sequences.append(sequence)
        return np.array(sequences)

    # Create sequences for training and testing data
    X_train = create_sequences(train_data, sequence_length)
    X_test = create_sequences(test_data, sequence_length)

    # Use the next time step as the target for prediction
    y_train = train_data[sequence_length:]
    y_test = test_data[sequence_length:]

    # Reshape X_train and X_test for LSTM input
    X_train = X_train.reshape((X_train.shape[0], sequence_length, X_train.shape[2]))
    X_test = X_test.reshape((X_test.shape[0], sequence_length, X_test.shape[2]))

    # If we are reloading the model
    if reload_model_path and os.path.exists(model_path):
        print("Loading saved regression model...")
        model = load_model(model_path)
        # Recompile the model to reset the optimizer
        model.compile(optimizer='adam', loss='mean_squared_error')
    else:
        print("Training a new model...")
        # Build and train a new LSTM model for regression
        model = Sequential([
            LSTM(100, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=False),
            Dropout(0.2),
            Dense(28)  # Predicting the next activity for each of the 28 cows
        ])
        # Compile the model
        model.compile(optimizer='adam', loss='mean_squared_error')

        # Train the model
        model.fit(X_train, y_train, epochs=100, batch_size=16, validation_data=(X_test, y_test), verbose=1)

        # Save the regression model
        model.save(model_path)

    # Continue with the rest of the code (predictions, plotting, PDF generation, etc.)

    # Call after_graph_is_loaded callback when done
    after_graph_is_loaded()

    # If save_callback exists and we're not reloading, prompt for saving the model
    if not reload_model_path and save_callback:
        save_callback(current_run_folder, model)



    # Make predictions for training and testing sets
    train_predictions_scaled = model.predict(X_train)
    test_predictions_scaled = model.predict(X_test)

    # Inverse transform the predictions to get them back to the original scale
    train_predictions = scaler.inverse_transform(train_predictions_scaled)
    test_predictions = scaler.inverse_transform(test_predictions_scaled)
    y_train_actual = scaler.inverse_transform(y_train)
    y_test_actual = scaler.inverse_transform(y_test)

    # ======= RMSE Calculation =======
    rmse_train = np.sqrt(mean_squared_error(y_train_actual, train_predictions))
    rmse_test = np.sqrt(mean_squared_error(y_test_actual, test_predictions))

    train_rmse_percentage = (1 - (rmse_train / np.max(y_train_actual))) * 100
    test_rmse_percentage = (1 - (rmse_test / np.max(y_test_actual))) * 100

    # Generate predictions for the entire dataset (train + test combined)
    full_data = np.vstack([train_data, test_data])
    X_full = create_sequences(full_data, sequence_length)
    predictions_full = model.predict(X_full)

    # Inverse transform the predictions to the original scale
    predictions_full_inverse = scaler.inverse_transform(predictions_full)

    # Averaging the predictions across all cows to get a single prediction line representing the entire herd
    herd_full_prediction = predictions_full_inverse.mean(axis=1)

    # Inverse transform to get actual values for the full dataset (train + test combined)
    actual_train_values = scaler.inverse_transform(train_data[sequence_length:]).mean(axis=1)
    actual_test_values = scaler.inverse_transform(test_data).mean(axis=1)

    # Combine actual values for the full dataset
    actual_values = np.concatenate([actual_train_values, actual_test_values])

    # Ensure the lengths match for comparison
    comparison_length = min(len(actual_values), len(herd_full_prediction))

    # Forecasting: Predict future values (15 days) based on the last available data
    last_sequence = full_data[-sequence_length:].reshape(1, sequence_length, 28)
    forecast = []
    for _ in range(15):
        forecast_pred = model.predict(last_sequence)
        forecast.append(forecast_pred)
        last_sequence = np.roll(last_sequence, -1, axis=1)  # Shift data
        last_sequence[0, -1, :] = forecast_pred  # Replace the last entry with the new prediction

    # Inverse transform the forecast to the original scale
    forecast_inverse = scaler.inverse_transform(np.array(forecast).reshape(-1, 28))
    forecast_line = forecast_inverse.mean(axis=1)

    # ======= Extend Dates for Forecast =======
    forecast_dates = pd.date_range(start=dates[-1] + pd.Timedelta(days=1), periods=15).values
    extended_dates = np.concatenate([dates, forecast_dates])


    # ======= LSTM Classification Model =======
    def preprocess_data_classification(data, lag=2):
        data_cleaned = data.apply(pd.to_numeric, errors='coerce').ffill()  # Fill missing values forward
        data_lagged = data_cleaned.copy()

        selected_columns = data_cleaned.iloc[:, :28]  # Select the first 28 columns only
        for col in selected_columns.columns:
            for i in range(1, lag + 1):
                data_lagged[f'{col}_lag{i}'] = selected_columns[col].shift(i, fill_value=selected_columns[col].iloc[0])

        # Ensure we're left with only 28 features for LSTM input
        final_lagged_data = data_lagged.iloc[:, :28]

        return final_lagged_data

    # Prepare data for classification
    lagged_data = preprocess_data_classification(pd.DataFrame(data_scaled))

    # Ensure lagged data has the correct shape (samples, timesteps, features)
    X_class = lagged_data.values
    X_class = X_class.reshape((X_class.shape[0], 1, X_class.shape[1]))

    # Check if the classification model exists
    if not os.path.exists(classification_model_path):
        classification_model = Sequential([
            LSTM(150, return_sequences=True, input_shape=(1, X_class.shape[2])),
            Dropout(0.3),
            LSTM(150, return_sequences=False),
            Dropout(0.3),
            Dense(50),
            Dense(3, activation='softmax')  # 3 classes for alerts: 0, 1, 2
        ])

        classification_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

        y_class = np.mean(lagged_data.values, axis=1)
        max_activity = np.max(y_class)
        y_class_labels = np.array([classify_alert(activity, max_activity)[0] for activity in y_class])
        y_class_labels = to_categorical(y_class_labels, num_classes=3)

        # Train the classification model
        classification_model.fit(X_class, y_class_labels, batch_size=4, epochs=100, verbose=1)

        # Save the classification model
        classification_model.save(classification_model_path)
    else:
        classification_model = load_model(classification_model_path)

    # Make predictions for classification
    class_predictions = classification_model.predict(X_class)
    combined_classification_classes = np.argmax(class_predictions, axis=1)

    # Generate forecast for classification
    last_class_sequence = X_class[-1]
    class_forecast = []
    for _ in range(15):
        next_class_pred = classification_model.predict(last_class_sequence.reshape(1, 1, -1))
        class_forecast.append(np.argmax(next_class_pred))
        last_class_sequence = np.roll(last_class_sequence, -1)
        last_class_sequence[0, -1] = np.argmax(next_class_pred)

    # ======= Classification Accuracy and RMSE Calculation =======
    def calculate_classification_accuracy(y_true, y_pred):
        accuracy = accuracy_score(y_true, y_pred) * 100
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        max_value = np.max(y_true)
        classification_rmse_percentage = (1 - (rmse / max_value)) * 100 if max_value > 0 else 100
        return accuracy, classification_rmse_percentage

    classification_accuracy, classification_rmse_percentage = calculate_classification_accuracy(
        np.concatenate([combined_classification_classes, class_forecast]),
        np.concatenate([combined_classification_classes, class_forecast])
    )

    # ======= Generate Alert Table =======
    def generate_alert_table(predictions, classification_preds, dates, cow_alerts):
        table_data = []
        max_activity = np.max(predictions)

        for i, (activity, classification_pred) in enumerate(zip(predictions, classification_preds)):
            alert_num, alert_desc = classify_alert(activity, max_activity)
            date_str = pd.to_datetime(dates[i]).strftime('%Y-%m-%d')

            classification_desc = ["Green Alert", "Orange Alert", "Red Alert"][classification_pred]

            cow_alert_row = cow_alerts[cow_alerts['Date'] == pd.to_datetime(date_str)]
            cow_alert_val = "-" if cow_alert_row.empty else cow_alert_row['Group Mean'].values[0]

            table_data.append({
                'date': date_str,
                'actual_activity': activity,
                'classification_alert_number': alert_num,
                'classification_alert': classification_desc,
                'cow_alert': cow_alert_val
            })

        return table_data

    # Collect table data
    table_data = generate_alert_table(
        np.concatenate([herd_full_prediction, forecast_line]),
        np.concatenate([combined_classification_classes, class_forecast]),
        extended_dates, cow_alerts
    )

    # ======= Generate Confusion Matrix and Final Herd Alert =======
    def generate_confusion_matrix_and_herd_alert(predictions, classification_preds, cow_alerts, dates):
        true_labels = []
        pred_labels = []

        for i, date in enumerate(dates):
            cow_alert_row = cow_alerts[cow_alerts['Date'] == pd.to_datetime(date)]
            if not cow_alert_row.empty:
                true_alert = cow_alert_row['Group Mean'].values[0]
                true_labels.append(true_alert)
                if i < len(classification_preds):
                    pred_labels.append(classification_preds[i])

        all_possible_labels = [0, 1, 2]
        cm = confusion_matrix(true_labels, pred_labels, labels=all_possible_labels)

        target_names = ["Green Alert", "Orange Alert", "Red Alert"]
        report = classification_report(true_labels, pred_labels, target_names=target_names, zero_division=0)

        alert_counts = np.bincount(pred_labels, minlength=len(all_possible_labels))
        final_herd_alert = np.argmax(alert_counts)
        alert_map = {0: "Green Alert", 1: "Orange Alert", 2: "Red Alert"}
        final_alert_text = f"\nFinal Alert for the Entire Herd: {alert_map[final_herd_alert]}"

        report_text = f"Confusion Matrix:\n{cm}\n\nClassification Report:\n{report}\n{final_alert_text}"
        print(report_text)
        return report_text

    # Generate report text
    report_text = generate_confusion_matrix_and_herd_alert(
        np.concatenate([herd_full_prediction, forecast_line]),
        np.concatenate([combined_classification_classes, class_forecast]),
        cow_alerts, extended_dates
    )



    # ======= PDF Report Generation =======
    def save_report_to_pdf(report_text, folder, report_number, table_data):
        pdf_path = os.path.join(folder, f"Report {report_number}.pdf")
        
        # Create instance of FPDF class
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Add title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "Entire Herd Activity Report", ln=True, align='C')

        # Add report text (Confusion Matrix and Classification Report)
        pdf.set_font("Arial", '', 12)
        for line in report_text.splitlines():
            pdf.multi_cell(0, 10, line)

        # Add some space before the table
        pdf.ln(10)

        # Add table header
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(40, 10, 'Date', 1, 0, 'C')
        pdf.cell(50, 10, 'Actual Activity', 1, 0, 'C')
        pdf.cell(60, 10, 'Classification Alert Number', 1, 0, 'C')
        pdf.cell(60, 10, 'Classification Alert', 1, 0, 'C')
        pdf.cell(40, 10, 'Cow Alert', 1, 1, 'C')

        # Add table content
        pdf.set_font("Arial", '', 12)
        for row in table_data:
            pdf.cell(40, 10, str(row['date']), 1)
            pdf.cell(50, 10, f"{row['actual_activity']:.2f}", 1)
            pdf.cell(60, 10, str(row['classification_alert_number']), 1)
            pdf.cell(60, 10, str(row['classification_alert']), 1)
            pdf.cell(40, 10, str(row['cow_alert']), 1, 1)

        # Save the pdf with the specified path
        pdf.output(pdf_path)

    # Ensure the report folder exists
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)

    # Create a new report folder and determine the next report number
    current_report_folder = create_new_folder(report_folder, "Report")
    report_number = current_report_folder.split()[-1]

    # Save the report to PDF with the table data
    save_report_to_pdf(report_text, report_folder, report_number, table_data)



    # Final Alert Calculation

    final_alert_text = generate_confusion_matrix_and_herd_alert(
        np.concatenate([herd_full_prediction, forecast_line]),
        np.concatenate([combined_classification_classes, class_forecast]),
        cow_alerts, extended_dates
    )

# Display a pop-up window showing the final alert result
    messagebox.showinfo("Final Alert Result", final_alert_text)

    # Now, after the user has seen the alert, prompt them to save the model
    if not reload_model_path and save_callback:  # Only do this if the model was trained (not reloaded)
        save_callback(current_run_folder, model)
    

    # Return the final alert text
   

    # ======= Plotting Phase =======
    fig = plt.figure(figsize=(10, 14))
    
    # First plot (Regression Model)
    ax1 = fig.add_axes([0.1, 0.45, 0.8, 0.45])
    
    train_end_index = len(train_data) - sequence_length
    forecast_start_index = comparison_length
    
    # Plot the data
    line1, = ax1.plot(np.arange(5) + 1, actual_values[:5], 'go-', label='Actual Data (First 5 Days)', markersize=4, linewidth=0.5)
    line2, = ax1.plot(np.arange(5, comparison_length + 5) + 1, actual_values[:comparison_length], 'co-', label='Actual Data (Average)', markersize=4, linewidth=0.5)
    line3, = ax1.plot(np.arange(5, comparison_length + 5) + 1, herd_full_prediction[:comparison_length], 'ro-', label='LSTM Predictions', markersize=4, linewidth=0.5)
    line4, = ax1.plot(np.arange(forecast_start_index + 5, forecast_start_index + 20) + 1, forecast_line, 'yo-', label='Forecast (Next 15 Days)', markersize=4, linewidth=0.5)
    
    # Add vertical lines for split points
    ax1.axvline(x=forecast_start_index + 5, color='black', linewidth=1, linestyle='--')
    ax1.axvline(x=train_end_index + 5, color='black', linewidth=1, linestyle='--')
    
    ylim = ax1.get_ylim()
    ax1.text(train_end_index + 5.5, ylim[1] * 0.95, 'Train-Test Split', rotation=90, verticalalignment='top', color='black', fontsize=10)
    ax1.text(forecast_start_index + 5.5, ylim[1] * 0.95, 'Forecast Start', rotation=90, verticalalignment='top', color='black', fontsize=10)
    
    ax1.set_title(f'LSTM Regression Model\nTrain RMSE Accuracy: {train_rmse_percentage:.2f}% | Test RMSE Accuracy: {test_rmse_percentage:.2f}%', color='white')
    ax1.set_xlabel('Days', color='white')
    ax1.set_ylabel('Activity (Normalized)', color='white')
    ax1.legend(loc='lower left')
    
    # Second plot (Classification Model)
    ax2 = fig.add_axes([0.1, 0.12, 0.8, 0.22])
    
    ax2.set_title(f'LSTM Classification Model\nClassification Accuracy: {classification_accuracy:.2f}% | Classification RMSE Accuracy: {classification_rmse_percentage:.2f}%', color='white')
    ax2.set_xlabel('Days', color='white')
    ax2.set_ylabel('Alert Level (0: Green, 1: Orange, 2: Red)', color='white')
    ax2.set_ylim(0, 2.5)
    ax2.set_yticks([-1, 0, 1, 2, 2.5])
    ax2.set_yticklabels(["", 0, 1, 2, ""])
    
    # Plot classification lines and points
    for i in range(len(combined_classification_classes) - 1):
        color = 'green' if combined_classification_classes[i] == 0 else 'orange' if combined_classification_classes[i] == 1 else 'red'
        ax2.plot([i + 1, i + 2], [combined_classification_classes[i], combined_classification_classes[i + 1]], color=color, linewidth=0.5)
    
    for i, classification in enumerate(combined_classification_classes):
        color = 'green' if classification == 0 else 'orange' if classification == 1 else 'red'
        ax2.scatter(i + 1, classification, color=color, s=21)
    
    for i in range(len(class_forecast) - 1):
        color = 'green' if class_forecast[i] == 0 else 'orange' if class_forecast[i] == 1 else 'red'
        ax2.plot([forecast_start_index + i + 6, forecast_start_index + i + 7], [class_forecast[i], class_forecast[i + 1]], color=color, linewidth=0.5)
    
    for i, classification in enumerate(class_forecast):
        color = 'green' if classification == 0 else 'orange' if classification == 1 else 'red'
        ax2.scatter(forecast_start_index + i + 6, classification, color=color, s=21)
    
    # Cow alert plotting on the classification model
    prev_x, prev_y = None, None
    for i, date in enumerate(dates):
        cow_alert_row = cow_alerts[cow_alerts['Date'] == pd.to_datetime(date)]
        if not cow_alert_row.empty:
            cow_alert_val = cow_alert_row['Group Mean'].values[0]
            ax2.scatter(i + 1, cow_alert_val, color='cyan', s=21, label='Cow Alert' if prev_x is None else "")
            if prev_x is not None and i == prev_x + 1:
                ax2.plot([prev_x + 1, i + 1], [prev_y, cow_alert_val], color='cyan', linewidth=0.3)
            prev_x, prev_y = i, cow_alert_val
        else:
            prev_x, prev_y = None, None
    
    ax2.axvline(x=train_end_index + 5, color='black', linewidth=1, linestyle='--')
    ax2.axvline(x=forecast_start_index + 5, color='black', linewidth=1, linestyle='--')
    
    # Apply mplcursors to both graphs
    
    # Cursor for ax1 (Regression plot)
    cursor1 = mplcursors.cursor([line1, line2, line3, line4], hover=True)
    @cursor1.connect("add")
    def on_add(sel):
        idx = int(sel.index)
        date = pd.to_datetime(extended_dates[idx]).strftime('%Y-%m-%d') if idx < len(extended_dates) else 'Forecast'
        value = sel.target[1]
        sel.annotation.set(text=f'Date: {date}\nValue: {value:.2f}', fontsize=8, color='black')
        sel.annotation.get_bbox_patch().set(facecolor='white', alpha=0.8)
        sel.annotation.arrow_patch.set(arrowstyle="->", fc="black", edgecolor="black", alpha=0.8)
    
    # Cursor for ax2 (Classification plot)
    cursor2 = mplcursors.cursor(ax2.collections, hover=True)
    @cursor2.connect("add")
    def on_add_classification(sel):
        idx = int(sel.index)
        date = pd.to_datetime(extended_dates[idx]).strftime('%Y-%m-%d') if idx < len(extended_dates) else 'Forecast'
        value = sel.target[1]
        sel.annotation.set(text=f'Date: {date}\nAlert Level: {int(value)}', fontsize=8, color='black')
        sel.annotation.get_bbox_patch().set(facecolor='white', alpha=0.8)
        sel.annotation.arrow_patch.set(arrowstyle="->", fc="black", edgecolor="black", alpha=0.8)
    
    # Apply white background to axes and customize tick colors
# Apply white background to axes and customize tick colors
# Apply white background to axes and customize tick colors
    for ax in [ax1, ax2]:
        ax.set_facecolor('white')  # Change background to white
        ax.xaxis.label.set_color('black')  # Change label color to black
        ax.yaxis.label.set_color('black')  # Change label color to black
        ax.tick_params(axis='x', colors='black')  # Change tick color to black
        ax.tick_params(axis='y', colors='black')  # Change tick color to black
        ax.grid(True, color='gray', linestyle='--', linewidth=0.5)  # Optional: Add gridlines if needed
    
        
        
    # Draw the figure in tkinter frame
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    after_graph_is_loaded()
    
    

    return final_alert_text  
    
# Helper function to classify alerts
def classify_alert(activity, max_activity):
    if activity < 0.4 * max_activity:
        return 0, "Green Alert"
    elif 0.4 * max_activity <= activity < 0.7 * max_activity:
        return 1, "Orange Alert"
    else:
        return 2, "Red Alert"



