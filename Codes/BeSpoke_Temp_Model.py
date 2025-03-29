
# BeSpoke_Temp_Model.py
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout
from keras.optimizers import Adam
import joblib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.offsetbox import AnnotationBbox, TextArea
import tkinter as tk
from data_utils import get_uploaded_data_paths 
from tkinter import messagebox


# Define the model directory
model_dir = 'BeSpoke Temperature Model'

# Function to create lagged features
def create_lagged_features(df, temp_column, lag=2):
    df_lagged = df.copy()
    for col in df.columns:
        for i in range(1, lag + 1):
            df_lagged[f'{col}_lag{i}'] = df[col].shift(i, fill_value=df[col].iloc[0])  # Shift with padding
    return df_lagged

# Function to preprocess data
def preprocess_data(data, temp_id, lag=2):
    data_cleaned = data.apply(pd.to_numeric, errors='coerce').fillna(method='ffill')  # Forward fill missing values
    data_lagged = create_lagged_features(data_cleaned, temp_id, lag=lag)
    data_lagged[f'{temp_id}_rolling'] = data_lagged[temp_id].rolling(window=3, min_periods=1).mean()

    # Define features and target
    X = data_lagged.drop(temp_id, axis=1).values
    y = data_lagged[temp_id].values

    # Feature scaling using MinMaxScaler
    scaler_X = MinMaxScaler(feature_range=(0, 1))
    scaler_y = MinMaxScaler(feature_range=(0, 1))

    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

    # Reshape input to be 3D for LSTM [samples, time steps, features]
    X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

    # Split data into training and testing sets (80% train, 20% test)
    train_size = int(len(X_scaled) * 0.8)
    X_train, X_test = X_scaled[:train_size], X_scaled[train_size:]
    y_train, y_test = y_scaled[:train_size], y_scaled[train_size:]

    return X_train, X_test, y_train, y_test, scaler_X, scaler_y

