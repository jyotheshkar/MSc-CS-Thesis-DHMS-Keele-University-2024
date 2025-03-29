
# BeSpoke_Multi_Model.py
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout
from sklearn.linear_model import LinearRegression
from keras.optimizers import Adam
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.offsetbox import AnnotationBbox, TextArea
import tkinter as tk
from data_utils import get_uploaded_data_paths 
from data_utils import get_uploaded_data_paths


# Set directory path for saved models
model_dir = 'BeSpoke Multi Model'

# Function to generate the bespoke multi model graph
def generate_bespoke_multi_model_graph(frame, cow_id, after_graph_is_loaded):
    # Destroy all widgets in the frame to clear previous graphs
    for widget in frame.winfo_children():
        widget.destroy()

    # Function to create the plot
    def create_plot(cow_id, combined_data, train_accuracy, test_accuracy, combined_actual_scaled, combined_predictions_scaled, forecasted_values_scaled, overall_alert, forecast_days):
        # Create the figure and axis
        fig, ax = plt.subplots(figsize=(14, 5))
    
        # Plot actual data
        line_actual, = ax.plot(range(len(combined_actual_scaled)), combined_actual_scaled, color='#DA70D6', linestyle='-', linewidth=0.8, marker='o', markersize=4, label='Actual Combined Health Data')
    
        # Plot LSTM predictions
        line_predictions, = ax.plot(range(len(combined_predictions_scaled)), combined_predictions_scaled, color='#00FFFF', linestyle='--', linewidth=0.8, label='LSTM Predictions')
    
        # Determine the overall forecast line color based on the alert level
        if overall_alert == "Red Alert":
            forecast_line_color = 'red'
        elif overall_alert == "Orange Alert":
            forecast_line_color = 'orange'
        else:
            forecast_line_color = 'green'
    
        # Plot the forecast line with the overall alert color
        line_forecast, = ax.plot(range(len(combined_actual_scaled), len(combined_actual_scaled) + forecast_days),
                                 forecasted_values_scaled, color=forecast_line_color, linestyle='-', 
                                 linewidth=1.5, label=f'15-Day Forecast ({overall_alert})')
    
        # Plot individual data points with color coding based on health score
        for i, value in enumerate(forecasted_values_scaled):
            if value < 30:
                point_color = 'red'
            elif 30 <= value < 60:
                point_color = 'orange'
            else:
                point_color = 'green'
    
            # Plot the colored data points
            ax.plot(len(combined_actual_scaled) + i, value, 'o', color=point_color, markersize=6)
    
        # Customize the plot with titles, labels, and styles
        ax.set_title(f"Cow {cow_id} | Train Accuracy: {train_accuracy:.2f}% | Test Accuracy: {test_accuracy:.2f}% | {overall_alert}", color='white')
        ax.set_xlabel('Time Steps', color='white')
        ax.set_ylabel('Health Score (0-100)', color='white')
        ax.set_ylim([0, 100])
    
        # Calculate correct indices for the vertical lines
        forecast_start_index = len(combined_actual_scaled)
        train_end_index = forecast_start_index - forecast_days
        
        # Add a vertical yellow line at the forecast start
        forecast_start_line = ax.axvline(x=forecast_start_index + 1, color='yellow', linewidth=1)
        
        # Add a vertical white line at the train-test split
        train_test_line = ax.axvline(x=train_end_index + 1, color='white', linewidth=1)
        
        # Add vertical text for the lines
        ylim = ax.get_ylim()
        ax.text(train_end_index + 1.5, ylim[1] * 0.95, 'Train-Test Split', rotation=90, verticalalignment='top', color='white', fontsize=10)
        ax.text(forecast_start_index + 1.5, ylim[1] * 0.95, 'Forecast Start', rotation=90, verticalalignment='top', color='yellow', fontsize=10)
        
        # Modify the x-axis to show values 0, 10, 20, etc.
        ax.set_xticks(np.arange(0, forecast_start_index + 20, 10))
    
        # Add legend
        ax.legend(loc='lower left', facecolor='black', edgecolor='white', fontsize=10, labelcolor='white')
    
        return fig, ax, line_actual, line_predictions, line_forecast


    # Retrieve the dynamic file paths for temperature and activity data
    activity_data_path, temperature_data_path = get_uploaded_data_paths()

    if not activity_data_path or not temperature_data_path:
        raise ValueError("Activity or Temperature data not uploaded or found. Please upload both datasets.")

    # Read the temperature and activity datasets
    temperature_data = pd.read_csv(temperature_data_path)
    activity_data = pd.read_csv(activity_data_path)

    # Rename 'Unnamed: 0' to 'Date' for both datasets
    temperature_data.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
    activity_data.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)

    # Merge both datasets on the 'Date' column
    combined_data = pd.merge(temperature_data, activity_data, on='Date', suffixes=('_temp', '_activity'))

    # Check if models are already trained and saved
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

        # Train and save each cow model
        for column in combined_data.columns:
            if '_temp' in column:
                cow_id = column.split('_')[0]
                temp_column = f'{cow_id}_temp'
                activity_column = f'{cow_id}_activity'

                if temp_column in combined_data.columns and activity_column in combined_data.columns:
                    cow_data = combined_data[['Date', temp_column, activity_column]]
                    scaler = MinMaxScaler()
                    cow_data[[temp_column, activity_column]] = scaler.fit_transform(cow_data[[temp_column, activity_column]])

                    # Train the linear regression model
                    X = cow_data[[temp_column, activity_column]]
                    y = 0.5 * X[temp_column] + 0.5 * X[activity_column]
                    linear_model = LinearRegression()
                    linear_model.fit(X, y)
                    cow_data['learned_health_score'] = linear_model.predict(X)

                    scaler_health = MinMaxScaler()
                    cow_data['normalized_learned_health_score'] = scaler_health.fit_transform(cow_data[['learned_health_score']])

                    # Preprocess data for LSTM
                    def create_lagged_features(df, target_column, lag=2):
                        df_lagged = df.copy()
                        for i in range(1, lag + 1):
                            df_lagged[f'{target_column}_lag{i}'] = df[target_column].shift(i, fill_value=df[target_column].iloc[0])
                        return df_lagged

                    lagged_data = create_lagged_features(cow_data, 'normalized_learned_health_score', lag=2)
                    lagged_data = lagged_data.drop(columns=['Date'])

                    X_lagged = lagged_data.drop('normalized_learned_health_score', axis=1).values
                    y_lagged = lagged_data['normalized_learned_health_score'].values

                    scaler_X = MinMaxScaler(feature_range=(0, 1))
                    X_scaled = scaler_X.fit_transform(X_lagged)
                    X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

                    # Split data into training and testing sets
                    train_size = int(len(X_scaled) * 0.8)
                    X_train, X_test = X_scaled[:train_size], X_scaled[train_size:]
                    y_train, y_test = y_lagged[:train_size], y_lagged[train_size:]

                    # Create the LSTM model
                    model = Sequential()
                    model.add(LSTM(150, return_sequences=True, input_shape=(1, X_train.shape[2])))
                    model.add(Dropout(0.3))
                    model.add(LSTM(150, return_sequences=False))
                    model.add(Dropout(0.3))
                    model.add(Dense(50))
                    model.add(Dense(1))

                    optimizer = Adam(learning_rate=0.0005)
                    model.compile(optimizer=optimizer, loss='mean_squared_error')

                    # Train the LSTM model
                    model.fit(X_train, y_train, batch_size=4, epochs=200, verbose=1)

                    # Save the trained model to the directory
                    cow_model_dir = os.path.join(model_dir, f'cow_{cow_id}')
                    os.makedirs(cow_model_dir, exist_ok=True)
                    model.save(os.path.join(cow_model_dir, f'model_{cow_id}.h5'))
                    print(f'Model for cow {cow_id} trained and saved.')

    else:
        print("Models are already trained and saved.")
    
    # Reload the specific model based on cow ID
    cow_model_path = os.path.join(model_dir, f'cow_{cow_id}', f'model_{cow_id}.h5')
    if os.path.exists(cow_model_path):
        model = load_model(cow_model_path)
        print(f"Model for cow {cow_id} loaded.")

        # Recompile the model with the optimizer
        optimizer = Adam(learning_rate=0.0005)
        model.compile(optimizer=optimizer, loss='mean_squared_error')

        # Retrain the loaded model
        temp_column = f'{cow_id}_temp'
        activity_column = f'{cow_id}_activity'

        if temp_column not in combined_data.columns or activity_column not in combined_data.columns:
            print(f"No data found for cow ID: {cow_id}")
        else:
            cow_data = combined_data[['Date', temp_column, activity_column]]
            scaler = MinMaxScaler()
            cow_data[[temp_column, activity_column]] = scaler.fit_transform(cow_data[[temp_column, activity_column]])

            # Retrain the model
            X = cow_data[[temp_column, activity_column]]
            y = 0.5 * X[temp_column] + 0.5 * X[activity_column]
            linear_model = LinearRegression()
            linear_model.fit(X, y)
            cow_data['learned_health_score'] = linear_model.predict(X)

            scaler_health = MinMaxScaler()
            cow_data['normalized_learned_health_score'] = scaler_health.fit_transform(cow_data[['learned_health_score']])

            # Preprocess data for LSTM (using normalized learned health score)
            def create_lagged_features(df, target_column, lag=2):
                df_lagged = df.copy()
                for i in range(1, lag + 1):
                    df_lagged[f'{target_column}_lag{i}'] = df[target_column].shift(i, fill_value=df[target_column].iloc[0])
                return df_lagged

            lagged_data = create_lagged_features(cow_data, 'normalized_learned_health_score', lag=2)
            lagged_data = lagged_data.drop(columns=['Date'])

            X_lagged = lagged_data.drop('normalized_learned_health_score', axis=1).values
            y_lagged = lagged_data['normalized_learned_health_score'].values

            scaler_X = MinMaxScaler(feature_range=(0, 1))
            X_scaled = scaler_X.fit_transform(X_lagged)
            X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

            train_size = int(len(X_scaled) * 0.8)
            X_train, X_test = X_scaled[:train_size], X_scaled[train_size:]
            y_train, y_test = y_lagged[:train_size], y_lagged[train_size:]

            # Retrain the LSTM model
            model.fit(X_train, y_train, batch_size=4, epochs=200, verbose=1)

            # Make predictions on both the training and testing datasets
            train_predictions_scaled = model.predict(X_train)
            test_predictions_scaled = model.predict(X_test)

            # Inverse transform the predictions to get them back to the original scale
            train_predictions = scaler_health.inverse_transform(train_predictions_scaled)
            test_predictions = scaler_health.inverse_transform(test_predictions_scaled)
            y_train_actual = scaler_health.inverse_transform(y_train.reshape(-1, 1))
            y_test_actual = scaler_health.inverse_transform(y_test.reshape(-1, 1))

            # Calculate training and testing accuracy using Mean Absolute Percentage Error (MAPE)
            train_accuracy = 100 - np.mean(np.abs((y_train_actual - train_predictions) / y_train_actual)) * 100
            test_accuracy = 100 - np.mean(np.abs((y_test_actual - test_predictions) / y_test_actual)) * 100

            # Print train and test accuracy for verification
            print(f"Train Accuracy: {train_accuracy:.2f}%")
            print(f"Test Accuracy: {test_accuracy:.2f}%")

            # Combine predictions and actual values for continuous plotting
            combined_predictions = np.concatenate((train_predictions, test_predictions), axis=0)
            combined_actual = np.concatenate((y_train_actual, y_test_actual), axis=0)

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
                next_prediction = scaler_health.inverse_transform(next_prediction_scaled)

                # Store the forecasted value
                forecasted_values.append(next_prediction[0][0])

                # Update the last_input with the predicted value for the next iteration
                last_input = np.roll(last_input, -1)
                last_input[0, -1] = next_prediction_scaled[0][0]  # Replace with the predicted value

            # Convert forecasted values to a 2D array for consistent dimensions with predictions
            forecasted_values = np.array(forecasted_values).reshape(-1, 1)

            # Calculate alert percentages
            red_alert_percentage = np.mean(np.array(forecasted_values) < 0.3) * 100
            orange_alert_percentage = np.mean((np.array(forecasted_values) >= 0.3) & (np.array(forecasted_values) < 0.6)) * 100
            green_alert_percentage = np.mean(np.array(forecasted_values) >= 0.6) * 100

            # Determine overall alert
            if red_alert_percentage >= 30:
                overall_alert = "Red Alert"
            elif orange_alert_percentage >= 40:
                overall_alert = "Orange Alert"
            elif green_alert_percentage >= 70:
                overall_alert = "Green Alert"
            else:
                overall_alert = "No Specific Alert"

            # Print alert percentages and overall alert for verification
            print(f"Red Alert: {red_alert_percentage:.2f}%")
            print(f"Orange Alert: {orange_alert_percentage:.2f}%")
            print(f"Green Alert: {green_alert_percentage:.2f}%")
            print(f"Overall Alert: {overall_alert}")

            # Generate the plot using the create_plot function
            fig, ax, line_actual, line_predictions, line_forecast = create_plot(
                cow_id, combined_data, train_accuracy, test_accuracy, 
                combined_actual * 100, combined_predictions * 100, 
                forecasted_values * 100, overall_alert, forecast_days
            )

            # Tooltip function for the plot
            annot = ax.annotate("", xy=(0,0), xytext=(15,15), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="black", ec="white"),
                                arrowprops=dict(arrowstyle="->", color="white"),
                                color="white")
            annot.set_visible(False)

            def get_closest_index(event, x_data, y_data):
                distances = np.sqrt((x_data - event.xdata)**2 + (y_data - event.ydata)**2)
                return np.argmin(distances), np.min(distances)

            def update_annot(ind, line, label, x_data, y_data):
                annot.xy = (x_data[ind], y_data[ind])
                text = f"Day: {int(x_data[ind])}\n{label}: {y_data[ind]:.2f}"
                annot.set_text(text)

                # Adjust the position to keep the tooltip inside the plot
                pos_x = x_data[ind]
                pos_y = y_data[ind]
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()

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

                    if closest_dist < 20:
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