# Function to generate the bespoke temperature model graph
def generate_bespoke_temp_model_graph(frame, temp_id, after_graph_is_loaded):
    # Destroy all widgets in the frame to clear previous graphs
    for widget in frame.winfo_children():
        widget.destroy()

    # Load dataset
    _, temperature_file_path = get_uploaded_data_paths()  # Assuming this returns (activity_path, temperature_path)

    if not temperature_file_path:
        messagebox.showerror("Error", "Please upload the activity CSV file.")
        return
    # Load dataset
    data = pd.read_csv(temperature_file_path)

    # Drop non-numeric and irrelevant columns such as 'Unnamed: 0', 'Date', etc.
    if 'Unnamed: 0' in data.columns:
        data = data.drop('Unnamed: 0', axis=1)
    if 'Date' in data.columns:
        data = data.drop('Date', axis=1)

    # List of all temperature IDs (after removing non-numeric columns)
    temp_ids = [col for col in data.columns if col != 'Date']

    # Ensure the temp ID exists in the dataset
    if temp_id not in temp_ids:
        raise ValueError(f"Temperature ID {temp_id} not found in the dataset")

    # Path to the specific temperature model folder
    temp_model_dir = os.path.join(model_dir, f'Temperature_{temp_id}_model')
    model_path = os.path.join(temp_model_dir, f'lstm_model_{temp_id}.keras')

    # Check if the model directory exists
    if not os.path.exists(temp_model_dir):
        os.makedirs(temp_model_dir)

    # Preprocess the data for the temperature column
    X_train, X_test, y_train, y_test, scaler_X, scaler_y = preprocess_data(data, temp_id)

    # Load or create the LSTM model
    if os.path.exists(model_path):
        print("Loading saved model and retraining...")
        model = load_model(model_path)

        # Retrain the loaded model with the new data
        model.fit(X_train, y_train, batch_size=4, epochs=200, verbose=1)

        # Save the retrained model
        model.save(model_path)
    else:
        print("Creating and training a new model...")
        # Create and train the LSTM model
        model = Sequential()
        model.add(LSTM(150, return_sequences=True, input_shape=(1, X_train.shape[2])))
        model.add(Dropout(0.3))
        model.add(LSTM(150, return_sequences=False))
        model.add(Dropout(0.3))
        model.add(Dense(50))
        model.add(Dense(1))

        # Compile the model with Adam optimizer and a lower learning rate
        optimizer = Adam(learning_rate=0.0005)
        model.compile(optimizer=optimizer, loss='mean_squared_error')

        # Train the model with more epochs and smaller batch size
        model.fit(X_train, y_train, batch_size=4, epochs=200, verbose=1)

        # Save the model and scalers inside the temperature-specific folder
        model.save(os.path.join(temp_model_dir, f'lstm_model_{temp_id}.keras'))
        joblib.dump(scaler_X, os.path.join(temp_model_dir, f'scaler_X_{temp_id}.pkl'))
        joblib.dump(scaler_y, os.path.join(temp_model_dir, f'scaler_y_{temp_id}.pkl'))

    # Make predictions on both the training and testing datasets
    train_predictions_scaled = model.predict(X_train)
    test_predictions_scaled = model.predict(X_test)

    # Inverse transform the predictions to get them back to the original scale
    train_predictions = scaler_y.inverse_transform(train_predictions_scaled)
    test_predictions = scaler_y.inverse_transform(test_predictions_scaled)
    y_train_actual = scaler_y.inverse_transform(y_train)
    y_test_actual = scaler_y.inverse_transform(y_test)

    # Combine predictions and actual values for continuous plotting
    combined_predictions = np.concatenate((train_predictions, test_predictions), axis=0)
    combined_actual = np.concatenate((y_train_actual, y_test_actual), axis=0)

    # Calculate accuracy using Mean Absolute Percentage Error (MAPE)
    train_accuracy = 100 - np.mean(np.abs((y_train_actual - train_predictions) / y_train_actual)) * 100
    test_accuracy = 100 - np.mean(np.abs((y_test_actual - test_predictions) / y_test_actual)) * 100

    # Save the retrained model
    model.save(os.path.join(temp_model_dir, f'lstm_model_{temp_id}_retrained.keras'))

    # ====== Forecasting Phase ======
    forecast_days = 15

    # Get the last data point from the test set as the starting point for forecasting
    last_input = X_test[-1]

    # Create a list to store the forecasted values
    forecasted_values = []

    # Forecast for the next 15 days
    for day in range(forecast_days):
        # Predict the next day's value
        next_prediction_scaled = model.predict(last_input.reshape(1, 1, -1))
        
        # Inverse transform the prediction back to the original scale
        next_prediction = scaler_y.inverse_transform(next_prediction_scaled)
        
        # Store the forecasted value
        forecasted_values.append(next_prediction[0][0])
        
        # Update the last_input with the predicted value for the next iteration
        last_input = np.roll(last_input, -1)
        last_input[0, -1] = next_prediction_scaled[0][0]  # Replace with the predicted value

    # Convert forecasted values to a 2D array for consistent dimensions with predictions
    forecasted_values = np.array(forecasted_values).reshape(-1, 1)

    # ====== Plotting Phase ======
    # Set dark mode style for the plot
    plt.style.use('default')

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(14, 5))
    
    # Customize the axis colors for light mode
    ax.set_facecolor('white')  # Set the background to white
    ax.xaxis.label.set_color('black')  # Set x-axis label color to black
    ax.yaxis.label.set_color('black')  # Set y-axis label color to black
    ax.tick_params(axis='x', colors='black')  # Set x-axis tick color to black
    ax.tick_params(axis='y', colors='black')  # Set y-axis tick color to black

    # Use integer x-axis values instead of dates
    x_train = np.arange(1, len(y_train_actual) + 1)  # Starts from 1
    x_test = np.arange(len(y_train_actual) + 1, len(y_train_actual) + len(y_test_actual) + 1)  # Starts from the end of x_train + 1
    x_forecast = np.arange(len(combined_actual) + 1, len(combined_actual) + forecast_days + 1)  # Starts from the end of x_test + 1
    # Plot the actual data with glowing dark cyan color and thin lines
    line_actual, = ax.plot(np.concatenate((x_train, x_test)), combined_actual, color='#00FFFF', marker='o', 
                           label='Actual Data (Train + Test)', markersize=3, linewidth=0.8)

    # Plot the LSTM predictions as a dotted line
    line_predictions, = ax.plot(np.concatenate((x_train, x_test)), combined_predictions, color='#FF4500', 
                                linestyle='--', linewidth=1, label='LSTM Predictions')

    # Plot the forecasted values as a bright red thin line with data points
    line_forecast, = ax.plot(x_forecast, forecasted_values, color='red', linestyle='-', marker='o', 
                             markersize=3, linewidth=1, label='15-Day Forecast')

    # Calculate correct indices for the vertical lines
    forecast_start_index = len(x_train) + len(x_test)
    train_end_index = len(x_train)
    
    # Add the vertical lines for the train/test split and forecast start
    forecast_start_line = ax.axvline(x=forecast_start_index + 1, color='black', linewidth=1)
    train_test_line = ax.axvline(x=train_end_index + 1, color='black', linewidth=1)
    
    # Add vertical text for the lines
    ylim = ax.get_ylim()
    ax.text(train_end_index + 1.5, ylim[1] * 0.95, 'Train-Test Split', rotation=90, verticalalignment='top', color='black', fontsize=10)
    ax.text(forecast_start_index + 1.5, ylim[1] * 0.95, 'Forecast Start', rotation=90, verticalalignment='top', color='black', fontsize=10)

    # Modify the x-axis to show values 0, 10, 20, etc.
    ax.set_xticks(np.arange(0, forecast_start_index + 20, 10))

    # Add title and labels
    ax.set_title(f"Temperature {temp_id} Model | Train Accuracy: {train_accuracy:.2f}% | Test Accuracy: {test_accuracy:.2f}% | 15-Day Forecast", color='black')
    ax.set_xlabel('Time (Days)', color='black')
    ax.set_ylabel('Temperature', color='black')

    # Remove gridlines but keep the line style and thickness
    ax.grid(False)

    # Add legend, removing the vertical lines
    ax.legend(loc='lower left', labels=[
        'Actual Data (Train + Test)', 
        'LSTM Predictions', 
        '15-Day Forecast'
    ])

    # Tooltip-like event handler with black background
    annot = ax.annotate("", xy=(0,0), xytext=(15,15), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="white", ec="black"),
                        arrowprops=dict(arrowstyle="->", color="black"),
                        color="black")
    
    annot.set_visible(False)

    def get_closest_index(event, x_data, y_data):
        """Helper function to find the closest index to the mouse position"""
        distances = np.sqrt((x_data - event.xdata)**2 + (y_data - event.ydata)**2)
        return np.argmin(distances), np.min(distances)

    # Update the annotation with the correct label and values
    def update_annot(ind, line, label, x_data, y_data):
        annot.xy = (x_data[ind], y_data[ind])
        text = f"Day: {int(x_data[ind])}\n{label}: {y_data[ind]:.2f}"
        annot.set_text(text)

        # Adjust the position to keep the tooltip inside the plot
        pos_x = x_data[ind]
        pos_y = y_data[ind]
        
        # Get axis limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Adjust the tooltip position if it's too close to the edge
        offset_x = 15
        offset_y = 15
        
        if pos_x > xlim[1] - (xlim[1] - xlim[0]) * 0.1:
            offset_x = -50
        if pos_y > ylim[1] - (ylim[1] - ylim[0]) * 0.1:
            offset_y = -50
        
        annot.set_position((offset_x, offset_y))
        annot.get_bbox_patch().set_alpha(0.8)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            closest_dist = np.inf
            closest_line = None
            closest_label = None
            closest_ind = None
            closest_x_data = None
            closest_y_data = None
            
            # Iterate over each line and find the closest data point to the mouse
            for line, label in [
                (line_actual, "Actual Data"),
                (line_predictions, "LSTM Predictions"),
                (line_forecast, "15-Day Forecast")
            ]:
                x_data, y_data = line.get_data()
                ind, dist = get_closest_index(event, x_data, y_data)
                
                if dist < closest_dist:
                    closest_dist = dist
                    closest_line = line
                    closest_label = label
                    closest_ind = ind
                    closest_x_data = x_data
                    closest_y_data = y_data

            # If the closest distance is within a reasonable threshold, show the tooltip
            if closest_dist < 20:  # Adjust this threshold for sensitivity
                update_annot(closest_ind, closest_line, closest_label, closest_x_data, closest_y_data)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    # Attach the new graph to the canvas
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Call the after_graph_is_loaded callback after the graph is loaded
    after_graph_is_loaded()

