# # # # # #  Individual LSTM training 


# # # # # # # LSTM_temperature_data.py

# # # # # # import pandas as pd
# # # # # # from sklearn.preprocessing import MinMaxScaler
# # # # # # from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, mean_absolute_error
# # # # # # from tensorflow.keras.models import Sequential
# # # # # # from tensorflow.keras.layers import LSTM, Dense, Input
# # # # # # from tensorflow.keras.callbacks import EarlyStopping
# # # # # # import numpy as np
# # # # # # import matplotlib.pyplot as plt

# # # # # # # Load the dataset
# # # # # # file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'
# # # # # # data = pd.read_csv(file_path)

# # # # # # # Restructure the data
# # # # # # data['Date'] = pd.to_datetime(data['Unnamed: 0'])
# # # # # # data = data.drop(columns=['Unnamed: 0'])  # Drop the old date column
# # # # # # data.set_index('Date', inplace=True)

# # # # # # # Prompt user for Cow ID
# # # # # # cow_id = input("Please enter the Cow ID: ")

# # # # # # # Filter data for the specified Cow ID
# # # # # # if cow_id not in data.columns:
# # # # # #     print(f"Cow ID {cow_id} not found in the dataset. Please check and try again.")
# # # # # # else:
# # # # # #     cow_data = data[[cow_id]].copy()

# # # # # #     # Save the original data for plotting
# # # # # #     original_cow_data = cow_data.copy()

# # # # # #     # Create lagged features and rolling statistics
# # # # # #     for lag in range(1, 7):  # Increase the number of lags
# # # # # #         cow_data[f'lag_{lag}'] = cow_data[cow_id].shift(lag)

# # # # # #     cow_data['rolling_mean'] = cow_data[cow_id].rolling(window=5).mean()  # Increase window for rolling mean
# # # # # #     cow_data['rolling_std'] = cow_data[cow_id].rolling(window=5).std()

# # # # # #     # Fill NaNs strategically to avoid dropping rows at the end of the training data
# # # # # #     cow_data.fillna(method='ffill', inplace=True)
# # # # # #     cow_data.fillna(method='bfill', inplace=True)

# # # # # #     # Prepare data for the vanilla LSTM model
# # # # # #     X = cow_data.drop(columns=[cow_id]).values  # Features (lagged and rolling stats)
# # # # # #     y = cow_data[cow_id].values  # Target variable

# # # # # #     # Reshape X for LSTM: [samples, time steps, features]
# # # # # #     time_steps = X.shape[1]  # Using all features as time steps
# # # # # #     X = X.reshape((X.shape[0], time_steps, 1))

# # # # # #     # Split data into training and testing sets with a slight overlap
# # # # # #     train_size = int(len(X) * 0.8)
# # # # # #     X_train, X_test = X[:train_size], X[train_size:]  # Fix the overlap issue
# # # # # #     y_train, y_test = y[:train_size], y[train_size:]

# # # # # #     def build_vanilla_lstm_model(input_shape):
# # # # # #         model = Sequential()
# # # # # #         model.add(Input(shape=input_shape))
# # # # # #         model.add(LSTM(100, activation='relu', return_sequences=True))
# # # # # #         model.add(LSTM(50, activation='relu'))
# # # # # #         model.add(Dense(1))
# # # # # #         model.compile(optimizer='adam', loss='mse')
# # # # # #         return model

# # # # # #     # Build and train the vanilla LSTM model
# # # # # #     vanilla_lstm_model = build_vanilla_lstm_model((time_steps, 1))
# # # # # #     early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)

# # # # # #     history = vanilla_lstm_model.fit(X_train, y_train, epochs=200, batch_size=8, verbose=1, validation_data=(X_test, y_test), callbacks=[early_stop])

# # # # # #     # Predict on the entire dataset (training + test)5
# # # # # #     y_pred_train = vanilla_lstm_model.predict(X_train)
# # # # # #     y_pred_test = vanilla_lstm_model.predict(X_test)
# # # # # #     y_pred_full = np.concatenate((y_pred_train, y_pred_test), axis=0)

# # # # # #     # Save the predictions to CSV for the combined model
# # # # # #     predictions_df = pd.DataFrame({
# # # # # #         'Date': cow_data.index,
# # # # # #         'temperature_prediction': y_pred_full.flatten()
# # # # # #     })
# # # # # #     predictions_df.to_csv(f'temperature_predictions_{cow_id}.csv', index=False)

# # # # # #     # Evaluate the model using additional metrics
# # # # # #     lstm_mape = mean_absolute_percentage_error(y_test, y_pred_test) * 100
# # # # # #     lstm_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
# # # # # #     lstm_mae = mean_absolute_error(y_test, y_pred_test)

# # # # # #     model_accuracy = 100 - lstm_mape

# # # # # #     print(f'LSTM Model MAPE: {lstm_mape:.2f}%')
# # # # # #     print(f'LSTM Model RMSE: {lstm_rmse:.2f}')
# # # # # #     print(f'LSTM Model MAE: {lstm_mae:.2f}')

# # # # # #     # Print the correct date range for training and testing data
# # # # # #     train_start_date = cow_data.index[0]
# # # # # #     train_end_date = cow_data.index[train_size - 1]
# # # # # #     test_start_date = cow_data.index[train_size]
# # # # # #     test_end_date = cow_data.index[-1]

# # # # # #     train_percentage = (train_size / len(X)) * 100
# # # # # #     test_percentage = ((len(X) - train_size) / len(X)) * 100

# # # # # #     print(f"Training data is from {train_start_date.date()} to {train_end_date.date()}")
# # # # # #     print(f"Test data is from {test_start_date.date()} to {test_end_date.date()}")
# # # # # #     print(f"Training data percentage: {train_percentage:.2f}%")
# # # # # #     print(f"Test data percentage: {test_percentage:.2f}%")

# # # # # #     # Plotting the results
# # # # # #     plt.figure(figsize=(12, 6))

# # # # # #     # Combine the original dropped data with the training data line
# # # # # #     plt.plot(original_cow_data.index, original_cow_data[cow_id], label="Training Data", color='blue')

# # # # # #     # Plot actual test data
# # # # # #     plt.plot(cow_data.index[train_size:], y_test, label="Test Data", color='cyan')

# # # # # #     # Plot predictions for the entire dataset (train + test)
# # # # # #     plt.plot(cow_data.index, y_pred_full.flatten(), label="LSTM Predictions", linestyle='dashed', color='green')

# # # # # #     # Add vertical line for train/test split
# # # # # #     plt.axvline(x=cow_data.index[train_size], color='r', linestyle='--', label='Train/Test Split')

# # # # # #     plt.legend()
# # # # # #     plt.xlabel('Date')
# # # # # #     plt.ylabel('Activity')
# # # # # #     plt.title(f'COW ID: {cow_id} | Model Accuracy: {model_accuracy:.2f}%')
# # # # # #     plt.show()

# # # # # # import pandas as pd
# # # # # # from sklearn.preprocessing import MinMaxScaler
# # # # # # from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, mean_absolute_error
# # # # # # from tensorflow.keras.models import Sequential
# # # # # # from tensorflow.keras.layers import LSTM, Dense, Input
# # # # # # from tensorflow.keras.callbacks import EarlyStopping
# # # # # # import numpy as np
# # # # # # import matplotlib.pyplot as plt

# # # # # # # Load the dataset
# # # # # # file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'
# # # # # # data = pd.read_csv(file_path)

# # # # # # # Restructure the data
# # # # # # data['Date'] = pd.to_datetime(data['Unnamed: 0'])
# # # # # # data = data.drop(columns=['Unnamed: 0'])  # Drop the old date column
# # # # # # data.set_index('Date', inplace=True)

# # # # # # # Prompt user for Cow ID
# # # # # # cow_id = input("Please enter the Cow ID: ")

# # # # # # # Filter data for the specified Cow ID
# # # # # # if cow_id not in data.columns:
# # # # # #     print(f"Cow ID {cow_id} not found in the dataset. Please check and try again.")
# # # # # # else:
# # # # # #     cow_data = data[[cow_id]].copy()

# # # # # #     # Save the original data for plotting
# # # # # #     original_cow_data = cow_data.copy()

# # # # # #     # Create lagged features and rolling statistics
# # # # # #     for lag in range(1, 7):  # Increase the number of lags
# # # # # #         cow_data[f'lag_{lag}'] = cow_data[cow_id].shift(lag)

# # # # # #     cow_data['rolling_mean'] = cow_data[cow_id].rolling(window=5).mean()  # Increase window for rolling mean
# # # # # #     cow_data['rolling_std'] = cow_data[cow_id].rolling(window=5).std()

# # # # # #     # Fill NaNs strategically to avoid dropping rows at the end of the training data
# # # # # #     cow_data.fillna(method='ffill', inplace=True)
# # # # # #     cow_data.fillna(method='bfill', inplace=True)

# # # # # #     # Prepare data for the vanilla LSTM model
# # # # # #     X = cow_data.drop(columns=[cow_id]).values  # Features (lagged and rolling stats)
# # # # # #     y = cow_data[cow_id].values  # Target variable

# # # # # #     # Reshape X for LSTM: [samples, time steps, features]
# # # # # #     time_steps = X.shape[1]  # Using all features as time steps
# # # # # #     X = X.reshape((X.shape[0], time_steps, 1))

# # # # # #     # Split data into training and testing sets with a slight overlap
# # # # # #     train_size = int(len(X) * 0.8)
# # # # # #     X_train, X_test = X[:train_size], X[train_size:]  # Fix the overlap issue
# # # # # #     y_train, y_test = y[:train_size], y[train_size:]

# # # # # #     def build_vanilla_lstm_model(input_shape):
# # # # # #         model = Sequential()
# # # # # #         model.add(Input(shape=input_shape))
# # # # # #         model.add(LSTM(100, activation='relu', return_sequences=True))
# # # # # #         model.add(LSTM(50, activation='relu'))
# # # # # #         model.add(Dense(1))
# # # # # #         model.compile(optimizer='adam', loss='mse')
# # # # # #         return model

# # # # # #     # Build and train the vanilla LSTM model
# # # # # #     vanilla_lstm_model = build_vanilla_lstm_model((time_steps, 1))
# # # # # #     early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)

# # # # # #     history = vanilla_lstm_model.fit(X_train, y_train, epochs=200, batch_size=8, verbose=1, validation_data=(X_test, y_test), callbacks=[early_stop])

# # # # # #     # Predict on the training and test datasets
# # # # # #     y_pred_train = vanilla_lstm_model.predict(X_train)
# # # # # #     y_pred_test = vanilla_lstm_model.predict(X_test)

# # # # # #     # Forecast one month into the future
# # # # # #     forecast_steps = 30  # Assuming daily data, so 30 days into the future
# # # # # #     last_input = X[-1]  # The last input data point for forecasting
# # # # # #     future_predictions = []

# # # # # #     for _ in range(forecast_steps):
# # # # # #         future_pred = vanilla_lstm_model.predict(last_input.reshape(1, time_steps, 1))
# # # # # #         future_predictions.append(future_pred[0][0])
# # # # # #         # Update the input with the new prediction, dropping the oldest input
# # # # # #         last_input = np.roll(last_input, -1)
# # # # # #         last_input[-1] = future_pred

# # # # # #     # Generate future dates for the forecast
# # # # # #     last_date = cow_data.index[-1]
# # # # # #     future_dates = pd.date_range(start=last_date, periods=forecast_steps + 1, freq='D')[1:]

# # # # # #     # Evaluate the model using additional metrics
# # # # # #     lstm_mape = mean_absolute_percentage_error(y_test, y_pred_test) * 100
# # # # # #     lstm_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
# # # # # #     lstm_mae = mean_absolute_error(y_test, y_pred_test)

# # # # # #     model_accuracy = 100 - lstm_mape

# # # # # #     print(f'LSTM Model MAPE: {lstm_mape:.2f}%')
# # # # # #     print(f'LSTM Model RMSE: {lstm_rmse:.2f}')
# # # # # #     print(f'LSTM Model MAE: {lstm_mae:.2f}')

# # # # # #     # Print the correct date range for training and testing data
# # # # # #     train_start_date = cow_data.index[0]
# # # # # #     train_end_date = cow_data.index[train_size - 1]
# # # # # #     test_start_date = cow_data.index[train_size]
# # # # # #     test_end_date = cow_data.index[-1]

# # # # # #     train_percentage = (train_size / len(X)) * 100
# # # # # #     test_percentage = ((len(X) - train_size) / len(X)) * 100

# # # # # #     print(f"Training data is from {train_start_date.date()} to {train_end_date.date()}")
# # # # # #     print(f"Test data is from {test_start_date.date()} to {test_end_date.date()}")
# # # # # #     print(f"Training data percentage: {train_percentage:.2f}%")
# # # # # #     print(f"Test data percentage: {test_percentage:.2f}%")

# # # # # #     # Plotting the results
# # # # # #     plt.figure(figsize=(12, 6))

# # # # # #     # Plot actual data
# # # # # #     plt.plot(original_cow_data.index, original_cow_data[cow_id], label="Actual Data", color='black', linewidth=2)

# # # # # #     # Plot training data (actual vs predictions)
# # # # # #     plt.plot(original_cow_data.index[:train_size], y_train, label="Training Data", color='blue', linewidth=2)
# # # # # #     plt.plot(cow_data.index[:train_size], y_pred_train.flatten(), label="LSTM Training Predictions", linestyle='dashed', color='green', linewidth=2)

# # # # # #     # Plot test data (actual vs predictions)
# # # # # #     plt.plot(original_cow_data.index[train_size:], y_test, label="Test Data", color='cyan', linewidth=2)
# # # # # #     plt.plot(cow_data.index[train_size:], y_pred_test.flatten(), label="LSTM Test Predictions", linestyle='dashed', color='orange', linewidth=2)

# # # # # #     # Plot future forecast data
# # # # # #     plt.plot(future_dates, future_predictions, label="Future Forecast", linestyle='dashed', color='purple', linewidth=2)

# # # # # #     # Add vertical line for train/test split
# # # # # #     plt.axvline(x=cow_data.index[train_size], color='r', linestyle='--', label='Train/Test Split')

# # # # # #     plt.legend()
# # # # # #     plt.xlabel('Date')
# # # # # #     plt.ylabel('Activity')
# # # # # #     plt.title(f'COW ID: {cow_id} | Model Accuracy: {model_accuracy:.2f}%')
# # # # # #     plt.show()


# # # # # # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# # # # # #  Individual LSTM training  set 2 


# # # # # # //////////////////////////////////////////////////////////////TESTING INVERSE SCALE /////////////////////////////////////////////////////////////////////////////


# # # # # # import pandas as pd
# # # # # # from sklearn.preprocessing import MinMaxScaler
# # # # # # import matplotlib.pyplot as plt

# # # # # # # Load the dataset
# # # # # # file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'
# # # # # # data = pd.read_csv(file_path)

# # # # # # # Restructure the data
# # # # # # data['Date'] = pd.to_datetime(data['Unnamed: 0'])
# # # # # # data = data.drop(columns=['Unnamed: 0'])  # Drop the old date column
# # # # # # data.set_index('Date', inplace=True)

# # # # # # # Filter data for Cow 6774
# # # # # # cow_id = '6774'
# # # # # # cow_6774_data = data[[cow_id]].copy()

# # # # # # # Normalize the data
# # # # # # scaler = MinMaxScaler()
# # # # # # scaled_data = scaler.fit_transform(cow_6774_data)

# # # # # # # Inverse transform the scaled data to compare with original
# # # # # # inverse_scaled_data = scaler.inverse_transform(scaled_data)

# # # # # # # Plot original and inverse scaled data
# # # # # # plt.figure(figsize=(12, 6))
# # # # # # plt.plot(cow_6774_data.index, cow_6774_data[cow_id], label="Original Data", color='cyan')
# # # # # # plt.plot(cow_6774_data.index, inverse_scaled_data, label="Inverse Scaled Data", color='orange', linestyle='dashed')
# # # # # # plt.legend()
# # # # # # plt.xlabel('Date')
# # # # # # plt.ylabel('Activity')
# # # # # # plt.title(f'Comparison of Original and Inverse Scaled Data for Cow ID: {cow_id}')
# # # # # # plt.show()



# # # # # # # /////////////////////////////////////////////////////////////////////////// BACK UP CODE //////////////////////////////////////////////////////////////////////////////////



# # # # # # import pandas as pd
# # # # # # from sklearn.preprocessing import MinMaxScaler
# # # # # # from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, mean_absolute_error
# # # # # # from tensorflow.keras.models import Sequential
# # # # # # from tensorflow.keras.layers import LSTM, Dense, Dropout
# # # # # # from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
# # # # # # import numpy as np
# # # # # # import matplotlib.pyplot as plt

# # # # # # # Load the dataset
# # # # # # file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'
# # # # # # data = pd.read_csv(file_path)

# # # # # # # Restructure the data
# # # # # # data['Date'] = pd.to_datetime(data['Unnamed: 0'])
# # # # # # data = data.drop(columns=['Unnamed: 0'])  # Drop the old date column
# # # # # # data.set_index('Date', inplace=True)

# # # # # # # Filter data for Cow 6774
# # # # # # cow_id = '6774'
# # # # # # cow_6774_data = data[[cow_id]].copy()

# # # # # # # Normalize the data
# # # # # # scaler = MinMaxScaler()
# # # # # # scaled_data = scaler.fit_transform(cow_6774_data)

# # # # # # # Prepare data for the LSTM model
# # # # # # X = scaled_data  # Features
# # # # # # y = scaled_data[:, 0]  # Target variable

# # # # # # # Reshape X for LSTM: [samples, time steps, features]
# # # # # # X = X.reshape((X.shape[0], 1, 1))

# # # # # # # Split data into training and testing sets
# # # # # # train_size = int(len(X) * 0.8)
# # # # # # X_train, X_test = X[:train_size], X[train_size:]
# # # # # # y_train, y_test = y[:train_size], y[train_size:]

# # # # # # # Print the date range for training and testing data
# # # # # # train_start_date = cow_6774_data.index[0]
# # # # # # train_end_date = cow_6774_data.index[train_size - 1]
# # # # # # test_start_date = cow_6774_data.index[train_size]
# # # # # # test_end_date = cow_6774_data.index[-1]

# # # # # # print(f"Training data is from {train_start_date.date()} to {train_end_date.date()}")
# # # # # # print(f"Test data is from {test_start_date.date()} to {test_end_date.date()}")

# # # # # # # Define the Vanilla LSTM model
# # # # # # def build_vanilla_lstm_model(input_shape):
# # # # # #     model = Sequential()
# # # # # #     model.add(LSTM(100, activation='relu', input_shape=input_shape))
# # # # # #     model.add(Dropout(0.3))  # Increased Dropout for regularization
# # # # # #     model.add(Dense(1))
# # # # # #     model.compile(optimizer='adam', loss='mse')
# # # # # #     return model

# # # # # # # Build and train the Vanilla LSTM model
# # # # # # vanilla_lstm_model = build_vanilla_lstm_model((1, 1))
# # # # # # early_stop = EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)
# # # # # # reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6)

# # # # # # history = vanilla_lstm_model.fit(X_train, y_train, epochs=400, batch_size=16, verbose=1, validation_data=(X_test, y_test), callbacks=[early_stop, reduce_lr])

# # # # # # # Predict on the entire dataset (training + test)
# # # # # # y_pred_scaled_all = vanilla_lstm_model.predict(X)

# # # # # # # Inverse transform the predictions and the true data
# # # # # # y_pred_all = scaler.inverse_transform(np.concatenate([y_pred_scaled_all, np.zeros((len(y_pred_scaled_all), 1))], axis=1))[:, 0]
# # # # # # y_all_inv = scaler.inverse_transform(np.concatenate([y.reshape(-1, 1), np.zeros((len(y), 1))], axis=1))[:, 0]

# # # # # # # Evaluate the model using additional metrics
# # # # # # lstm_rmse = np.sqrt(mean_squared_error(y_all_inv[train_size:], y_pred_all[train_size:]))
# # # # # # lstm_mae = mean_absolute_error(y_all_inv[train_size:], y_pred_all[train_size:])
# # # # # # lstm_mape = mean_absolute_percentage_error(y_all_inv[train_size:], y_pred_all[train_size:]) * 100

# # # # # # print(f'LSTM Model RMSE: {lstm_rmse:.2f}')
# # # # # # print(f'LSTM Model MAE: {lstm_mae:.2f}')
# # # # # # print(f'LSTM Model MAPE: {lstm_mape:.2f}%')

# # # # # # # Plotting the results
# # # # # # plt.figure(figsize=(12, 6))

# # # # # # # Plot training data
# # # # # # plt.plot(cow_6774_data.index[:train_size], y_all_inv[:train_size], label="Training Data", color='orange')
# # # # # # # Plot actual test data
# # # # # # plt.plot(cow_6774_data.index[train_size:], y_all_inv[train_size:], label="Test Data", color='blue')
# # # # # # # Plot predictions for the entire dataset
# # # # # # plt.plot(cow_6774_data.index, y_pred_all, label="LSTM Predictions", linestyle='dashed', color='green')

# # # # # # # Add vertical line for train/test split
# # # # # # plt.axvline(x=cow_6774_data.index[train_size], color='r', linestyle='--', label='Train/Test Split')

# # # # # # plt.legend()
# # # # # # plt.xlabel('Date')
# # # # # # plt.ylabel('Activity')
# # # # # # plt.title(f'COW ID: {cow_id} | Model Accuracy: {100 - lstm_mape:.2f}% (MAPE), RMSE: {lstm_rmse:.2f}, MAE: {lstm_mae:.2f}')
# # # # # # plt.show()

# # # # # # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////




# # # # # import pandas as pd
# # # # # import numpy as np
# # # # # import os
# # # # # import tensorflow as tf
# # # # # from sklearn.preprocessing import MinMaxScaler
# # # # # from sklearn.model_selection import TimeSeriesSplit
# # # # # from tensorflow.keras.models import Sequential
# # # # # from tensorflow.keras.layers import LSTM, Dense, Dropout
# # # # # from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
# # # # # import matplotlib.pyplot as plt

# # # # # # Set a random seed for reproducibility
# # # # # RANDOM_SEED = 42
# # # # # np.random.seed(RANDOM_SEED)
# # # # # tf.random.set_seed(RANDOM_SEED)

# # # # # # Section 1: Data Preprocessing
# # # # # def load_data(file_path):
# # # # #     try:
# # # # #         data = pd.read_csv(file_path, encoding='utf-8')
# # # # #     except UnicodeDecodeError:
# # # # #         data = pd.read_csv(file_path, encoding='ISO-8859-1')
# # # # #     print(f"\nStep 1: Data Collection and Integration - Loaded data from {file_path}.\n")
# # # # #     return data

# # # # # def handle_missing_values(df):
# # # # #     actions_taken = []
# # # # #     if df.isnull().sum().sum() == 0:
# # # # #         actions_taken.append("No missing values found. No need for spline interpolation.")
# # # # #     else:
# # # # #         missing_percentage = df.isnull().mean() * 100
# # # # #         if missing_percentage.max() > 30:
# # # # #             actions_taken.append("Columns with more than 30% missing values found. Consider removing these columns.")
# # # # #         for col in df.columns:
# # # # #             if df[col].isnull().sum() > 0:
# # # # #                 if df[col].dtype in ['float64', 'int64']:
# # # # #                     df[col].fillna(df[col].interpolate(method='spline', order=3), inplace=True)
# # # # #                     actions_taken.append(f"Interpolated missing values in column '{col}'.")
# # # # #     return df, actions_taken

# # # # # def remove_duplicates(df):
# # # # #     initial_row_count = df.shape[0]
# # # # #     df.drop_duplicates(inplace=True)
# # # # #     final_row_count = df.shape[0]
# # # # #     return df, initial_row_count - final_row_count

# # # # # def identify_and_handle_outliers(df):
# # # # #     actions_taken = []
# # # # #     numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
# # # # #     z_scores = (df[numeric_cols] - df[numeric_cols].mean()) / df[numeric_cols].std()
# # # # #     outliers = (z_scores.abs() > 3)
# # # # #     for col in numeric_cols:
# # # # #         num_outliers = outliers[col].sum()
# # # # #         if num_outliers > 0:
# # # # #             median_value = df[col].median()
# # # # #             df.loc[outliers[col], col] = median_value.astype(df[col].dtype)
# # # # #             actions_taken.append(f"Capped {num_outliers} outliers in column '{col}' to median value.")
# # # # #     return df, actions_taken

# # # # # def apply_normalization(df):
# # # # #     numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
# # # # #     scaler = MinMaxScaler()
# # # # #     df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
# # # # #     scaling_action = "Applied MinMaxScaler for normalization."
# # # # #     return df, scaling_action

# # # # # # Function to process activity data
# # # # # def preprocess_activity_data(file_path, output_folder):
# # # # #     # Step 1: Load Data
# # # # #     data = load_data(file_path)

# # # # #     print("\n")

# # # # #     # Ensure the first cell of the first column is labeled 'date'
# # # # #     if data.columns[0] == '' or pd.isna(data.columns[0]):
# # # # #         data.columns = ['date'] + data.columns[1:].tolist()
# # # # #     else:
# # # # #         data.columns = ['date'] + data.columns[1:].tolist() if data.columns[0] != 'date' else data.columns

# # # # #     # Ensure column names are stripped of leading/trailing spaces
# # # # #     data.columns = data.columns.str.strip()

# # # # #     # Step 2: Data Cleaning
# # # # #     # Handle missing values
# # # # #     data, missing_actions = handle_missing_values(data)
# # # # #     print("Step 2: Data Cleaning - Missing Values")
# # # # #     for action in missing_actions:
# # # # #         print(action)

# # # # #     print("\n")

# # # # #     # Remove duplicates
# # # # #     data, num_duplicates_removed = remove_duplicates(data)
# # # # #     print(f"Removed {num_duplicates_removed} duplicate rows.")

# # # # #     print("\n")

# # # # #     # Identify and handle outliers
# # # # #     data, outlier_actions = identify_and_handle_outliers(data)
# # # # #     print("Step 2: Data Cleaning - Outliers")
# # # # #     for action in outlier_actions:
# # # # #         print(action)

# # # # #     print("\n\n")

# # # # #     # Step 3: Data Transformation
# # # # #     data_transformed, scaling_action = apply_normalization(data)
# # # # #     print("Step 3: Data Transformation")
# # # # #     print(scaling_action)

# # # # #     print("\n\n")

# # # # #     # Display final DataFrame
# # # # #     print("Final DataFrame preview:")
# # # # #     columns_to_display = list(data_transformed.columns[:6]) + ["..."] + list(data_transformed.columns[-6:])
# # # # #     df_preview = data_transformed[data_transformed.columns[:6]].copy()
# # # # #     df_preview["..."] = "..."
# # # # #     for col in data_transformed.columns[-6:]:
# # # # #         df_preview[col] = data_transformed[col]
# # # # #     print(df_preview.head().to_string(index=False))

# # # # #     print("\n\n")

# # # # #     # Save the cleaned and transformed data
# # # # #     if not os.path.exists(output_folder):
# # # # #         os.makedirs(output_folder)
# # # # #         print(f"Created folder: {output_folder}")
    
# # # # #     output_filename = 'preprocessed_activity_data.csv'
# # # # #     output_path = os.path.join(output_folder, output_filename)
# # # # #     if os.path.exists(output_path):
# # # # #         os.remove(output_path)
# # # # #         print(f"Deleted existing file: {output_path}")
# # # # #     data_transformed.to_csv(output_path, index=False)
# # # # #     print(f"Processed file saved at: {output_path}")

# # # # #     print("\n\n" + "-"*50 + "\n\n")
# # # # #     return output_path

# # # # # # Section 2: Time Series Formatting
# # # # # def determine_dynamic_sequence_length(data, min_proportion=0.1, max_proportion=0.5, min_length=5, max_length=30):
# # # # #     data_length = len(data)
# # # # #     sequence_length = int(np.sqrt(data_length))
# # # # #     dynamic_min_length = max(min_length, int(data_length * min_proportion))
# # # # #     dynamic_max_length = min(max_length, int(data_length * max_proportion))
# # # # #     sequence_length = max(dynamic_min_length, min(sequence_length, dynamic_max_length))
# # # # #     return sequence_length

# # # # # def create_activity_sequences(activity_data, sequence_length, dates):
# # # # #     X_activity = []
# # # # #     y_activity = []
# # # # #     sequence_dates = []
    
# # # # #     for i in range(len(activity_data) - sequence_length):
# # # # #         seq = activity_data.iloc[i:i + sequence_length, :].values
# # # # #         target = activity_data.iloc[i + sequence_length, :].values
# # # # #         dates_seq = dates[i:i + sequence_length]
# # # # #         X_activity.append(seq)
# # # # #         y_activity.append(target)
# # # # #         sequence_dates.append(dates_seq)
        
# # # # #     return np.array(X_activity), np.array(y_activity), sequence_dates

# # # # # # Section 3: Train-Test Split and Cross-Validation
# # # # # def time_series_cross_validation(X_activity, y_activity, n_splits):
# # # # #     tscv = TimeSeriesSplit(n_splits=n_splits)
# # # # #     fold_results = []
# # # # #     best_val_loss = float('inf')
# # # # #     best_fold = None
# # # # #     best_model_path = None

# # # # #     for fold, (train_index, test_index) in enumerate(tscv.split(X_activity), 1):
# # # # #         X_train, X_test = X_activity[train_index], X_activity[test_index]
# # # # #         y_train, y_test = y_activity[train_index], y_activity[test_index]
        
# # # # #         fold_result = {
# # # # #             'fold': fold,
# # # # #             'train_indices': train_index,
# # # # #             'test_indices': test_index,
# # # # #             'train_size': len(train_index),
# # # # #             'test_size': len(test_index),
# # # # #             'X_train_shape': X_train.shape,
# # # # #             'X_test_shape': X_test.shape,
# # # # #             'y_train_shape': y_train.shape,
# # # # #             'y_test_shape': y_test.shape
# # # # #         }
        
# # # # #         fold_results.append(fold_result)
        
# # # # #         print(f"\nFold {fold}:")
# # # # #         print(f"  Train indices: {train_index}")
# # # # #         print(f"  Test indices: {test_index}")
# # # # #         print(f"  Train size: {len(train_index)}, Test size: {len(test_index)}")
# # # # #         print(f"  X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
# # # # #         print(f"  X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")

# # # # #         # Model training
# # # # #         model = build_model(X_train.shape[1:])
# # # # #         early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
# # # # #         model_checkpoint = ModelCheckpoint(f'fold_{fold}_model.keras', monitor='val_loss', save_best_only=True)
        
# # # # #         history = model.fit(X_train, y_train, 
# # # # #                             validation_data=(X_test, y_test), 
# # # # #                             epochs=250, 
# # # # #                             batch_size=16, 
# # # # #                             callbacks=[early_stopping, model_checkpoint])
        
# # # # #         val_loss = min(history.history['val_loss'])
# # # # #         print(f"Best val_loss for Fold {fold}: {val_loss}")

# # # # #         if val_loss < best_val_loss:
# # # # #             best_val_loss = val_loss
# # # # #             best_fold = fold
# # # # #             best_model_path = f'fold_{fold}_model.keras'

# # # # #     print(f"\nBest model was from Fold {best_fold} with validation loss: {best_val_loss}")
# # # # #     print(f"Best model across all folds saved at: {best_model_path}")
    
# # # # #     return fold_results, best_fold, best_val_loss, best_model_path

# # # # # # Section 4: Build and Train Model
# # # # # def build_model(input_shape):
# # # # #     model = Sequential()
# # # # #     model.add(LSTM(units=64, return_sequences=False, input_shape=input_shape))
# # # # #     model.add(Dropout(0.2))
# # # # #     model.add(Dense(input_shape[-1]))  # Assuming y_train has the same number of features as X_train

# # # # #     model.compile(optimizer='adam', loss='mean_squared_error')
# # # # #     return model

# # # # # # Section 5: Forecasting and Visualization
# # # # # def categorize_alert(predicted_activity, group_mean_activity):
# # # # #     # Assuming both predicted_activity and group_mean_activity are arrays of the same shape
# # # # #     predicted_activity_value = predicted_activity[0] if isinstance(predicted_activity, np.ndarray) else predicted_activity
# # # # #     group_mean_activity_value = group_mean_activity[0] if isinstance(group_mean_activity, np.ndarray) else group_mean_activity
    
# # # # #     if predicted_activity_value < 0.7 * group_mean_activity_value:
# # # # #         return "Red Alert"
# # # # #     elif predicted_activity_value < 0.9 * group_mean_activity_value:
# # # # #         return "Orange Alert"
# # # # #     else:
# # # # #         return "Green Alert"


# # # # # def plot_activity(cow_data, group_mean, predicted_activity, alert_level, sequence_dates):
# # # # #     plt.plot(sequence_dates, cow_data, 'b-', label='Cow Activity')
# # # # #     plt.plot(sequence_dates, group_mean, 'r-', label='Group Mean Activity')
# # # # #     plt.axhline(y=predicted_activity, color='g' if alert_level == "Green Alert" else 'orange' if alert_level == "Orange Alert" else 'r', linestyle='--', label='Predicted Activity')
# # # # #     plt.title(f"Cow Activity Forecast - {alert_level}")
# # # # #     plt.legend()
# # # # #     plt.show()

# # # # # def forecast_and_visualize(model_path, X_activity, y_activity, sequence_dates):
# # # # #     model = tf.keras.models.load_model(model_path)
# # # # #     recent_sequence = X_activity[-1].reshape(1, X_activity.shape[1], X_activity.shape[2])
# # # # #     predicted_activity = model.predict(recent_sequence)[0]
    
# # # # #     # Assuming the group mean activity is the last feature in the sequence
# # # # #     group_mean_activity = np.mean(recent_sequence[0][:, -1])
    
# # # # #     alert_level = categorize_alert(predicted_activity, group_mean_activity)
# # # # #     print(f"Predicted Activity: {predicted_activity}, Alert Level: {alert_level}")
    
# # # # #     plot_activity(
# # # # #         cow_data=recent_sequence[0][:, 0],  # Assuming first column is cow activity
# # # # #         group_mean=recent_sequence[0][:, -1],  # Assuming last column is group mean activity
# # # # #         predicted_activity=predicted_activity[0],
# # # # #         alert_level=alert_level,
# # # # #         sequence_dates=sequence_dates[-1]  # Dates corresponding to the last sequence
# # # # #     )

# # # # # # Main processing function
# # # # # def process_activity_data(file_path):
# # # # #     # Set up folder paths
# # # # #     desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
# # # # #     output_folder = os.path.join(desktop_path, "Activity data preparation")
# # # # #     final_results_folder = os.path.join(output_folder, "final results")

# # # # #     # Section 1: Data Preprocessing
# # # # #     preprocessed_data_path = preprocess_activity_data(file_path, output_folder)

# # # # #     # Load preprocessed data for further processing
# # # # #     activity_data = pd.read_csv(preprocessed_data_path)
    
# # # # #     # Section 2: Time Series Formatting
# # # # #     print("\nSection 2: Time Series Formatting")
# # # # #     dates = activity_data['date'].tolist()
# # # # #     activity_data = activity_data.drop(columns=['date'])

# # # # #     sequence_length = determine_dynamic_sequence_length(activity_data)
# # # # #     print(f"Determined sequence length for activity data: {sequence_length}")

# # # # #     X_activity, y_activity, sequence_dates = create_activity_sequences(activity_data, sequence_length, dates)

# # # # #     print(f"\nActivity data sequences: {X_activity.shape}, Targets: {y_activity.shape}")

# # # # #     # Section 3: Train-Test Split and Cross-Validation
# # # # #     print("\nSection 3: Train-Test Split and Cross-Validation")
# # # # #     sequence_length = X_activity.shape[1]
# # # # #     total_sequences = len(X_activity)
# # # # #     n_splits = max(2, total_sequences // sequence_length)
# # # # #     print(f"\nDynamically determined number of splits: {n_splits}")

# # # # #     cross_val_results, best_fold, best_val_loss, best_model_path = time_series_cross_validation(X_activity, y_activity, n_splits)

# # # # #     # Save all results
# # # # #     os.makedirs(final_results_folder, exist_ok=True)

# # # # #     # Save preprocessed and sequence data
# # # # #     np.save(os.path.join(output_folder, 'X_activity.npy'), X_activity)
# # # # #     np.save(os.path.join(output_folder, 'y_activity.npy'), y_activity)
# # # # #     pd.DataFrame(sequence_dates).to_csv(os.path.join(output_folder, 'sequence_dates_activity.csv'), index=False, header=False)

# # # # #     # Save cross-validation results in the final results folder
# # # # #     cross_val_df = pd.DataFrame(cross_val_results)
# # # # #     cross_val_df.to_csv(os.path.join(final_results_folder, 'cross_val_results_activity.csv'), index=False)

# # # # #     print(f"\nAll results have been saved successfully in {output_folder}.")
    
# # # # #     return best_fold, best_val_loss, best_model_path, X_activity, y_activity, sequence_dates

# # # # # # Example usage
# # # # # activity_file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'
# # # # # best_fold, best_val_loss, best_model_path, X_activity, y_activity, sequence_dates = process_activity_data(activity_file_path)

# # # # # # Forecast and visualize
# # # # # def forecast_and_visualize(model_path, X_activity, y_activity, sequence_dates):
# # # # #     model = tf.keras.models.load_model(model_path)
# # # # #     recent_sequence = X_activity[-1].reshape(1, X_activity.shape[1], X_activity.shape[2])
# # # # #     predicted_activity = model.predict(recent_sequence)[0]  # `predicted_activity` should be an array
    
# # # # #     # Assuming the group mean activity is the last feature in the sequence
# # # # #     group_mean_activity = np.mean(recent_sequence[0][:, -1])
    
# # # # #     # If predicted_activity is an array, compare its first element to group_mean_activity
# # # # #     alert_level = categorize_alert(predicted_activity, group_mean_activity)
# # # # #     print(f"Predicted Activity: {predicted_activity}, Alert Level: {alert_level}")
    
# # # # #     plot_activity(
# # # # #         cow_data=recent_sequence[0][:, 0],  # Assuming first column is cow activity
# # # # #         group_mean=recent_sequence[0][:, -1],  # Assuming last column is group mean activity
# # # # #         predicted_activity=predicted_activity[0],  # Take the first element of predicted_activity
# # # # #         alert_level=alert_level,
# # # # #         sequence_dates=sequence_dates[-1]  # Dates corresponding to the last sequence
# # # # #     )



# # # # # # import pandas as pd
# # # # # # from sklearn.preprocessing import MinMaxScaler
# # # # # # from sklearn.model_selection import train_test_split
# # # # # # from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, mean_absolute_error
# # # # # # from tensorflow.keras.models import Sequential
# # # # # # from tensorflow.keras.layers import LSTM, Dense, Input
# # # # # # from tensorflow.keras.callbacks import EarlyStopping
# # # # # # import numpy as np
# # # # # # import matplotlib.pyplot as plt

# # # # # # # Load the dataset
# # # # # # file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'
# # # # # # data = pd.read_csv(file_path)

# # # # # # # Restructure the data
# # # # # # data['Date'] = pd.to_datetime(data['Unnamed: 0'])
# # # # # # data = data.drop(columns=['Unnamed: 0'])  # Drop the old date column
# # # # # # data.set_index('Date', inplace=True)

# # # # # # # Filter data for Cow 6774
# # # # # # cow_6774_data = data[['6774']].copy()

# # # # # # # Create lagged features and rolling statistics
# # # # # # for lag in range(1, 7):  # Increase the number of lags
# # # # # #     cow_6774_data[f'lag_{lag}'] = cow_6774_data['6774'].shift(lag)

# # # # # # cow_6774_data['rolling_mean'] = cow_6774_data['6774'].rolling(window=5).mean()  # Increase window for rolling mean
# # # # # # cow_6774_data['rolling_std'] = cow_6774_data['6774'].rolling(window=5).std()

# # # # # # # Drop any rows with NaN values that were introduced by lagging/rolling
# # # # # # cow_6774_data = cow_6774_data.dropna()

# # # # # # # Prepare data for the vanilla LSTM model
# # # # # # X = cow_6774_data.drop(columns=['6774']).values  # Features (lagged and rolling stats)
# # # # # # y = cow_6774_data['6774'].values  # Target variable

# # # # # # # Reshape X for LSTM: [samples, time steps, features]
# # # # # # time_steps = X.shape[1]  # Using all features as time steps
# # # # # # X = X.reshape((X.shape[0], time_steps, 1))

# # # # # # # Split data into training and testing sets with a slight overlap
# # # # # # train_size = int(len(X) * 0.8)
# # # # # # X_train, X_test = X[:train_size], X[train_size:]  # Fix the overlap issue
# # # # # # y_train, y_test = y[:train_size], y[train_size:]

# # # # # # # Define the vanilla LSTM model with potential hyperparameter tuning
# # # # # # def build_vanilla_lstm_model(input_shape):
# # # # # #     model = Sequential()
# # # # # #     model.add(Input(shape=input_shape))
# # # # # #     model.add(LSTM(100, activation='relu'))  # Increase number of units
# # # # # #     model.add(Dense(1))
# # # # # #     model.compile(optimizer='adam', loss='mse')  # Lower learning rate
# # # # # #     return model

# # # # # # # Build and train the vanilla LSTM model
# # # # # # vanilla_lstm_model = build_vanilla_lstm_model((time_steps, 1))
# # # # # # early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)

# # # # # # history = vanilla_lstm_model.fit(X_train, y_train, epochs=200, batch_size=8, verbose=1, validation_data=(X_test, y_test), callbacks=[early_stop])

# # # # # # # Predict on the test set
# # # # # # y_pred = vanilla_lstm_model.predict(X_test)

# # # # # # # Evaluate the model using additional metrics
# # # # # # lstm_mape = mean_absolute_percentage_error(y_test, y_pred) * 100
# # # # # # lstm_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
# # # # # # lstm_mae = mean_absolute_error(y_test, y_pred)

# # # # # # print(f'LSTM Model MAPE: {lstm_mape:.2f}%')
# # # # # # print(f'LSTM Model RMSE: {lstm_rmse:.2f}')
# # # # # # print(f'LSTM Model MAE: {lstm_mae:.2f}')

# # # # # # # Plotting the results
# # # # # # plt.figure(figsize=(12, 6))

# # # # # # # Plot training data
# # # # # # plt.plot(cow_6774_data.index[:train_size], y_train, label="Training Data")
# # # # # # # Plot actual test data
# # # # # # plt.plot(cow_6774_data.index[train_size:], y_test, label="Test Data")
# # # # # # # Plot predictions for the test dates
# # # # # # plt.plot(cow_6774_data.index[train_size:], y_pred.flatten(), label="LSTM Predictions", linestyle='dashed')

# # # # # # # Add vertical line for train/test split
# # # # # # plt.axvline(x=cow_6774_data.index[train_size], color='r', linestyle='--', label='Train/Test Split')

# # # # # # plt.legend()
# # # # # # plt.xlabel('Date')
# # # # # # plt.ylabel('Activity')
# # # # # # plt.title(f'LSTM Model MAPE: {100 - lstm_mape:.2f}%, RMSE: {lstm_rmse:.2f}, MAE: {lstm_mae:.2f}')
# # # # # # plt.show()





# # # # # # # # # ////////////////////////////////BEST PERFORMANCE//////////////////////////////////////////////////


# # # # import os
# # # # import pandas as pd
# # # # import numpy as np
# # # # from sklearn.preprocessing import MinMaxScaler
# # # # from keras.models import Sequential
# # # # from keras.layers import LSTM, Dense, Dropout
# # # # from keras.optimizers import Adam
# # # # import joblib
# # # # import matplotlib.pyplot as plt
# # # # from matplotlib.offsetbox import AnnotationBbox, TextArea

# # # # # Create the directory for saving the model and scalers if it doesn't exist
# # # # model_dir = 'Cow_6774_Model'
# # # # if not os.path.exists(model_dir):
# # # #     os.makedirs(model_dir)

# # # # # ====== Data Preprocessing Phase with Lag Features and Rolling Windows ======

# # # # # Load the dataset
# # # # file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'  # Update this path if necessary
# # # # data = pd.read_csv(file_path)

# # # # # Drop non-numeric columns if present
# # # # if 'Unnamed: 0' in data.columns:
# # # #     data = data.drop('Unnamed: 0', axis=1)
# # # # if 'Date' in data.columns:
# # # #     data = data.drop('Date', axis=1)

# # # # # Ensure all data is numeric and drop rows with missing values
# # # # data_cleaned = data.apply(pd.to_numeric, errors='coerce').fillna(method='ffill')  # Forward fill missing values

# # # # # Create lag features for the '6774' column and others without dropping initial rows
# # # # def create_lagged_features(df, lag=2):
# # # #     df_lagged = df.copy()
# # # #     for col in df.columns:
# # # #         for i in range(1, lag + 1):
# # # #             df_lagged[f'{col}_lag{i}'] = df[col].shift(i, fill_value=df[col].iloc[0])  # Shift with padding
# # # #     return df_lagged

# # # # # Apply lag features and fill NaNs with the first available value
# # # # lag = 2  # Reduced lag to avoid dropping too many initial data points
# # # # data_lagged = create_lagged_features(data_cleaned, lag=lag)

# # # # # Apply rolling window on the '6774' column (e.g., 3-day rolling mean) with minimal data loss
# # # # data_lagged['6774_rolling'] = data_lagged['6774'].rolling(window=3, min_periods=1).mean()

# # # # # Define features and target
# # # # X = data_lagged.drop('6774', axis=1).values
# # # # y = data_lagged['6774'].values

# # # # # Feature scaling using MinMaxScaler
# # # # scaler_X = MinMaxScaler(feature_range=(0, 1))
# # # # scaler_y = MinMaxScaler(feature_range=(0, 1))

# # # # X_scaled = scaler_X.fit_transform(X)
# # # # y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

# # # # # Reshape input to be 3D for LSTM [samples, time steps, features]
# # # # X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

# # # # # Split data into training and testing sets (80% train, 20% test)
# # # # train_size = int(len(X_scaled) * 0.8)
# # # # X_train, X_test = X_scaled[:train_size], X_scaled[train_size:]
# # # # y_train, y_test = y_scaled[:train_size], y_scaled[train_size:]

# # # # # ====== Model Training Phase ======

# # # # # Build the LSTM model with dropout and LSTM layers
# # # # model = Sequential()
# # # # model.add(LSTM(150, return_sequences=True, input_shape=(1, X_train.shape[2])))
# # # # model.add(Dropout(0.3))
# # # # model.add(LSTM(150, return_sequences=False))
# # # # model.add(Dropout(0.3))
# # # # model.add(Dense(50))
# # # # model.add(Dense(1))

# # # # # Compile the model with Adam optimizer and a lower learning rate
# # # # optimizer = Adam(learning_rate=0.0005)
# # # # model.compile(optimizer=optimizer, loss='mean_squared_error')

# # # # # Train the model with more epochs and smaller batch size
# # # # model.fit(X_train, y_train, batch_size=4, epochs=200, verbose=1)

# # # # # Save the trained model
# # # # model.save(os.path.join(model_dir, 'lstm_model_6774_lagged.keras'))

# # # # # Save the scalers for future use
# # # # joblib.dump(scaler_X, os.path.join(model_dir, 'scaler_X_6774_lagged.pkl'))
# # # # joblib.dump(scaler_y, os.path.join(model_dir, 'scaler_y_6774_lagged.pkl'))

# # # # # ====== Prediction Phase ======

# # # # # Make predictions on both the training and testing datasets
# # # # train_predictions_scaled = model.predict(X_train)
# # # # test_predictions_scaled = model.predict(X_test)

# # # # # Inverse transform the predictions to get them back to the original scale
# # # # train_predictions = scaler_y.inverse_transform(train_predictions_scaled)
# # # # test_predictions = scaler_y.inverse_transform(test_predictions_scaled)
# # # # y_train_actual = scaler_y.inverse_transform(y_train)
# # # # y_test_actual = scaler_y.inverse_transform(y_test)

# # # # # Combine predictions and actual values for continuous plotting
# # # # combined_predictions = np.concatenate((train_predictions, test_predictions), axis=0)
# # # # combined_actual = np.concatenate((y_train_actual, y_test_actual), axis=0)

# # # # # Calculate accuracy using Mean Absolute Percentage Error (MAPE)
# # # # train_accuracy = 100 - np.mean(np.abs((y_train_actual - train_predictions) / y_train_actual)) * 100
# # # # test_accuracy = 100 - np.mean(np.abs((y_test_actual - test_predictions) / y_test_actual)) * 100

# # # # # ====== Forecasting Phase ======

# # # # # Number of days to forecast
# # # # forecast_days = 15

# # # # # Get the last data point from the test set as the starting point for forecasting
# # # # last_input = X_test[-1]

# # # # # Create a list to store the forecasted values
# # # # forecasted_values = []

# # # # # Forecast for the next 15 days
# # # # for day in range(forecast_days):
# # # #     # Predict the next day's value
# # # #     next_prediction_scaled = model.predict(last_input.reshape(1, 1, -1))
    
# # # #     # Inverse transform the prediction back to the original scale
# # # #     next_prediction = scaler_y.inverse_transform(next_prediction_scaled)
    
# # # #     # Store the forecasted value
# # # #     forecasted_values.append(next_prediction[0][0])
    
# # # #     # Update the last_input with the predicted value for the next iteration
# # # #     last_input = np.roll(last_input, -1)
# # # #     last_input[0, -1] = next_prediction_scaled[0][0]  # Replace with the predicted value

# # # # # Convert forecasted values to a 2D array for consistent dimensions with predictions
# # # # forecasted_values = np.array(forecasted_values).reshape(-1, 1)

# # # # # ====== Plotting Phase with Tooltips ======

# # # # # Set dark mode style for the plot
# # # # plt.style.use('dark_background')

# # # # # Create the figure and axis
# # # # fig, ax = plt.subplots(figsize=(14, 5))

# # # # # Customize the axis colors for dark mode
# # # # ax.set_facecolor('black')
# # # # ax.xaxis.label.set_color('white')
# # # # ax.yaxis.label.set_color('white')
# # # # ax.tick_params(axis='x', colors='white')
# # # # ax.tick_params(axis='y', colors='white')

# # # # # Use integer x-axis values instead of dates
# # # # x_train = np.arange(len(y_train_actual))
# # # # x_test = np.arange(len(y_train_actual), len(y_train_actual) + len(y_test_actual))
# # # # x_forecast = np.arange(len(combined_actual), len(combined_actual) + forecast_days)

# # # # # Plot the actual data with glowing dark cyan color and thin lines
# # # # line_actual, = ax.plot(np.concatenate((x_train, x_test)), combined_actual, color='#00FFFF', marker='o', label='Actual Data (Train + Test)', markersize=3, linewidth=0.8)

# # # # # Plot the LSTM predictions as a dotted line
# # # # line_predictions, = ax.plot(np.concatenate((x_train, x_test)), combined_predictions, color='#FF4500', linestyle='--', linewidth=1, label='LSTM Predictions')

# # # # # Plot the forecasted values as a bright red thin line with data points
# # # # line_forecast, = ax.plot(x_forecast, forecasted_values, color='red', linestyle='-', marker='o', markersize=3, linewidth=1, label='15-Day Forecast')

# # # # # Add a thin black solid line for the train/test split
# # # # ax.axvline(x=len(x_train), color='white', linestyle='-', linewidth=1)
# # # # ax.text(len(x_train), ax.get_ylim()[1] * 0.98, 'Train/Test Split', rotation=90, verticalalignment='top',
# # # #         horizontalalignment='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.4'), color='black', fontsize=8)

# # # # # Add a thin black solid line for the start of the forecast
# # # # ax.axvline(x=len(x_train) + len(x_test), color='white', linestyle='-', linewidth=1)
# # # # ax.text(len(x_train) + len(x_test), ax.get_ylim()[1] * 0.98, 'Forecast Start', rotation=90, verticalalignment='top',
# # # #         horizontalalignment='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.4'), color='black', fontsize=8)

# # # # # Add title and labels
# # # # ax.set_title(f"Cow 6774 Activity Model | Train Data Prediction Accuracy: {train_accuracy:.2f}% | Test Data Prediction Accuracy: {test_accuracy:.2f}% | 15-Day Forecast", color='white')
# # # # ax.set_xlabel('Time (Days)', color='white')
# # # # ax.set_ylabel('Activity Level', color='white')

# # # # # Format x-axis as integers
# # # # ax.set_xticks(np.arange(0, len(combined_actual) + forecast_days, 10))

# # # # # Legend with white text
# # # # ax.legend(facecolor='black', edgecolor='white', fontsize=10, labelcolor='white')

# # # # # Initialize tooltip (AnnotationBbox)
# # # # tooltip = None

# # # # # Keep track of the previous tooltip
# # # # previous_tooltip = None

# # # # def on_plot_hover(event):
# # # #     global previous_tooltip
    
# # # #     # Clear the previous tooltip if it exists
# # # #     if previous_tooltip:
# # # #         previous_tooltip.remove()
# # # #         previous_tooltip = None

# # # #     # Check for proximity to actual data points (this will limit tooltips to the vicinity of markers)
# # # #     for curve in [line_actual, line_predictions, line_forecast]:
# # # #         if curve.contains(event)[0]:
# # # #             # Find the index of the nearest data point
# # # #             if curve == line_actual:
# # # #                 label = "Actual Data (Train + Test)"
# # # #                 ind = np.argmin(np.abs(np.concatenate((x_train, x_test)) - event.xdata))
# # # #                 activity_value = float(combined_actual[ind])  # Extract scalar from array
# # # #                 text = f"{label}\nActivity: {activity_value:.2f}"
# # # #             elif curve == line_predictions:
# # # #                 label = "LSTM Predictions"
# # # #                 ind = np.argmin(np.abs(np.concatenate((x_train, x_test)) - event.xdata))
# # # #                 predicted_value = float(combined_predictions[ind])  # Extract scalar from array
# # # #                 text = f"{label}\nPredicted Activity: {predicted_value:.2f}"
# # # #             elif curve == line_forecast:
# # # #                 label = "15-Day Forecast"
# # # #                 ind = np.argmin(np.abs(x_forecast - event.xdata))
# # # #                 forecasted_value = float(forecasted_values[ind])  # Extract scalar from array
# # # #                 text = f"{label}\nForecast Day: {x_forecast[ind]}\nForecasted Activity: {forecasted_value:.2f}"
# # # #             else:
# # # #                 continue

# # # #             # Create the annotation box with the tooltip text and an arrow
# # # #             tooltip_text = TextArea(text, textprops=dict(color="black", size=6))  # Reduce text size by 30%
# # # #             tooltip = AnnotationBbox(
# # # #                 tooltip_text,
# # # #                 (event.xdata, event.ydata),
# # # #                 xybox=(35., 35.),  # Offset the tooltip
# # # #                 xycoords='data',
# # # #                 boxcoords="offset points",
# # # #                 arrowprops=dict(arrowstyle="->", color='white'),
# # # #                 bboxprops=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2')  # Ensure white background and reduced padding
# # # #             )
# # # #             ax.add_artist(tooltip)
# # # #             previous_tooltip = tooltip
# # # #             fig.canvas.draw_idle()
# # # #             break


# # # # # Connect the hover event to the figure
# # # # fig.canvas.mpl_connect("motion_notify_event", on_plot_hover)

# # # # # Show the plot
# # # # plt.show()



# # # import os
# # # import pandas as pd
# # # import numpy as np
# # # from sklearn.preprocessing import MinMaxScaler
# # # from keras.models import Sequential, load_model
# # # from keras.layers import LSTM, Dense, Dropout
# # # from keras.optimizers import Adam
# # # import joblib
# # # import matplotlib.pyplot as plt
# # # from sklearn.metrics import mean_absolute_percentage_error

# # # # Directory for saving the models and scalers
# # # model_dir = 'Individual Cow Activity Model'
# # # if not os.path.exists(model_dir):
# # #     os.makedirs(model_dir)

# # # # Function to create lagged features
# # # def create_lagged_features(df, lag=5):
# # #     df_lagged = df.copy()
# # #     for col in df.columns:
# # #         for i in range(1, lag + 1):
# # #             df_lagged[f'{col}_lag{i}'] = df[col].shift(i)
# # #     return df_lagged

# # # # Function to handle NaN values
# # # def handle_nans(df):
# # #     df.ffill(inplace=True)  # Forward fill
# # #     df.bfill(inplace=True)  # Backward fill
# # #     return df

# # # # Function to train and save the model for a specific cow
# # # def train_and_save_model(cow_id, cow_data):
# # #     # Preprocessing
# # #     lag = 5
# # #     cow_data_lagged = create_lagged_features(cow_data, lag=lag)
# # #     cow_data_lagged[f'{cow_id}_rolling'] = cow_data_lagged[cow_id].rolling(window=3, min_periods=1).mean()

# # #     # Handle NaNs
# # #     cow_data_lagged = handle_nans(cow_data_lagged)

# # #     # Define features and target
# # #     X = cow_data_lagged.drop([cow_id], axis=1).values
# # #     y = cow_data_lagged[cow_id].values

# # #     # Feature scaling using MinMaxScaler
# # #     scaler_X = MinMaxScaler(feature_range=(0, 1))
# # #     scaler_y = MinMaxScaler(feature_range=(0, 1))

# # #     # Fit the scalers on the training data
# # #     X_scaled = scaler_X.fit_transform(X)
# # #     y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

# # #     # Reshape input to be 3D for LSTM [samples, time steps, features]
# # #     X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

# # #     # Split data into training and testing sets (80% train, 20% test)
# # #     train_size = int(len(X_scaled) * 0.8)
# # #     X_train, X_test = X_scaled[:train_size], X_scaled[train_size:]
# # #     y_train, y_test = y_scaled[:train_size], y_scaled[train_size:]

# # #     # Model Training
# # #     model = Sequential()
# # #     model.add(LSTM(150, return_sequences=True, input_shape=(1, X_train.shape[2])))
# # #     model.add(Dropout(0.3))
# # #     model.add(LSTM(150, return_sequences=False))
# # #     model.add(Dropout(0.3))
# # #     model.add(Dense(50))
# # #     model.add(Dense(1))

# # #     optimizer = Adam(learning_rate=0.0005)
# # #     model.compile(optimizer=optimizer, loss='mean_squared_error')

# # #     # Train the model
# # #     model.fit(X_train, y_train, batch_size=4, epochs=200, verbose=1)

# # #     # Save the trained model and scalers
# # #     cow_model_dir = os.path.join(model_dir, f'Cow_{cow_id}_Model')
# # #     if not os.path.exists(cow_model_dir):
# # #         os.makedirs(cow_model_dir)

# # #     model.save(os.path.join(cow_model_dir, f'lstm_model_{cow_id}.keras'))
# # #     joblib.dump(scaler_X, os.path.join(cow_model_dir, f'scaler_X_{cow_id}.pkl'))
# # #     joblib.dump(scaler_y, os.path.join(cow_model_dir, f'scaler_y_{cow_id}.pkl'))

# # # # Function to load, retrain, and forecast for a specific cow with sliding window approach
# # # def load_and_forecast_model(cow_id, new_data_file, forecast_days=10):
# # #     cow_model_dir = os.path.join(model_dir, f'Cow_{cow_id}_Model')

# # #     # Check if the model exists
# # #     if not os.path.exists(cow_model_dir):
# # #         print(f"No model found for cow ID {cow_id}. Training a new model.")
# # #         data = pd.read_csv(new_data_file)
# # #         cow_data = data[[cow_id]]  # Select only the column for the specific cow
# # #         train_and_save_model(cow_id, cow_data)
# # #         return

# # #     # Load the model and scalers
# # #     model = load_model(os.path.join(cow_model_dir, f'lstm_model_{cow_id}.keras'))
# # #     scaler_X = joblib.load(os.path.join(cow_model_dir, f'scaler_X_{cow_id}.pkl'))
# # #     scaler_y = joblib.load(os.path.join(cow_model_dir, f'scaler_y_{cow_id}.pkl'))

# # #     # Load new data
# # #     new_data = pd.read_csv(new_data_file)
# # #     if cow_id not in new_data.columns:
# # #         print(f"Cow ID {cow_id} not found in the new dataset.")
# # #         return
# # #     cow_data = new_data[[cow_id]]  # Select only the column for the specific cow

# # #     # Preprocess the new data
# # #     lag = 5  # Larger window to capture more context for forecasting
# # #     cow_data_lagged = create_lagged_features(cow_data, lag=lag)
# # #     cow_data_lagged[f'{cow_id}_rolling'] = cow_data_lagged[cow_id].rolling(window=3, min_periods=1).mean()

# # #     # Handle NaNs
# # #     cow_data_lagged = handle_nans(cow_data_lagged)

# # #     X_new = cow_data_lagged.drop([cow_id], axis=1).values
# # #     y_new = cow_data_lagged[cow_id].values

# # #     # Make sure the scaler has been fit to the correct number of features
# # #     if X_new.shape[1] != scaler_X.n_features_in_:
# # #         # Refit the scaler on the new data if necessary
# # #         X_new_scaled = scaler_X.fit_transform(X_new)
# # #     else:
# # #         X_new_scaled = scaler_X.transform(X_new)
    
# # #     y_new_scaled = scaler_y.transform(y_new.reshape(-1, 1))

# # #     # Reshape input to be 3D for LSTM
# # #     X_new_scaled = X_new_scaled.reshape((X_new_scaled.shape[0], 1, X_new_scaled.shape[1]))

# # #     # Retrain the model
# # #     model.fit(X_new_scaled, y_new_scaled, batch_size=4, epochs=50, verbose=1)

# # #     # Make predictions on the test set
# # #     train_predictions_scaled = model.predict(X_new_scaled)
# # #     train_predictions = scaler_y.inverse_transform(train_predictions_scaled)
# # #     y_new_actual = scaler_y.inverse_transform(y_new_scaled)

# # #     # Split the new actual data into train and test sets for evaluation
# # #     train_size = int(len(y_new_actual) * 0.8)

# # #     # Calculate MAPE for train and test sets
# # #     train_mape = mean_absolute_percentage_error(y_new_actual[:train_size], train_predictions[:train_size])
# # #     test_mape = mean_absolute_percentage_error(y_new_actual[train_size:], train_predictions[train_size:])

# # #     # Calculate Train and Test Model Accuracy as percentages
# # #     train_accuracy = (1 - train_mape) * 100
# # #     test_accuracy = (1 - test_mape) * 100

# # #     # Forecast the next 10 days using sliding window approach
# # #     forecasted_activity_scaled = []
# # #     last_known_data = X_new_scaled[-lag:].reshape(1, lag, X_new_scaled.shape[2])  # Use the last 'lag' points for forecasting

# # #     for _ in range(forecast_days):
# # #         # Predict the next value
# # #         next_prediction_scaled = model.predict(last_known_data)
# # #         forecasted_activity_scaled.append(next_prediction_scaled[0, 0])

# # #         # Update the input by shifting the window and adding the new prediction
# # #         new_input = np.roll(last_known_data, shift=-1, axis=1)
# # #         new_input[0, -1, -1] = next_prediction_scaled  # Insert the new predicted value
# # #         last_known_data = new_input

# # #     # Inverse transform the forecasted values
# # #     forecasted_activity = scaler_y.inverse_transform(np.array(forecasted_activity_scaled).reshape(-1, 1))

# # #     # Plot the results
# # #     plt.style.use('dark_background')
# # #     fig, ax = plt.subplots(figsize=(14, 5))

# # #     ax.set_facecolor('black')
# # #     ax.xaxis.label.set_color('white')
# # #     ax.yaxis.label.set_color('white')
# # #     ax.tick_params(axis='x', colors='white')
# # #     ax.tick_params(axis='y', colors='white')

# # #     x_train = np.arange(len(y_new_actual))

# # #     # Plot actual data and predictions
# # #     line_actual, = ax.plot(x_train, y_new_actual, color='#00FFFF', marker='o', label='Actual Data', markersize=3, linewidth=0.8)
# # #     line_predictions, = ax.plot(x_train, train_predictions, color='#FF4500', linestyle='--', linewidth=1, label='LSTM Predictions')

# # #     # Plot forecasted data
# # #     x_forecast = np.arange(len(y_new_actual), len(y_new_actual) + forecast_days)
# # #     line_forecast, = ax.plot(x_forecast, forecasted_activity, color='#32CD32', linestyle='--', linewidth=1, label='Forecast (Next 10 Days)')

# # #     # Plot vertical line for train-test split
# # #     ax.axvline(x=train_size, color='white', linestyle='-', linewidth=1)

# # #     # Update title with Cow ID, Train Accuracy, and Test Accuracy as percentages
# # #     ax.set_title(f"Cow ID: {cow_id} | Train Model Accuracy: {train_accuracy:.2f}% | Test Model Accuracy: {test_accuracy:.2f}%", color='white')
# # #     ax.set_xlabel('Time (Days)', color='white')
# # #     ax.set_ylabel('Activity Level', color='white')

# # #     ax.legend(facecolor='black', edgecolor='white', fontsize=10, labelcolor='white')

# # #     plt.show()

# # # # Main execution flow
# # # if __name__ == "__main__":
# # #     cow_id = input("Enter the Cow ID (e.g., 6774, 6775, etc.): ")
# # #     new_data_file = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'  # Update the path if necessary

# # #     # Call the function to load and retrain the model and forecast the next 10 days
# # #     load_and_forecast_model(cow_id, new_data_file, forecast_days=10)



# # # //////////////////////////////////////////////////////////////TESTING INVERSE SCALE /////////////////////////////////////////////////////////////////////////////


# # # import pandas as pd
# # # from sklearn.preprocessing import MinMaxScaler
# # # import matplotlib.pyplot as plt

# # # # Load the dataset
# # # file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'
# # # data = pd.read_csv(file_path)

# # # # Restructure the data
# # # data['Date'] = pd.to_datetime(data['Unnamed: 0'])
# # # data = data.drop(columns=['Unnamed: 0'])  # Drop the old date column
# # # data.set_index('Date', inplace=True)

# # # # Filter data for Cow 6774
# # # cow_id = '6774'
# # # cow_6774_data = data[[cow_id]].copy()

# # # # Normalize the data
# # # scaler = MinMaxScaler()
# # # scaled_data = scaler.fit_transform(cow_6774_data)

# # # # Inverse transform the scaled data to compare with original
# # # inverse_scaled_data = scaler.inverse_transform(scaled_data)

# # # # Plot original and inverse scaled data
# # # plt.figure(figsize=(12, 6))
# # # plt.plot(cow_6774_data.index, cow_6774_data[cow_id], label="Original Data", color='cyan')
# # # plt.plot(cow_6774_data.index, inverse_scaled_data, label="Inverse Scaled Data", color='orange', linestyle='dashed')
# # # plt.legend()
# # # plt.xlabel('Date')
# # # plt.ylabel('Activity')
# # # plt.title(f'Comparison of Original and Inverse Scaled Data for Cow ID: {cow_id}')
# # # plt.show()



# # # # /////////////////////////////////////////////////////////////////////////// BACK UP CODE //////////////////////////////////////////////////////////////////////////////////



# # # import pandas as pd
# # # from sklearn.preprocessing import MinMaxScaler
# # # from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, mean_absolute_error
# # # from tensorflow.keras.models import Sequential
# # # from tensorflow.keras.layers import LSTM, Dense, Dropout
# # # from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
# # # import numpy as np
# # # import matplotlib.pyplot as plt

# # # # Load the dataset
# # # file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'
# # # data = pd.read_csv(file_path)

# # # # Restructure the data
# # # data['Date'] = pd.to_datetime(data['Unnamed: 0'])
# # # data = data.drop(columns=['Unnamed: 0'])  # Drop the old date column
# # # data.set_index('Date', inplace=True)

# # # # Filter data for Cow 6774
# # # cow_id = '6774'
# # # cow_6774_data = data[[cow_id]].copy()

# # # # Normalize the data
# # # scaler = MinMaxScaler()
# # # scaled_data = scaler.fit_transform(cow_6774_data)

# # # # Prepare data for the LSTM model
# # # X = scaled_data  # Features
# # # y = scaled_data[:, 0]  # Target variable

# # # # Reshape X for LSTM: [samples, time steps, features]
# # # X = X.reshape((X.shape[0], 1, 1))

# # # # Split data into training and testing sets
# # # train_size = int(len(X) * 0.8)
# # # X_train, X_test = X[:train_size], X[train_size:]
# # # y_train, y_test = y[:train_size], y[train_size:]

# # # # Print the date range for training and testing data
# # # train_start_date = cow_6774_data.index[0]
# # # train_end_date = cow_6774_data.index[train_size - 1]
# # # test_start_date = cow_6774_data.index[train_size]
# # # test_end_date = cow_6774_data.index[-1]

# # # print(f"Training data is from {train_start_date.date()} to {train_end_date.date()}")
# # # print(f"Test data is from {test_start_date.date()} to {test_end_date.date()}")

# # # # Define the Vanilla LSTM model
# # # def build_vanilla_lstm_model(input_shape):
# # #     model = Sequential()
# # #     model.add(LSTM(100, activation='relu', input_shape=input_shape))
# # #     model.add(Dropout(0.3))  # Increased Dropout for regularization
# # #     model.add(Dense(1))
# # #     model.compile(optimizer='adam', loss='mse')
# # #     return model

# # # # Build and train the Vanilla LSTM model
# # # vanilla_lstm_model = build_vanilla_lstm_model((1, 1))
# # # early_stop = EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)
# # # reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6)

# # # history = vanilla_lstm_model.fit(X_train, y_train, epochs=400, batch_size=16, verbose=1, validation_data=(X_test, y_test), callbacks=[early_stop, reduce_lr])

# # # # Predict on the entire dataset (training + test)
# # # y_pred_scaled_all = vanilla_lstm_model.predict(X)

# # # # Inverse transform the predictions and the true data
# # # y_pred_all = scaler.inverse_transform(np.concatenate([y_pred_scaled_all, np.zeros((len(y_pred_scaled_all), 1))], axis=1))[:, 0]
# # # y_all_inv = scaler.inverse_transform(np.concatenate([y.reshape(-1, 1), np.zeros((len(y), 1))], axis=1))[:, 0]

# # # # Evaluate the model using additional metrics
# # # lstm_rmse = np.sqrt(mean_squared_error(y_all_inv[train_size:], y_pred_all[train_size:]))
# # # lstm_mae = mean_absolute_error(y_all_inv[train_size:], y_pred_all[train_size:])
# # # lstm_mape = mean_absolute_percentage_error(y_all_inv[train_size:], y_pred_all[train_size:]) * 100

# # # print(f'LSTM Model RMSE: {lstm_rmse:.2f}')
# # # print(f'LSTM Model MAE: {lstm_mae:.2f}')
# # # print(f'LSTM Model MAPE: {lstm_mape:.2f}%')

# # # # Plotting the results
# # # plt.figure(figsize=(12, 6))

# # # # Plot training data
# # # plt.plot(cow_6774_data.index[:train_size], y_all_inv[:train_size], label="Training Data", color='orange')
# # # # Plot actual test data
# # # plt.plot(cow_6774_data.index[train_size:], y_all_inv[train_size:], label="Test Data", color='blue')
# # # # Plot predictions for the entire dataset
# # # plt.plot(cow_6774_data.index, y_pred_all, label="LSTM Predictions", linestyle='dashed', color='green')

# # # # Add vertical line for train/test split
# # # plt.axvline(x=cow_6774_data.index[train_size], color='r', linestyle='--', label='Train/Test Split')

# # # plt.legend()
# # # plt.xlabel('Date')
# # # plt.ylabel('Activity')
# # # plt.title(f'COW ID: {cow_id} | Model Accuracy: {100 - lstm_mape:.2f}% (MAPE), RMSE: {lstm_rmse:.2f}, MAE: {lstm_mae:.2f}')
# # # plt.show()

# # # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////




# # import pandas as pd
# # from sklearn.preprocessing import MinMaxScaler
# # from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, mean_absolute_error
# # from tensorflow.keras.models import Sequential
# # from tensorflow.keras.layers import LSTM, Dense
# # from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
# # import numpy as np
# # import matplotlib.pyplot as plt

# # # Load the dataset
# # file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'  # Update with the correct path
# # data = pd.read_csv(file_path)

# # # Restructure the data
# # data['Date'] = pd.to_datetime(data['Unnamed: 0'])
# # data = data.drop(columns=['Unnamed: 0'])  # Drop the old date column
# # data.set_index('Date', inplace=True)

# # # Filter data for Cow 6774
# # cow_id = '6774'
# # cow_6774_data = data[[cow_id]].copy()

# # # Normalize the data
# # scaler = MinMaxScaler()
# # scaled_data = scaler.fit_transform(cow_6774_data)

# # # Prepare data with sequences
# # sequence_length = 10  # Shorter sequence length to see if it captures more detail

# # def create_sequences(data, seq_length):
# #     X = []
# #     y = []
# #     for i in range(len(data) - seq_length):
# #         X.append(data[i:i + seq_length, 0])  # Using the target variable
# #         y.append(data[i + seq_length, 0])    # Target is the next day's value
# #     return np.array(X), np.array(y)

# # # Create sequences
# # X, y = create_sequences(scaled_data, sequence_length)

# # # Reshape X to be [samples, time steps, features]
# # X = X.reshape((X.shape[0], X.shape[1], 1))

# # # Split the data into training and testing sets
# # train_size = int(len(X) * 0.8)
# # X_train, X_test = X[:train_size], X[train_size:]
# # y_train, y_test = y[:train_size], y[train_size:]

# # # Print the correct date range for training and testing data
# # train_start_date = cow_6774_data.index[sequence_length]
# # train_end_date = cow_6774_data.index[train_size + sequence_length - 1]
# # test_start_date = cow_6774_data.index[train_size + sequence_length]
# # test_end_date = cow_6774_data.index[-1]

# # train_percentage = (train_size / len(X)) * 100
# # test_percentage = ((len(X) - train_size) / len(X)) * 100

# # print(f"Training data is from {train_start_date.date()} to {train_end_date.date()}")
# # print(f"Test data is from {test_start_date.date()} to {test_end_date.date()}")
# # print(f"Training data percentage: {train_percentage:.2f}%")
# # print(f"Test data percentage: {test_percentage:.2f}%")

# # # Define a Vanilla LSTM model
# # def build_vanilla_lstm_model(input_shape):
# #     model = Sequential()
# #     model.add(LSTM(64, activation='relu', input_shape=input_shape))
# #     model.add(Dense(1))
# #     model.compile(optimizer='adam', loss='mse')
# #     return model

# # # Build and train the Vanilla LSTM model
# # vanilla_lstm_model = build_vanilla_lstm_model((X.shape[1], X.shape[2]))
# # early_stop = EarlyStopping(monitor='val_loss', patience=30, restore_best_weights=True)
# # reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, min_lr=1e-6)

# # history = vanilla_lstm_model.fit(X_train, y_train, epochs=800, batch_size=8, verbose=1, validation_data=(X_test, y_test), callbacks=[early_stop, reduce_lr])

# # # Predict on the entire dataset (training + test)
# # y_pred_scaled_all = vanilla_lstm_model.predict(np.concatenate([X_train, X_test], axis=0))

# # # Inverse transform the predictions and the true data
# # y_pred_all = scaler.inverse_transform(np.concatenate([y_pred_scaled_all, np.zeros((len(y_pred_scaled_all), 1))], axis=1))[:, 0]
# # y_all_inv = scaler.inverse_transform(np.concatenate([y.reshape(-1, 1), np.zeros((len(y), 1))], axis=1))[:, 0]

# # # Evaluate the model using additional metrics for the test data
# # lstm_rmse = np.sqrt(mean_squared_error(y_all_inv[train_size:], y_pred_all[train_size:]))
# # lstm_mae = mean_absolute_error(y_all_inv[train_size:], y_pred_all[train_size:])
# # lstm_mape = mean_absolute_percentage_error(y_all_inv[train_size:], y_pred_all[train_size:]) * 100

# # print(f'LSTM Model RMSE: {lstm_rmse:.2f}')
# # print(f'LSTM Model MAE: {lstm_mae:.2f}')
# # print(f'LSTM Model MAPE: {lstm_mape:.2f}%')

# # # Plotting the results for the test data only
# # plt.figure(figsize=(12, 6))

# # # Plot the full actual data for reference
# # plt.plot(cow_6774_data.index, cow_6774_data[cow_id], label="Actual Data", color='orange')

# # # Plot test data (actual values)
# # plt.plot(test_plot_index, y_all_inv[train_size:], label="Test Data (Actual)", color='cyan')

# # # Plot LSTM predictions for the test data
# # plt.plot(test_plot_index, y_pred_all[train_size:], label="LSTM Predictions (Test)", linestyle='dashed', color='green')

# # # Add vertical line for train/test split
# # plt.axvline(x=cow_6774_data.index[train_size + sequence_length], color='r', linestyle='--', label='Train/Test Split')

# # plt.legend()
# # plt.xlabel('Date')
# # plt.ylabel('Activity')
# # plt.title(f'COW ID: {cow_id} | Model Accuracy: {100 - lstm_mape:.2f}% (MAPE), RMSE: {lstm_rmse:.2f}, MAE: {lstm_mae:.2f}')
# # plt.show()


# import pandas as pd
# import matplotlib.pyplot as plt

# # Step 1: Clean and Prepare Alerts Data
# def clean_alerts_data(file_path):
#     trial_alerts_data = pd.read_csv(file_path)
    
#     # Replace '1013' with '2023' and '1014' with '2024'
#     trial_alerts_data['Unnamed: 0'] = trial_alerts_data['Unnamed: 0'].str.replace('1013', '2023')
#     trial_alerts_data['Unnamed: 0'] = trial_alerts_data['Unnamed: 0'].str.replace('1014', '2024')
    
#     # Correct the invalid date '31/11/2023' to '30/11/2023'
#     trial_alerts_data['Unnamed: 0'] = trial_alerts_data['Unnamed: 0'].str.replace('31/11/2023', '30/11/2023')
    
#     # Convert the date column to datetime format
#     trial_alerts_data['Date'] = pd.to_datetime(trial_alerts_data['Unnamed: 0'], format='%d/%m/%Y', errors='coerce')
    
#     # Convert all columns except 'Date' to numeric, forcing errors to NaN
#     for col in trial_alerts_data.columns[1:]:
#         trial_alerts_data[col] = pd.to_numeric(trial_alerts_data[col], errors='coerce')
    
#     return trial_alerts_data

# # Step 2: Load and Clean Data
# alerts_file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/trialAlerts.csv'  # Update the path as needed
# alerts_data = clean_alerts_data(alerts_file_path)

# # Step 3: Analyze Alert Trends

# # 3.1: Aggregating alert data to count daily alerts
# daily_alerts = alerts_data.groupby('Date').sum().sum(axis=1)

# # 3.2: Counting alerts by cow
# cow_alerts = alerts_data.iloc[:, 1:-1].sum()

# # 3.3: Counting the distribution of alert levels (0, 1, 2)
# alert_distribution = alerts_data.iloc[:, 1:-1].stack().value_counts()

# # Step 4: Plotting the Results

# # 4.1: Daily Alert Count
# plt.figure(figsize=(12, 6))
# daily_alerts.plot(kind='bar')
# plt.title('Daily Alert Count Across All Cows')
# plt.xlabel('Date')
# plt.ylabel('Total Alerts')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

# # 4.2: Cow-Specific Alert Analysis
# plt.figure(figsize=(12, 6))
# cow_alerts.plot(kind='bar')
# plt.title('Total Alerts by Cow ID')
# plt.xlabel('Cow ID')
# plt.ylabel('Total Alerts')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

# # 4.3: Distribution of Alert Levels
# plt.figure(figsize=(8, 6))
# alert_distribution.plot(kind='bar', color=['green', 'orange', 'red'])
# plt.title('Distribution of Alert Levels')
# plt.xlabel('Alert Level')
# plt.ylabel('Count')
# plt.xticks(rotation=0)
# plt.tight_layout()
# plt.show()




# # import pandas as pd
# # import numpy as np
# # import matplotlib.pyplot as plt
# # from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, mean_absolute_error
# # from tensorflow.keras.models import Sequential
# # from tensorflow.keras.layers import LSTM, Dense, Input
# # from tensorflow.keras.callbacks import EarlyStopping

# # # Step 1: Clean and Prepare Alerts Data
# # def clean_alerts_data(file_path):
# #     trial_alerts_data = pd.read_csv(file_path)
    
# #     # Correct the year from '1013' to '2023' and '1014' to '2024' in the 'Unnamed: 0' (Date) column
# #     trial_alerts_data['Unnamed: 0'] = trial_alerts_data['Unnamed: 0'].str.replace('1013', '2023').str.replace('1014', '2024')
    
# #     # Fix the incorrect date of 31/11/2023 to 30/11/2023
# #     trial_alerts_data['Unnamed: 0'] = trial_alerts_data['Unnamed: 0'].str.replace('31/11/2023', '30/11/2023')
    
# #     # Convert the corrected 'Unnamed: 0' column to datetime format
# #     trial_alerts_data['Date'] = pd.to_datetime(trial_alerts_data['Unnamed: 0'], format='%d/%m/%Y', errors='coerce')
    
# #     # Melt the DataFrame to long format
# #     cleaned_alerts_data = trial_alerts_data.melt(id_vars=['Date'], var_name='CowID', value_name='Alert')
    
# #     # Remove any rows where 'Alert' is not numeric
# #     cleaned_alerts_data = cleaned_alerts_data[cleaned_alerts_data['CowID'] != 'Unnamed: 0']
    
# #     # Convert 'Alert' values to numeric
# #     cleaned_alerts_data['Alert'] = pd.to_numeric(cleaned_alerts_data['Alert'], errors='coerce')
    
# #     # Drop any remaining rows with missing values
# #     cleaned_alerts_data.dropna(inplace=True)
    
# #     return cleaned_alerts_data

# # # Step 2: Merge Alerts Data with Predictions and Filter for November 2023
# # def merge_data(alerts_file_path, cow_id):
# #     alerts_data = clean_alerts_data(alerts_file_path)

# #     # Load activity and temperature predictions
# #     activity_predictions = pd.read_csv(f'activity_predictions_{cow_id}.csv')
# #     temperature_predictions = pd.read_csv(f'temperature_predictions_{cow_id}.csv')

# #     # Add the CowID column to the predictions data
# #     activity_predictions['CowID'] = cow_id
# #     temperature_predictions['CowID'] = cow_id

# #     # Merge the predictions on Date
# #     combined_predictions = pd.merge(activity_predictions, temperature_predictions, on=['Date', 'CowID'])

# #     # Ensure that the data is in time order if not already
# #     combined_predictions['Date'] = pd.to_datetime(combined_predictions['Date'])
# #     combined_predictions.set_index('Date', inplace=True)

# #     # Merge the combined predictions with alerts data on Date and CowID
# #     final_data = pd.merge(combined_predictions.reset_index(), alerts_data, on=['Date', 'CowID'])

# #     # Filter for November 13, 2023, to November 30, 2023
# #     final_data = final_data[(final_data['Date'] >= '2023-11-13') & (final_data['Date'] <= '2023-11-30')]

# #     return final_data, combined_predictions.shape[1]  # Returning time_steps along with final_data

# # # Step 3: Prepare Data for LSTM Using a Rolling Window
# # def prepare_lstm_data(final_data, time_steps):
# #     X = []
# #     y = []
# #     for i in range(len(final_data) - time_steps):
# #         X.append(final_data[['activity_prediction', 'temperature_prediction']].values[i:(i + time_steps)])
# #         y.append(final_data['Alert'].values[i + time_steps])
    
# #     X = np.array(X)
# #     y = np.array(y)
    
# #     return X, y

# # # Step 4: Build and Train the Vanilla LSTM Model
# # def train_lstm_model(X, y, time_steps):
# #     # Split data into training and testing sets
# #     train_size = int(len(X) * 0.8)
# #     X_train, X_test = X[:train_size], X[train_size:]
# #     y_train, y_test = y[:train_size], y[train_size:]

# #     # Define the Vanilla LSTM model
# #     model = Sequential()
# #     model.add(Input(shape=(time_steps, 2)))  # Correct input shape
# #     model.add(LSTM(50, activation='relu'))
# #     model.add(Dense(1, activation='sigmoid'))  # Sigmoid for binary classification
# #     model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# #     # Train the model with early stopping
# #     early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
# #     history = model.fit(X_train, y_train, epochs=200, batch_size=8, verbose=1, validation_data=(X_test, y_test), callbacks=[early_stop])

# #     return model, X_test, y_test

# # # Step 5: Function to Display Alerts and Forecasts
# # def display_results(cow_id, model, X_test, y_test, final_data, time_steps):
# #     # Predict on the test set
# #     y_pred_test = (model.predict(X_test) > 0.5).astype("int32")

# #     # Evaluate the model
# #     lstm_mape = mean_absolute_percentage_error(y_test, y_pred_test) * 100
# #     lstm_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
# #     lstm_mae = mean_absolute_error(y_test, y_pred_test)

# #     print(f'Combined LSTM Model MAPE: {lstm_mape:.2f}%')
# #     print(f'Combined LSTM Model RMSE: {lstm_rmse:.2f}')
# #     print(f'Combined LSTM Model MAE: {lstm_mae:.2f}')

# #     # Forecast: Assuming we want to predict the next 7 days (for example)
# #     num_forecast_steps = 7
# #     last_known_data = X_test[-1].reshape(1, time_steps, 2)
# #     forecasts = []

# #     for _ in range(num_forecast_steps):
# #         # Predict the next step
# #         next_pred = model.predict(last_known_data)[0][0]
# #         forecasts.append(next_pred)
        
# #         # Shift the window and add the new prediction to the last known data
# #         last_known_data = np.roll(last_known_data, -1, axis=1)
# #         last_known_data[0, -1, 0] = next_pred  # Update the last position with the new prediction

# #     # Update the final data with forecasted results
# #     forecast_dates = pd.date_range(start=final_data['Date'].iloc[-1] + pd.Timedelta(days=1), periods=num_forecast_steps)
# #     forecast_df = pd.DataFrame({'Date': forecast_dates, 'CowID': cow_id, 'Alert': forecasts})
    
# #     # Determine the latest alert (0 or 1) from the predictions
# #     latest_alert = int(y_pred_test[-1])

# #     # Plot the results
# #     plt.figure(figsize=(12, 6))
# #     plt.plot(final_data['Date'].iloc[-len(y_test):], y_test, label="Actual Alerts", color='blue')
# #     plt.plot(final_data['Date'].iloc[-len(y_test):], y_pred_test.flatten(), label="Predicted Alerts", linestyle='dashed', color='green')
# #     plt.plot(forecast_dates, forecasts, label="Forecasted Alerts", linestyle='dotted', color='red')
# #     plt.legend()
# #     plt.xlabel('Date')
# #     plt.ylabel('Alert Level')
# #     plt.title(f'COW ID: {cow_id} | Current Alert: {latest_alert} | Combined Model')
# #     plt.xticks(rotation=45)
# #     plt.show()

# # # Step 6: Main Function to Run the Analysis
# # def main():
# #     alerts_file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/trialAlerts.csv'
# #     cow_id = input("Please enter the Cow ID: ")

# #     # Merge the data and get time_steps
# #     final_data, time_steps = merge_data(alerts_file_path, cow_id)
# #     print(f"Final merged data shape: {final_data.shape}")
# #     print(final_data.head())

# #     # Prepare data for LSTM
# #     X, y = prepare_lstm_data(final_data, time_steps)

# #     # Train the LSTM model
# #     model, X_test, y_test = train_lstm_model(X, y, time_steps)

# #     # Display the results
# #     display_results(cow_id, model, X_test, y_test, final_data, time_steps)

# # if __name__ == "__main__":
# #     main()



# # import os
# # import pandas as pd
# # import numpy as np
# # from sklearn.preprocessing import MinMaxScaler
# # from keras.models import Sequential
# # from keras.layers import LSTM, Dense
# # import joblib
# # import matplotlib.pyplot as plt
# # from matplotlib.offsetbox import AnnotationBbox, TextArea

# # # Create the directory for saving the model and scalers if it doesn't exist
# # model_dir = 'Dairy Herd Activity Model'
# # if not os.path.exists(model_dir):
# #     os.makedirs(model_dir)

# # # ====== Training Phase ======

# # # Load the dataset
# # file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'  # Update this path if necessary
# # data = pd.read_csv(file_path)

# # # Rename the columns for easier access
# # data.columns = ['Date'] + [f'Feature_{i}' for i in range(1, 29)] + ['Group_mean']

# # # Convert 'Date' column to datetime (though we won't use it on the x-axis here)
# # data['Date'] = pd.to_datetime(data['Date'])

# # # Define features and target
# # X = data.drop(['Date', 'Group_mean'], axis=1).values
# # y = data['Group_mean'].values
# # dates = data['Date'].values  # Store dates for later, though x-axis will use integers

# # # Feature scaling using MinMaxScaler
# # scaler_X = MinMaxScaler(feature_range=(0, 1))
# # scaler_y = MinMaxScaler(feature_range=(0, 1))

# # X_scaled = scaler_X.fit_transform(X)
# # y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

# # # Reshape input to be 3D for LSTM [samples, time steps, features]
# # X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

# # # Split the data into training and testing sets (80% train, 20% test)
# # split_index = int(X_scaled.shape[0] * 0.8)
# # X_train, X_test = X_scaled[:split_index], X_scaled[split_index:]
# # y_train, y_test = y_scaled[:split_index], y_scaled[split_index:]

# # # Build the LSTM model
# # model = Sequential()
# # model.add(LSTM(50, return_sequences=True, input_shape=(1, X_train.shape[2])))
# # model.add(LSTM(50, return_sequences=False))
# # model.add(Dense(25))
# # model.add(Dense(1))

# # # Compile the model
# # model.compile(optimizer='adam', loss='mean_squared_error')

# # # Train the model on the training dataset
# # model.fit(X_train, y_train, batch_size=1, epochs=50)

# # # Save the trained model and scalers in the 'Dairy Herd Activity Model' folder
# # model.save(os.path.join(model_dir, 'lstm_model.keras'))  # Using the recommended keras format
# # joblib.dump(scaler_X, os.path.join(model_dir, 'scaler_X.pkl'))
# # joblib.dump(scaler_y, os.path.join(model_dir, 'scaler_y.pkl'))

# # # Make predictions on both the training and testing sets
# # train_predictions_scaled = model.predict(X_train)
# # test_predictions_scaled = model.predict(X_test)

# # # Inverse transform the predictions and actual values to get them back to the original scale
# # train_predictions = scaler_y.inverse_transform(train_predictions_scaled)
# # test_predictions = scaler_y.inverse_transform(test_predictions_scaled)
# # y_train_actual = scaler_y.inverse_transform(y_train)
# # y_test_actual = scaler_y.inverse_transform(y_test)

# # # Combine actual and predicted values for continuous plotting
# # y_actual = np.concatenate((y_train_actual, y_test_actual), axis=0)
# # predictions = np.concatenate((train_predictions, test_predictions), axis=0)

# # # Calculate accuracy using Mean Absolute Percentage Error (MAPE)
# # train_accuracy = 100 - np.mean(np.abs((y_train_actual - train_predictions) / y_train_actual)) * 100
# # test_accuracy = 100 - np.mean(np.abs((y_test_actual - test_predictions) / y_test_actual)) * 100

# # # ====== Forecasting Phase ======

# # # Number of days to forecast
# # forecast_days = 15

# # # Get the last data point from the test set as the starting point for forecasting
# # last_input = X_test[-1]

# # # Create a list to store the forecasted values
# # forecasted_values = []

# # # Forecast for the next 15 days
# # for day in range(forecast_days):
# #     # Predict the next day's value
# #     next_prediction_scaled = model.predict(last_input.reshape(1, 1, -1))
    
# #     # Inverse transform the prediction back to the original scale
# #     next_prediction = scaler_y.inverse_transform(next_prediction_scaled)
    
# #     # Store the forecasted value
# #     forecasted_values.append(next_prediction[0][0])
    
# #     # Update the last_input with the predicted value for the next iteration
# #     last_input = np.roll(last_input, -1)
# #     last_input[0, -1] = next_prediction_scaled[0][0]  # Replace with the predicted value

# # # Convert forecasted values to a 2D array for consistent dimensions with predictions
# # forecasted_values = np.array(forecasted_values).reshape(-1, 1)

# # # ====== Plotting Phase with Tooltips ======

# # # Set dark mode style for the plot
# # plt.style.use('dark_background')

# # # Create the figure and axis
# # fig, ax = plt.subplots(figsize=(14, 5))

# # # Customize the axis colors for dark mode
# # ax.set_facecolor('black')
# # ax.xaxis.label.set_color('white')
# # ax.yaxis.label.set_color('white')
# # ax.tick_params(axis='x', colors='white')
# # ax.tick_params(axis='y', colors='white')

# # # Use integer x-axis values instead of dates
# # x_train = np.arange(len(y_train_actual))
# # x_test = np.arange(len(y_train_actual), len(y_train_actual) + len(y_test_actual))
# # x_forecast = np.arange(len(y_actual), len(y_actual) + forecast_days)

# # # Plot the actual data with glowing dark cyan color and thin lines
# # line_actual, = ax.plot(np.concatenate((x_train, x_test)), y_actual, color='#00FFFF', marker='o', label='Actual Data (Train + Test)', markersize=3, linewidth=0.8)

# # # Plot the LSTM predictions as a dotted line
# # line_predictions, = ax.plot(np.concatenate((x_train, x_test)), predictions, color='#FF4500', linestyle='--', linewidth=1, label='LSTM Predictions')

# # # Plot the forecasted values as a bright red thin line with data points
# # line_forecast, = ax.plot(x_forecast, forecasted_values, color='red', linestyle='-', marker='o', markersize=3, linewidth=1, label='15-Day Forecast')

# # # Add a thin black solid line for the train/test split
# # ax.axvline(x=len(x_train), color='white', linestyle='-', linewidth=1)
# # ax.text(len(x_train), ax.get_ylim()[1] * 0.98, 'Train/Test Split', rotation=90, verticalalignment='top',
# #         horizontalalignment='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.4'), color='black', fontsize=8)

# # # Add a thin black solid line for the start of the forecast
# # ax.axvline(x=len(x_train) + len(x_test), color='white', linestyle='-', linewidth=1)
# # ax.text(len(x_train) + len(x_test), ax.get_ylim()[1] * 0.98, 'Forecast Start', rotation=90, verticalalignment='top',
# #         horizontalalignment='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.4'), color='black', fontsize=8)

# # # Add title and labels
# # ax.set_title(f"Entire Dairy Herd Activity Model | Train Data Prediction Accuracy: {train_accuracy:.2f}% | Test Data Prediction Accuracy: {test_accuracy:.2f}% | 15-Day Forecast", color='white')
# # ax.set_xlabel('Time (Days)', color='white')
# # ax.set_ylabel('Group Mean', color='white')

# # # Format x-axis as integers
# # ax.set_xticks(np.arange(0, len(y_actual) + forecast_days, 10))

# # # Legend with white text
# # ax.legend(facecolor='black', edgecolor='white', fontsize=10, labelcolor='white')

# # # Initialize tooltip (AnnotationBbox)
# # tooltip = None

# # # Keep track of the previous tooltip
# # previous_tooltip = None


# # def on_plot_hover(event):
# #     global previous_tooltip
    
# #     # Clear the previous tooltip if it exists
# #     if previous_tooltip:
# #         previous_tooltip.remove()
# #         previous_tooltip = None

# #     for curve in [line_actual, line_predictions, line_forecast]:
# #         if curve.contains(event)[0]:
# #             if curve == line_actual:
# #                 label = "Actual Data (Train + Test)"
# #                 ind = np.argmin(np.abs(np.concatenate((x_train, x_test)) - event.xdata))
# #                 activity_value = float(y_actual[ind])  # Extract scalar from array
# #                 text = f"{label}\nDate: {str(dates[ind])[:10]}\nActivity: {activity_value:.2f}"
# #             elif curve == line_predictions:
# #                 label = "LSTM Predictions"
# #                 ind = np.argmin(np.abs(np.concatenate((x_train, x_test)) - event.xdata))
# #                 predicted_value = float(predictions[ind])  # Extract scalar from array
# #                 text = f"{label}\nDate: {str(dates[ind])[:10]}\nPredicted Activity: {predicted_value:.2f}"
# #             elif curve == line_forecast:
# #                 label = "15-Day Forecast"
# #                 ind = np.argmin(np.abs(x_forecast - event.xdata))
# #                 forecasted_value = float(forecasted_values[ind])  # Extract scalar from array
# #                 text = f"{label}\nForecast Day: {x_forecast[ind]}\nForecasted Activity: {forecasted_value:.2f}"
# #             else:
# #                 continue

# #             # Create the annotation box with the tooltip text and an arrow
# #             tooltip_text = TextArea(text, textprops=dict(color="black", size=6))  # Reduce text size by 30%
# #             tooltip = AnnotationBbox(
# #                 tooltip_text,
# #                 (event.xdata, event.ydata),
# #                 xybox=(35., 35.),  # Reduce the tooltip size by 30%
# #                 xycoords='data',
# #                 boxcoords="offset points",
# #                 arrowprops=dict(arrowstyle="->", color='white'),
# #                 bboxprops=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2')  # Ensure white background and reduced padding
# #             )
# #             ax.add_artist(tooltip)
# #             previous_tooltip = tooltip
# #             fig.canvas.draw_idle()
# #             break


# # # Connect the hover event to the figure
# # fig.canvas.mpl_connect("motion_notify_event", on_plot_hover)

# # # Show the plot with dark mode settings and tooltips
# # plt.show()


# # 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'


# import os
# import pandas as pd
# import numpy as np
# from sklearn.preprocessing import MinMaxScaler
# from keras.models import Sequential
# from keras.layers import LSTM, Dense
# import joblib
# import matplotlib.pyplot as plt
# from matplotlib.offsetbox import AnnotationBbox, TextArea

# # Create the directory for saving the model and scalers if it doesn't exist
# model_dir = 'Dairy Herd Activity Model'
# if not os.path.exists(model_dir):
#     os.makedirs(model_dir)

# # ====== Training Phase ======

# # Load the dataset
# file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'  # Adjust this path as needed for your environment
# data = pd.read_csv(file_path)

# # Rename the columns for easier access
# data.columns = ['Date'] + [f'Feature_{i}' for i in range(1, 29)] + ['Group_mean']

# # Convert 'Date' column to datetime (though we won't use it on the x-axis here)
# data['Date'] = pd.to_datetime(data['Date'])

# # Drop the 'Group_mean' as we are no longer using it
# data = data.drop(columns=['Group_mean'])

# # Reshape data to simulate cows
# num_cows = 10  # We are assuming 10 cows

# # Trim the dataset to be evenly divisible by the number of cows
# trimmed_size = (data.shape[0] // num_cows) * num_cows
# data = data.iloc[:trimmed_size]  # Trim the data

# # Calculate timesteps based on the number of cows and the trimmed size of the dataset
# timesteps = data.shape[0] // num_cows  # This will give us timesteps per cow

# # Prepare the feature matrix
# X = data.drop(columns=['Date']).values

# # Reshape X to [num_cows, timesteps, features]
# X = X.reshape((num_cows, timesteps, -1))  # Reshape to [num_cows, timesteps, features]

# # Create target values for training, using the first feature of the last timestep as target
# y = X[:, -1, 0]  # Using the first feature of the last timestep as target, adjust based on your use case

# # Feature scaling using MinMaxScaler
# scaler_X = MinMaxScaler(feature_range=(0, 1))
# X_scaled = scaler_X.fit_transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)

# scaler_y = MinMaxScaler(feature_range=(0, 1))
# y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

# # Split the data into training and testing sets (80% train, 20% test)
# split_index = int(num_cows * 0.8)
# X_train, X_test = X_scaled[:split_index], X_scaled[split_index:]
# y_train, y_test = y_scaled[:split_index], y_scaled[split_index:]

# # Print the number of training and testing days
# print(f"Training days: {X_train.shape[0]} cows * {timesteps} timesteps = {X_train.shape[0] * timesteps} days")
# print(f"Testing days: {X_test.shape[0]} cows * {timesteps} timesteps = {X_test.shape[0] * timesteps} days")

# # Build the LSTM model
# model = Sequential()
# model.add(LSTM(50, return_sequences=True, input_shape=(timesteps, X_train.shape[2])))
# model.add(LSTM(50, return_sequences=False))
# model.add(Dense(25))
# model.add(Dense(1))

# # Compile the model
# model.compile(optimizer='adam', loss='mean_squared_error')

# # Train the model on the training dataset
# model.fit(X_train, y_train, batch_size=1, epochs=50)

# # Save the trained model and scalers in the 'Dairy Herd Activity Model' folder
# model.save(os.path.join(model_dir, 'lstm_model.keras'))  # Using the recommended keras format
# joblib.dump(scaler_X, os.path.join(model_dir, 'scaler_X.pkl'))
# joblib.dump(scaler_y, os.path.join(model_dir, 'scaler_y.pkl'))

# # Make predictions on both the training and testing sets
# train_predictions_scaled = model.predict(X_train)
# test_predictions_scaled = model.predict(X_test)

# # Inverse transform the predictions and actual values to get them back to the original scale
# train_predictions = scaler_y.inverse_transform(train_predictions_scaled)
# test_predictions = scaler_y.inverse_transform(test_predictions_scaled)
# y_train_actual = scaler_y.inverse_transform(y_train)
# y_test_actual = scaler_y.inverse_transform(y_test)

# # Combine actual and predicted values for continuous plotting
# y_actual = np.concatenate((y_train_actual, y_test_actual), axis=0)
# predictions = np.concatenate((train_predictions, test_predictions), axis=0)

# # Calculate accuracy using Mean Absolute Percentage Error (MAPE)
# train_accuracy = 100 - np.mean(np.abs((y_train_actual - train_predictions) / y_train_actual)) * 100
# test_accuracy = 100 - np.mean(np.abs((y_test_actual - test_predictions) / y_test_actual)) * 100

# # ====== Forecasting Phase ======

# # Number of days to forecast
# forecast_days = 15

# # Get the last data point from the test set as the starting point for forecasting
# last_input = X_test[-1]

# # Create a list to store the forecasted values
# forecasted_values = []

# # Forecast for the next 15 days
# for day in range(forecast_days):
#     # Predict the next day's value
#     next_prediction_scaled = model.predict(last_input.reshape(1, timesteps, -1))
    
#     # Inverse transform the prediction back to the original scale
#     next_prediction = scaler_y.inverse_transform(next_prediction_scaled)
    
#     # Store the forecasted value
#     forecasted_values.append(next_prediction[0][0])
    
#     # Update the last_input with the predicted value for the next iteration
#     last_input = np.roll(last_input, -1)
#     last_input[0, -1] = next_prediction_scaled[0][0]  # Replace with the predicted value

# # Convert forecasted values to a 2D array for consistent dimensions with predictions
# forecasted_values = np.array(forecasted_values).reshape(-1, 1)

# # ====== Plotting Phase with Tooltips ======

# # Set dark mode style for the plot
# plt.style.use('dark_background')

# # Create the figure and axis
# fig, ax = plt.subplots(figsize=(14, 5))

# # Customize the axis colors for dark mode
# ax.set_facecolor('black')
# ax.xaxis.label.set_color('white')
# ax.yaxis.label.set_color('white')
# ax.tick_params(axis='x', colors='white')
# ax.tick_params(axis='y', colors='white')

# # Use integer x-axis values instead of dates
# x_train = np.arange(len(y_train_actual))
# x_test = np.arange(len(y_train_actual), len(y_train_actual) + len(y_test_actual))
# x_forecast = np.arange(len(y_actual), len(y_actual) + forecast_days)  # Start forecast right after y_actual

# # Plot the actual data with glowing dark cyan color and thin lines
# line_actual, = ax.plot(np.concatenate((x_train, x_test)), y_actual, color='#00FFFF', marker='o', label='Actual Data (Train + Test)', markersize=3, linewidth=0.8)

# # Plot the LSTM predictions as a dotted line
# line_predictions, = ax.plot(np.concatenate((x_train, x_test)), predictions, color='#FF4500', linestyle='--', linewidth=1, label='LSTM Predictions')

# # Plot the forecasted values as a bright red thin line with data points
# line_forecast, = ax.plot(np.arange(len(y_actual), len(y_actual) + forecast_days), forecasted_values, color='red', linestyle='-', marker='o', markersize=3, linewidth=1, label='15-Day Forecast')

# # Add a thin black solid line for the train/test split
# ax.axvline(x=len(x_train), color='white', linestyle='-', linewidth=1)
# ax.text(len(x_train), ax.get_ylim()[1] * 0.98, 'Train/Test Split', rotation=90, verticalalignment='top',
#         horizontalalignment='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.4'), color='black', fontsize=8)

# # Add a thin black solid line for the start of the forecast
# ax.axvline(x=len(x_train) + len(x_test), color='white', linestyle='-', linewidth=1)
# ax.text(len(x_train) + len(x_test), ax.get_ylim()[1] * 0.98, 'Forecast Start', rotation=90, verticalalignment='top',
#         horizontalalignment='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.4'), color='black', fontsize=8)

# # Add title and labels
# ax.set_title(f"Entire Dairy Herd Activity Model | Train Data Prediction Accuracy: {train_accuracy:.2f}% | Test Data Prediction Accuracy: {test_accuracy:.2f}% | 15-Day Forecast", color='white')
# ax.set_xlabel('Time (Days)', color='white')
# ax.set_ylabel('Activity (Scaled)', color='white')

# # Format x-axis as integers
# ax.set_xticks(np.arange(0, len(y_actual) + forecast_days, 10))

# # Legend with white text
# ax.legend(facecolor='black', edgecolor='white', fontsize=10, labelcolor='white')

# # Initialize tooltip (AnnotationBbox)
# tooltip = None

# # Keep track of the previous tooltip
# previous_tooltip = None

# def on_plot_hover(event):
#     global previous_tooltip
    
#     # Clear the previous tooltip if it exists
#     if previous_tooltip:
#         previous_tooltip.remove()
#         previous_tooltip = None

#     for curve in [line_actual, line_predictions, line_forecast]:
#         if curve.contains(event)[0]:
#             if curve == line_actual:
#                 label = "Actual Data (Train + Test)"
#                 ind = np.argmin(np.abs(np.concatenate((x_train, x_test)) - event.xdata))
#                 activity_value = float(y_actual[ind])  # Extract scalar from array
#                 text = f"{label}\nTime Step: {ind}\nActivity: {activity_value:.2f}"
#             elif curve == line_predictions:
#                 label = "LSTM Predictions"
#                 ind = np.argmin(np.abs(np.concatenate((x_train, x_test)) - event.xdata))
#                 predicted_value = float(predictions[ind])  # Extract scalar from array
#                 text = f"{label}\nTime Step: {ind}\nPredicted Activity: {predicted_value:.2f}"
#             elif curve == line_forecast:
#                 label = "15-Day Forecast"
#                 ind = np.argmin(np.abs(x_forecast - event.xdata))
#                 forecasted_value = float(forecasted_values[ind])  # Extract scalar from array
#                 text = f"{label}\nForecast Day: {x_forecast[ind]}\nForecasted Activity: {forecasted_value:.2f}"
#             else:
#                 continue

#             # Create the annotation box with the tooltip text and an arrow
#             tooltip_text = TextArea(text, textprops=dict(color="black", size=6))
#             tooltip = AnnotationBbox(
#                 tooltip_text,
#                 (event.xdata, event.ydata),
#                 xybox=(35., 35.),
#                 xycoords='data',
#                 boxcoords="offset points",
#                 arrowprops=dict(arrowstyle="->", color='white'),
#                 bboxprops=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2')
#             )
#             ax.add_artist(tooltip)
#             previous_tooltip = tooltip
#             fig.canvas.draw_idle()
#             break

# # Connect the hover event to the figure
# fig.canvas.mpl_connect("motion_notify_event", on_plot_hover)

# # Show the plot with dark mode settings and tooltips
# plt.show()

# import os
# import pandas as pd
# import numpy as np
# from sklearn.preprocessing import MinMaxScaler
# from keras.models import Sequential
# from keras.layers import LSTM, Dense
# import joblib
# import matplotlib.pyplot as plt
# from matplotlib.offsetbox import AnnotationBbox, TextArea

# # Create the directory for saving the model and scalers if it doesn't exist
# model_dir = 'Dairy Herd Temperature Model'
# if not os.path.exists(model_dir):
#     os.makedirs(model_dir)

# # ====== Training Phase ======

# # Load the temperature dataset
# file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/trialTemperature.csv'  # Update this path if necessary
# data = pd.read_csv(file_path)

# # Rename the columns for easier access
# data.columns = ['Date'] + [f'Feature_{i}' for i in range(1, 29)] + ['Temperature']

# # Convert 'Date' column to datetime
# data['Date'] = pd.to_datetime(data['Date'])

# # Define features and target
# X = data.drop(['Date', 'Temperature'], axis=1).values
# y = data['Temperature'].values
# dates = data['Date'].values  # Store dates for later, though x-axis will use integers

# # Feature scaling using MinMaxScaler
# scaler_X = MinMaxScaler(feature_range=(0, 1))
# scaler_y = MinMaxScaler(feature_range=(0, 1))

# X_scaled = scaler_X.fit_transform(X)
# y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

# # Reshape input to be 3D for LSTM [samples, time steps, features]
# X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

# # Split the data into training and testing sets (80% train, 20% test)
# split_index = int(X_scaled.shape[0] * 0.8)
# X_train, X_test = X_scaled[:split_index], X_scaled[split_index:]
# y_train, y_test = y_scaled[:split_index], y_scaled[split_index:]

# # Build the LSTM model
# model = Sequential()
# model.add(LSTM(50, return_sequences=True, input_shape=(1, X_train.shape[2])))
# model.add(LSTM(50, return_sequences=False))
# model.add(Dense(25))
# model.add(Dense(1))

# # Compile the model
# model.compile(optimizer='adam', loss='mean_squared_error')

# # Train the model on the training dataset
# model.fit(X_train, y_train, batch_size=1, epochs=50)

# # Save the trained model and scalers in the 'Dairy Herd Temperature Model' folder
# model.save(os.path.join(model_dir, 'lstm_temperature_model.keras'))  # Using the recommended keras format
# joblib.dump(scaler_X, os.path.join(model_dir, 'scaler_X.pkl'))
# joblib.dump(scaler_y, os.path.join(model_dir, 'scaler_y.pkl'))

# # Make predictions on both the training and testing sets
# train_predictions_scaled = model.predict(X_train)
# test_predictions_scaled = model.predict(X_test)

# # Inverse transform the predictions and actual values to get them back to the original scale
# train_predictions = scaler_y.inverse_transform(train_predictions_scaled)
# test_predictions = scaler_y.inverse_transform(test_predictions_scaled)
# y_train_actual = scaler_y.inverse_transform(y_train)
# y_test_actual = scaler_y.inverse_transform(y_test)

# # Combine actual and predicted values for continuous plotting
# y_actual = np.concatenate((y_train_actual, y_test_actual), axis=0)
# predictions = np.concatenate((train_predictions, test_predictions), axis=0)

# # Calculate accuracy using Mean Absolute Percentage Error (MAPE)
# train_accuracy = 100 - np.mean(np.abs((y_train_actual - train_predictions) / y_train_actual)) * 100
# test_accuracy = 100 - np.mean(np.abs((y_test_actual - test_predictions) / y_test_actual)) * 100

# # ====== Forecasting Phase ======

# # Number of days to forecast
# forecast_days = 15

# # Get the last data point from the test set as the starting point for forecasting
# last_input = X_test[-1]

# # Create a list to store the forecasted values
# forecasted_values = []

# # Forecast for the next 15 days
# for day in range(forecast_days):
#     # Predict the next day's value
#     next_prediction_scaled = model.predict(last_input.reshape(1, 1, -1))
    
#     # Inverse transform the prediction back to the original scale
#     next_prediction = scaler_y.inverse_transform(next_prediction_scaled)
    
#     # Store the forecasted value
#     forecasted_values.append(next_prediction[0][0])
    
#     # Update the last_input with the predicted value for the next iteration
#     last_input = np.roll(last_input, -1)
#     last_input[0, -1] = next_prediction_scaled[0][0]  # Replace with the predicted value

# # Convert forecasted values to a 2D array for consistent dimensions with predictions
# forecasted_values = np.array(forecasted_values).reshape(-1, 1)

# # ====== Plotting Phase with Tooltips ======

# # Set dark mode style for the plot
# plt.style.use('dark_background')

# # Create the figure and axis
# fig, ax = plt.subplots(figsize=(14, 5))

# # Customize the axis colors for dark mode
# ax.set_facecolor('black')
# ax.xaxis.label.set_color('white')
# ax.yaxis.label.set_color('white')
# ax.tick_params(axis='x', colors='white')
# ax.tick_params(axis='y', colors='white')

# # Use integer x-axis values instead of dates
# x_train = np.arange(len(y_train_actual))
# x_test = np.arange(len(y_train_actual), len(y_train_actual) + len(y_test_actual))
# x_forecast = np.arange(len(y_actual), len(y_actual) + forecast_days)

# # Plot the actual data with glowing dark cyan color and thin lines
# line_actual, = ax.plot(np.concatenate((x_train, x_test)), y_actual, color='#00FFFF', marker='o', label='Actual Data (Train + Test)', markersize=3, linewidth=0.8)

# # Plot the LSTM predictions as a dotted line
# line_predictions, = ax.plot(np.concatenate((x_train, x_test)), predictions, color='#FF4500', linestyle='--', linewidth=1, label='LSTM Predictions')

# # Plot the forecasted values as a bright red thin line with data points
# line_forecast, = ax.plot(x_forecast, forecasted_values, color='red', linestyle='-', marker='o', markersize=3, linewidth=1, label='15-Day Forecast')

# # Add a thin black solid line for the train/test split
# ax.axvline(x=len(x_train), color='white', linestyle='-', linewidth=1)
# ax.text(len(x_train), ax.get_ylim()[1] * 0.98, 'Train/Test Split', rotation=90, verticalalignment='top',
#         horizontalalignment='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.4'), color='black', fontsize=8)

# # Add a thin black solid line for the start of the forecast
# ax.axvline(x=len(x_train) + len(x_test), color='white', linestyle='-', linewidth=1)
# ax.text(len(x_train) + len(x_test), ax.get_ylim()[1] * 0.98, 'Forecast Start', rotation=90, verticalalignment='top',
#         horizontalalignment='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.4'), color='black', fontsize=8)

# # Add title and labels
# ax.set_title(f"Entire Dairy Herd Temperature Model | Train Data Prediction Accuracy: {train_accuracy:.2f}% | Test Data Prediction Accuracy: {test_accuracy:.2f}% | 15-Day Forecast", color='white')
# ax.set_xlabel('Time (Days)', color='white')
# ax.set_ylabel('Temperature', color='white')

# # Format x-axis as integers
# ax.set_xticks(np.arange(0, len(y_actual) + forecast_days, 10))

# # Legend with white text
# ax.legend(facecolor='black', edgecolor='white', fontsize=10, labelcolor='white')

# # Initialize tooltip (AnnotationBbox)
# tooltip = None

# # Keep track of the previous tooltip
# previous_tooltip = None

# def on_plot_hover(event):
#     global previous_tooltip
    
#     # Clear the previous tooltip if it exists
#     if previous_tooltip:
#         previous_tooltip.remove()
#         previous_tooltip = None

#     for curve in [line_actual, line_predictions, line_forecast]:
#         if curve.contains(event)[0]:
#             if curve == line_actual:
#                 label = "Actual Data (Train + Test)"
#                 ind = np.argmin(np.abs(np.concatenate((x_train, x_test)) - event.xdata))
#                 activity_value = float(y_actual[ind])  # Extract scalar from array
#                 text = f"{label}\nDate: {str(dates[ind])[:10]}\nActivity: {activity_value:.2f}"
#             elif curve == line_predictions:
#                 label = "LSTM Predictions"
#                 ind = np.argmin(np.abs(np.concatenate((x_train, x_test)) - event.xdata))
#                 predicted_value = float(predictions[ind])  # Extract scalar from array
#                 text = f"{label}\nDate: {str(dates[ind])[:10]}\nPredicted Activity: {predicted_value:.2f}"
#             elif curve == line_forecast:
#                 label = "15-Day Forecast"
#                 ind = np.argmin(np.abs(x_forecast - event.xdata))
#                 forecasted_value = float(forecasted_values[ind])  # Extract scalar from array
#                 text = f"{label}\nForecast Day: {x_forecast[ind]}\nForecasted Activity: {forecasted_value:.2f}"
#             else:
#                 continue

#             # Create the annotation box with the tooltip text and an arrow
#             tooltip_text = TextArea(text, textprops=dict(color='black', size=7))  # Ensuring black text and smaller font size
#             tooltip = AnnotationBbox(
#                 tooltip_text,
#                 (event.xdata, event.ydata),
#                 xybox=(30., 30.),  # Reduced the size of the tooltip box
#                 xycoords='data',
#                 boxcoords="offset points",
#                 arrowprops=dict(arrowstyle="->", color='white'),
#                 bboxprops=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'),
#                 zorder=10  # Ensuring tooltip is rendered on top
#             )
#             ax.add_artist(tooltip)
#             previous_tooltip = tooltip
#             fig.canvas.draw_idle()
#             break

# # Connect the hover event to the figure
# fig.canvas.mpl_connect("motion_notify_event", on_plot_hover)

# # Show the plot with dark mode settings and tooltips
# plt.show()




# //////////////////////////////////////////////////////////////////////////////



# # # # # ////////////////////////////////BEST PERFORMANCE//////////////////////////////////////////////////


# import os
# import pandas as pd
# import numpy as np
# from sklearn.preprocessing import MinMaxScaler
# from keras.models import Sequential
# from keras.layers import LSTM, Dense, Dropout
# from keras.optimizers import Adam
# import joblib
# import matplotlib.pyplot as plt
# from matplotlib.offsetbox import AnnotationBbox, TextArea

# # Create the directory for saving the model and scalers if it doesn't exist
# model_dir = 'Cow_6774_Model'
# if not os.path.exists(model_dir):
#     os.makedirs(model_dir)

# # ====== Data Preprocessing Phase with Lag Features and Rolling Windows ======

# # Load the dataset
# file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'  # Update this path if necessary
# data = pd.read_csv(file_path)

# # Drop non-numeric columns if present
# if 'Unnamed: 0' in data.columns:
#     data = data.drop('Unnamed: 0', axis=1)
# if 'Date' in data.columns:
#     data = data.drop('Date', axis=1)

# # Ensure all data is numeric and drop rows with missing values
# data_cleaned = data.apply(pd.to_numeric, errors='coerce').fillna(method='ffill')  # Forward fill missing values

# # Create lag features for the '6774' column and others without dropping initial rows
# def create_lagged_features(df, lag=2):
#     df_lagged = df.copy()
#     for col in df.columns:
#         for i in range(1, lag + 1):
#             df_lagged[f'{col}_lag{i}'] = df[col].shift(i, fill_value=df[col].iloc[0])  # Shift with padding
#     return df_lagged

# # Apply lag features and fill NaNs with the first available value
# lag = 2  # Reduced lag to avoid dropping too many initial data points
# data_lagged = create_lagged_features(data_cleaned, lag=lag)

# # Apply rolling window on the '6774' column (e.g., 3-day rolling mean) with minimal data loss
# data_lagged['6774_rolling'] = data_lagged['6774'].rolling(window=3, min_periods=1).mean()

# # Define features and target
# X = data_lagged.drop('6774', axis=1).values
# y = data_lagged['6774'].values

# # Feature scaling using MinMaxScaler
# scaler_X = MinMaxScaler(feature_range=(0, 1))
# scaler_y = MinMaxScaler(feature_range=(0, 1))

# X_scaled = scaler_X.fit_transform(X)
# y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

# # Reshape input to be 3D for LSTM [samples, time steps, features]
# X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

# # Split data into training and testing sets (80% train, 20% test)
# train_size = int(len(X_scaled) * 0.8)
# X_train, X_test = X_scaled[:train_size], X_scaled[train_size:]
# y_train, y_test = y_scaled[:train_size], y_scaled[train_size:]

# # ====== Model Training Phase ======

# # Build the LSTM model with dropout and LSTM layers
# model = Sequential()
# model.add(LSTM(150, return_sequences=True, input_shape=(1, X_train.shape[2])))
# model.add(Dropout(0.3))
# model.add(LSTM(150, return_sequences=False))
# model.add(Dropout(0.3))
# model.add(Dense(50))
# model.add(Dense(1))

# # Compile the model with Adam optimizer and a lower learning rate
# optimizer = Adam(learning_rate=0.0005)
# model.compile(optimizer=optimizer, loss='mean_squared_error')

# # Train the model with more epochs and smaller batch size
# model.fit(X_train, y_train, batch_size=4, epochs=200, verbose=1)

# # Save the trained model
# model.save(os.path.join(model_dir, 'lstm_model_6774_lagged.keras'))

# # Save the scalers for future use
# joblib.dump(scaler_X, os.path.join(model_dir, 'scaler_X_6774_lagged.pkl'))
# joblib.dump(scaler_y, os.path.join(model_dir, 'scaler_y_6774_lagged.pkl'))

# # ====== Prediction Phase ======

# # Make predictions on both the training and testing datasets
# train_predictions_scaled = model.predict(X_train)
# test_predictions_scaled = model.predict(X_test)

# # Inverse transform the predictions to get them back to the original scale
# train_predictions = scaler_y.inverse_transform(train_predictions_scaled)
# test_predictions = scaler_y.inverse_transform(test_predictions_scaled)
# y_train_actual = scaler_y.inverse_transform(y_train)
# y_test_actual = scaler_y.inverse_transform(y_test)

# # Combine predictions and actual values for continuous plotting
# combined_predictions = np.concatenate((train_predictions, test_predictions), axis=0)
# combined_actual = np.concatenate((y_train_actual, y_test_actual), axis=0)

# # Calculate accuracy using Mean Absolute Percentage Error (MAPE)
# train_accuracy = 100 - np.mean(np.abs((y_train_actual - train_predictions) / y_train_actual)) * 100
# test_accuracy = 100 - np.mean(np.abs((y_test_actual - test_predictions) / y_test_actual)) * 100

# # ====== Forecasting Phase ======

# # Number of days to forecast
# forecast_days = 15

# # Get the last data point from the test set as the starting point for forecasting
# last_input = X_test[-1]

# # Create a list to store the forecasted values
# forecasted_values = []

# # Forecast for the next 15 days
# for day in range(forecast_days):
#     # Predict the next day's value
#     next_prediction_scaled = model.predict(last_input.reshape(1, 1, -1))
    
#     # Inverse transform the prediction back to the original scale
#     next_prediction = scaler_y.inverse_transform(next_prediction_scaled)
    
#     # Store the forecasted value
#     forecasted_values.append(next_prediction[0][0])
    
#     # Update the last_input with the predicted value for the next iteration
#     last_input = np.roll(last_input, -1)
#     last_input[0, -1] = next_prediction_scaled[0][0]  # Replace with the predicted value

# # Convert forecasted values to a 2D array for consistent dimensions with predictions
# forecasted_values = np.array(forecasted_values).reshape(-1, 1)

# # ====== Plotting Phase with Tooltips ======

# # Set dark mode style for the plot
# plt.style.use('dark_background')

# # Create the figure and axis
# fig, ax = plt.subplots(figsize=(14, 5))

# # Customize the axis colors for dark mode
# ax.set_facecolor('black')
# ax.xaxis.label.set_color('white')
# ax.yaxis.label.set_color('white')
# ax.tick_params(axis='x', colors='white')
# ax.tick_params(axis='y', colors='white')

# # Use integer x-axis values instead of dates
# x_train = np.arange(len(y_train_actual))
# x_test = np.arange(len(y_train_actual), len(y_train_actual) + len(y_test_actual))
# x_forecast = np.arange(len(combined_actual), len(combined_actual) + forecast_days)

# # Plot the actual data with glowing dark cyan color and thin lines
# line_actual, = ax.plot(np.concatenate((x_train, x_test)), combined_actual, color='#00FFFF', marker='o', label='Actual Data (Train + Test)', markersize=3, linewidth=0.8)

# # Plot the LSTM predictions as a dotted line
# line_predictions, = ax.plot(np.concatenate((x_train, x_test)), combined_predictions, color='#FF4500', linestyle='--', linewidth=1, label='LSTM Predictions')

# # Plot the forecasted values as a bright red thin line with data points
# line_forecast, = ax.plot(x_forecast, forecasted_values, color='red', linestyle='-', marker='o', markersize=3, linewidth=1, label='15-Day Forecast')

# # Add a thin black solid line for the train/test split
# ax.axvline(x=len(x_train), color='white', linestyle='-', linewidth=1)
# ax.text(len(x_train), ax.get_ylim()[1] * 0.98, 'Train/Test Split', rotation=90, verticalalignment='top',
#         horizontalalignment='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.4'), color='black', fontsize=8)

# # Add a thin black solid line for the start of the forecast
# ax.axvline(x=len(x_train) + len(x_test), color='white', linestyle='-', linewidth=1)
# ax.text(len(x_train) + len(x_test), ax.get_ylim()[1] * 0.98, 'Forecast Start', rotation=90, verticalalignment='top',
#         horizontalalignment='center', bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.4'), color='black', fontsize=8)

# # Add title and labels
# ax.set_title(f"Cow 6774 Activity Model | Train Data Prediction Accuracy: {train_accuracy:.2f}% | Test Data Prediction Accuracy: {test_accuracy:.2f}% | 15-Day Forecast", color='white')
# ax.set_xlabel('Time (Days)', color='white')
# ax.set_ylabel('Activity Level', color='white')

# # Format x-axis as integers
# ax.set_xticks(np.arange(0, len(combined_actual) + forecast_days, 10))

# # Legend with white text
# ax.legend(facecolor='black', edgecolor='white', fontsize=10, labelcolor='white')

# # Initialize tooltip (AnnotationBbox)
# tooltip = None

# # Keep track of the previous tooltip
# previous_tooltip = None

# def on_plot_hover(event):
#     global previous_tooltip
    
#     # Clear the previous tooltip if it exists
#     if previous_tooltip:
#         previous_tooltip.remove()
#         previous_tooltip = None

#     # Check for proximity to actual data points (this will limit tooltips to the vicinity of markers)
#     for curve in [line_actual, line_predictions, line_forecast]:
#         if curve.contains(event)[0]:
#             # Find the index of the nearest data point
#             if curve == line_actual:
#                 label = "Actual Data (Train + Test)"
#                 ind = np.argmin(np.abs(np.concatenate((x_train, x_test)) - event.xdata))
#                 activity_value = float(combined_actual[ind])  # Extract scalar from array
#                 text = f"{label}\nActivity: {activity_value:.2f}"
#             elif curve == line_predictions:
#                 label = "LSTM Predictions"
#                 ind = np.argmin(np.abs(np.concatenate((x_train, x_test)) - event.xdata))
#                 predicted_value = float(combined_predictions[ind])  # Extract scalar from array
#                 text = f"{label}\nPredicted Activity: {predicted_value:.2f}"
#             elif curve == line_forecast:
#                 label = "15-Day Forecast"
#                 ind = np.argmin(np.abs(x_forecast - event.xdata))
#                 forecasted_value = float(forecasted_values[ind])  # Extract scalar from array
#                 text = f"{label}\nForecast Day: {x_forecast[ind]}\nForecasted Activity: {forecasted_value:.2f}"
#             else:
#                 continue

#             # Create the annotation box with the tooltip text and an arrow
#             tooltip_text = TextArea(text, textprops=dict(color="black", size=6))  # Reduce text size by 30%
#             tooltip = AnnotationBbox(
#                 tooltip_text,
#                 (event.xdata, event.ydata),
#                 xybox=(35., 35.),  # Offset the tooltip
#                 xycoords='data',
#                 boxcoords="offset points",
#                 arrowprops=dict(arrowstyle="->", color='white'),
#                 bboxprops=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2')  # Ensure white background and reduced padding
#             )
#             ax.add_artist(tooltip)
#             previous_tooltip = tooltip
#             fig.canvas.draw_idle()
#             break


# # Connect the hover event to the figure
# fig.canvas.mpl_connect("motion_notify_event", on_plot_hover)

# # Show the plot
# plt.show()



# # //////////////////////////////////////////////////////EXTREMELY VALUABLE///////////////////////////////////////////////////////////////////////////////

# import os
# import pandas as pd
# import numpy as np
# from sklearn.preprocessing import MinMaxScaler
# from keras.models import Sequential, load_model
# from keras.layers import LSTM, Dense, Dropout
# from keras.optimizers import Adam
# import joblib
# import matplotlib.pyplot as plt

# # Set up the model directory
# model_dir = 'Activity_Model'
# model_file = os.path.join(model_dir, 'lstm_model_combined_cows.keras')
# scaler_X_file = os.path.join(model_dir, 'scaler_X_combined_cows.pkl')
# scaler_y_file = os.path.join(model_dir, 'scaler_y_combined_cows.pkl')

# # Create the directory for saving the model and scalers if it doesn't exist
# if not os.path.exists(model_dir):
#     os.makedirs(model_dir)

# # ====== Data Preprocessing Phase ======

# # Load the dataset
# file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'
# data = pd.read_csv(file_path)

# # Drop non-numeric columns if present
# if 'Unnamed: 0' in data.columns:
#     data = data.drop('Unnamed: 0', axis=1)
# if 'Date' in data.columns:
#     data = data.drop('Date', axis=1)

# # Ensure all data is numeric and fill missing values
# data_cleaned = data.apply(pd.to_numeric, errors='coerce').fillna(method='ffill')

# # Filter out the columns for cows 6774 to 6834
# cow_columns = [str(i) for i in range(6774, 6835) if str(i) in data_cleaned.columns]

# # Create lag features for all cow columns
# def create_lagged_features(df, lag=2):
#     df_lagged = df.copy()
#     for col in df.columns:
#         for i in range(1, lag + 1):
#             df_lagged[f'{col}_lag{i}'] = df[col].shift(i, fill_value=df[col].iloc[0])  # Shift with padding
#     return df_lagged

# # Apply lag features and fill NaNs with the first available value
# lag = 2  # Adjust lag as needed
# data_lagged = create_lagged_features(data_cleaned[cow_columns], lag=lag)

# # Prepare data for the entire herd
# def prepare_data_for_herd():
#     X = data_lagged.values  # Use all cows as features
#     y = data_lagged.sum(axis=1).values  # Sum across all cows for each day to get the total herd movement
#     return X, y

# # ====== Model Training and Loading ======

# def build_model(input_shape):
#     # Build the LSTM model with dropout and LSTM layers
#     model = Sequential()
#     model.add(LSTM(150, return_sequences=True, input_shape=input_shape))
#     model.add(Dropout(0.3))
#     model.add(LSTM(150, return_sequences=False))
#     model.add(Dropout(0.3))
#     model.add(Dense(50))
#     model.add(Dense(1))  # Predict a single target (can be individual cow or herd movement)
#     return model

# def load_or_train_model(X_train, y_train, scaler_X, scaler_y):
#     # Check if a pre-trained model exists
#     if os.path.exists(model_file) and os.path.exists(scaler_X_file) and os.path.exists(scaler_y_file):
#         # Load the existing model and scalers
#         model = load_model(model_file)
#         print("Loaded existing model and scalers.")
#     else:
#         # Build and train a new model if no saved model exists
#         print("Training a new model...")
#         model = build_model((1, X_train.shape[2]))
        
#         # Compile the model with Adam optimizer and a lower learning rate
#         optimizer = Adam(learning_rate=0.0005)
#         model.compile(optimizer=optimizer, loss='mean_squared_error')

#         # Train the model
#         model.fit(X_train, y_train, batch_size=4, epochs=200, verbose=1)

#         # Save the trained model and scalers
#         model.save(model_file)
#         joblib.dump(scaler_X, scaler_X_file)
#         joblib.dump(scaler_y, scaler_y_file)
#         print("Model and scalers saved.")

#     return model

# # Function to plot continuous actual vs predicted data for both train and test sets
# def plot_continuous_predictions(y_actual, predictions, title):
#     fig, ax = plt.subplots(figsize=(14, 5))

#     # Plot actual vs predictions as continuous lines
#     ax.plot(np.arange(len(y_actual)), y_actual, label='Actual Data', color='blue')
#     ax.plot(np.arange(len(predictions)), predictions, label='LSTM Predictions', linestyle='--', color='red')

#     # Add labels and title
#     ax.set_title(title)
#     ax.set_xlabel('Time (Days)')
#     ax.set_ylabel('Activity Level')

#     # Add a legend
#     ax.legend()

#     # Show the plot
#     plt.show()

# # ====== Model Training and Prediction ======

# # Prepare data for the entire herd (used for training the model)
# X, y = prepare_data_for_herd()

# # Scale and reshape the data for LSTM
# scaler_X = MinMaxScaler(feature_range=(0, 1))
# scaler_y = MinMaxScaler(feature_range=(0, 1))

# X_scaled = scaler_X.fit_transform(X)
# y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

# # Reshape input to be 3D for LSTM [samples, time steps, features]
# X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

# # Split data into training and testing sets (80% train, 20% test)
# train_size = int(len(X_scaled) * 0.8)
# X_train, X_test = X_scaled[:train_size], X_scaled[train_size:]
# y_train, y_test = y_scaled[:train_size], y_scaled[train_size:]

# # Load or train the model
# model = load_or_train_model(X_train, y_train, scaler_X, scaler_y)

# # Make predictions on both the training and testing datasets for the herd
# train_predictions_scaled = model.predict(X_train)
# test_predictions_scaled = model.predict(X_test)

# # Inverse transform the predictions to get them back to the original scale
# train_predictions = scaler_y.inverse_transform(train_predictions_scaled)
# test_predictions = scaler_y.inverse_transform(test_predictions_scaled)
# y_train_actual = scaler_y.inverse_transform(y_train)
# y_test_actual = scaler_y.inverse_transform(y_test)

# # Ask user if they want individual cow or herd movement predictions
# response = input("Would you like to see the activity for an individual cow or the entire herd? Type 'cow' for individual cow or 'herd' for entire herd: ")

# if response.lower() == 'cow':
#     # Ask for the cow ID
#     cow_id = input("Enter the cow ID (e.g., 6774): ")
    
#     # Prepare data for the selected cow
#     def prepare_data_for_cow(cow_id):
#         X = data_lagged.values  # Use all cows as features
#         y = data_lagged[str(cow_id)].values  # Target is the selected cow's activity
#         return X, y

#     X_cow, y_cow = prepare_data_for_cow(cow_id)
    
#     # Scale and reshape the data for LSTM
#     scaler_X_cow = MinMaxScaler(feature_range=(0, 1))
#     scaler_y_cow = MinMaxScaler(feature_range=(0, 1))
    
#     X_scaled_cow = scaler_X_cow.fit_transform(X_cow)
#     y_scaled_cow = scaler_y_cow.fit_transform(y_cow.reshape(-1, 1))

#     X_scaled_cow = X_scaled_cow.reshape((X_scaled_cow.shape[0], 1, X_scaled_cow.shape[1]))
    
#     # Split data into training and testing sets (80% train, 20% test)
#     train_size_cow = int(len(X_scaled_cow) * 0.8)
#     X_train_cow, X_test_cow = X_scaled_cow[:train_size_cow], X_scaled_cow[train_size_cow:]
#     y_train_cow, y_test_cow = y_scaled_cow[:train_size_cow], y_scaled_cow[train_size_cow:]

#     # Make predictions for the selected cow
#     train_predictions_cow_scaled = model.predict(X_train_cow)
#     test_predictions_cow_scaled = model.predict(X_test_cow)

#     # Inverse transform the predictions to get them back to the original scale
#     train_predictions_cow = scaler_y_cow.inverse_transform(train_predictions_cow_scaled)
#     test_predictions_cow = scaler_y_cow.inverse_transform(test_predictions_cow_scaled)
#     y_train_actual_cow = scaler_y_cow.inverse_transform(y_train_cow)
#     y_test_actual_cow = scaler_y_cow.inverse_transform(y_test_cow)

#     # Concatenate the train and test predictions for continuous plotting
#     all_predictions_cow = np.concatenate((train_predictions_cow, test_predictions_cow), axis=0)
#     all_actual_cow = np.concatenate((y_train_actual_cow, y_test_actual_cow), axis=0)

#     # Plot the results for the selected cow
#     plot_continuous_predictions(all_actual_cow, all_predictions_cow, f'Cow {cow_id} Actual Data vs LSTM Predictions (Continuous)')

# elif response.lower() == 'herd':
#     # Concatenate the train and test predictions for continuous plotting
#     all_predictions = np.concatenate((train_predictions, test_predictions), axis=0)
#     all_actual = np.concatenate((y_train_actual, y_test_actual), axis=0)

#     # Plot the results for the herd
#     plot_continuous_predictions(all_actual, all_predictions, 'Herd Actual Data vs LSTM Predictions (Continuous)')

# else:
#     print("Invalid input. Please type 'cow' or 'herd'.")





# # import pandas as pd
# # import numpy as np
# # from sklearn.preprocessing import MinMaxScaler
# # from sklearn.model_selection import train_test_split
# # from sklearn.metrics import r2_score, mean_squared_error
# # import matplotlib.pyplot as plt
# # from tensorflow.keras.models import Sequential
# # from tensorflow.keras.layers import LSTM, Dense

# # # Load the data
# # data = pd.read_csv('C:/Users/Jyothesh karnam/Desktop/Trial/trialActivity.csv')
# # data['Date'] = pd.to_datetime(data['Unnamed: 0'])
# # data.set_index('Date', inplace=True)

# # # Select the '6774' column
# # df = data[['6774']]

# # # Normalize the data
# # scaler = MinMaxScaler()
# # df_scaled = scaler.fit_transform(df)

# # # Prepare the dataset for LSTM
# # X, y = [], []
# # timesteps = 5  # Number of previous time steps to use as input
# # for i in range(timesteps, len(df_scaled)):
# #     X.append(df_scaled[i-timesteps:i, 0])
# #     y.append(df_scaled[i, 0])
# # X, y = np.array(X), np.array(y)
# # X = X.reshape((X.shape[0], X.shape[1], 1))

# # # Split the data into training and testing sets
# # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# # # Build the LSTM model
# # model = Sequential()
# # model.add(LSTM(50, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])))
# # model.add(Dense(1))
# # model.compile(optimizer='adam', loss='mse')

# # # Train the model
# # model.fit(X_train, y_train, epochs=50, batch_size=1, verbose=1, validation_data=(X_test, y_test))

# # # Predict on the test set
# # y_pred = model.predict(X_test)

# # # Inverse scaling to get the original values
# # y_pred_inv = scaler.inverse_transform(y_pred)
# # y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1))

# # # Calculate R-squared score for model accuracy
# # r2 = r2_score(y_test_inv, y_pred_inv)
# # accuracy_percentage = r2 * 100

# # print(f'R² Score: {r2:.2f}')
# # print(f'Accuracy: {accuracy_percentage:.2f}%')

# # # Prepare the training set to plot on the same graph
# # y_train_pred = model.predict(X_train)
# # y_train_inv = scaler.inverse_transform(y_train_pred)

# # # Plot the results
# # plt.figure(figsize=(14, 7))
# # plt.plot(range(len(y_train_inv)), y_train_inv, label='Training Data', color='blue')
# # plt.plot(range(len(y_train_inv), len(y_train_inv) + len(y_test_inv)), y_test_inv, label='Test Data', color='green')
# # plt.plot(range(len(y_train_inv), len(y_train_inv) + len(y_test_inv)), y_pred_inv, label='LSTM Predictions', color='orange')
# # plt.legend()
# # plt.title(f'LSTM Model: Train Data, Test Data, and Predictions\nAccuracy: {accuracy_percentage:.2f}%')
# # plt.xlabel('Time')
# # plt.ylabel('6774 Activity')
# # plt.show()




# import pandas as pd
# import numpy as np
# import os
# from sklearn.preprocessing import MinMaxScaler
# from sklearn.metrics import r2_score, mean_squared_error
# import matplotlib.pyplot as plt
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import LSTM, Dense, Dropout
# from tensorflow.keras.optimizers import RMSprop

# # Section 1: Data Preprocessing
# def load_data(file_path):
#     try:
#         data = pd.read_csv(file_path, encoding='utf-8')
#     except UnicodeDecodeError:
#         data = pd.read_csv(file_path, encoding='ISO-8859-1')
#     print(f"\nStep 1: Data Collection and Integration - Loaded data from {file_path}.\n")
#     return data

# def handle_missing_values(df):
#     actions_taken = []
#     if df.isnull().sum().sum() == 0:
#         actions_taken.append("No missing values found. No need for spline interpolation.")
#     else:
#         missing_percentage = df.isnull().mean() * 100
#         if missing_percentage.max() > 30:
#             actions_taken.append("Columns with more than 30% missing values found. Consider removing these columns.")
#         for col in df.columns:
#             if df[col].isnull().sum() > 0:
#                 if df[col].dtype in ['float64', 'int64']:
#                     df[col].fillna(df[col].interpolate(method='spline', order=3), inplace=True)
#                     actions_taken.append(f"Interpolated missing values in column '{col}'.")
#     return df, actions_taken

# def remove_duplicates(df):
#     initial_row_count = df.shape[0]
#     df.drop_duplicates(inplace=True)
#     final_row_count = df.shape[0]
#     return df, initial_row_count - final_row_count

# def identify_and_handle_outliers(df):
#     actions_taken = []
#     numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
#     z_scores = (df[numeric_cols] - df[numeric_cols].mean()) / df[numeric_cols].std()
#     outliers = (z_scores.abs() > 3)
#     for col in numeric_cols:
#         num_outliers = outliers[col].sum()
#         if num_outliers > 0:
#             median_value = df[col].median()
#             df.loc[outliers[col], col] = median_value.astype(df[col].dtype)
#             actions_taken.append(f"Capped {num_outliers} outliers in column '{col}' to median value.")
#     return df, actions_taken

# def apply_normalization(df):
#     numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
#     scaler = MinMaxScaler()
#     df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
#     scaling_action = "Applied MinMaxScaler for normalization."
#     return df, scaling_action, scaler

# # Function to process activity data
# def preprocess_activity_data(file_path, output_folder):
#     # Step 1: Load Data
#     data = load_data(file_path)

#     print("\n")

#     # Ensure the first cell of the first column is labeled 'date'
#     if data.columns[0] == '' or pd.isna(data.columns[0]):
#         data.columns = ['date'] + data.columns[1:].tolist()
#     else:
#         data.columns = ['date'] + data.columns[1:].tolist() if data.columns[0] != 'date' else data.columns

#     # Ensure column names are stripped of leading/trailing spaces
#     data.columns = data.columns.str.strip()

#     # Step 2: Data Cleaning
#     # Handle missing values
#     data, missing_actions = handle_missing_values(data)
#     print("Step 2: Data Cleaning - Missing Values")
#     for action in missing_actions:
#         print(action)

#     print("\n")

#     # Remove duplicates
#     data, num_duplicates_removed = remove_duplicates(data)
#     print(f"Removed {num_duplicates_removed} duplicate rows.")

#     print("\n")

#     # Identify and handle outliers
#     data, outlier_actions = identify_and_handle_outliers(data)
#     print("Step 2: Data Cleaning - Outliers")
#     for action in outlier_actions:
#         print(action)

#     print("\n\n")

#     # Step 3: Data Transformation
#     data_transformed, scaling_action, scaler = apply_normalization(data)
#     print("Step 3: Data Transformation")
#     print(scaling_action)

#     print("\n\n")

#     # Display final DataFrame
#     print("Final DataFrame preview:")
#     print(data_transformed.head().to_string(index=False))

#     print("\n\n")

#     # Save the cleaned and transformed data
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)
#         print(f"Created folder: {output_folder}")
    
#     output_filename = 'preprocessed_activity_data.csv'
#     output_path = os.path.join(output_folder, output_filename)
#     if os.path.exists(output_path):
#         os.remove(output_path)
#         print(f"Deleted existing file: {output_path}")
#     data_transformed.to_csv(output_path, index=False)
#     print(f"Processed file saved at: {output_path}")

#     print("\n\n" + "-"*50 + "\n\n")
#     return output_path, scaler

# # Section 2: Time Series Formatting
# def determine_dynamic_sequence_length(data, min_proportion=0.1, max_proportion=0.5, min_length=5, max_length=30):
#     data_length = len(data)
#     sequence_length = int(np.sqrt(data_length))
#     dynamic_min_length = max(min_length, int(data_length * min_proportion))
#     dynamic_max_length = min(max_length, int(data_length * max_proportion))
#     sequence_length = max(dynamic_min_length, min(sequence_length, dynamic_max_length))
#     return sequence_length

# def create_activity_sequences(activity_data, sequence_length, dates):
#     X_activity = []
#     y_activity = []
#     sequence_dates = []
    
#     for i in range(len(activity_data) - sequence_length):
#         seq = activity_data.iloc[i:i + sequence_length, :].values
#         target = activity_data.iloc[i + sequence_length, :].values
#         dates_seq = dates[i:i + sequence_length]
#         X_activity.append(seq)
#         y_activity.append(target)
#         sequence_dates.append(dates_seq)
        
#     return np.array(X_activity), np.array(y_activity), sequence_dates

# # Main processing function
# def process_activity_data(file_path):
#     # Set up folder paths
#     desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
#     output_folder = os.path.join(desktop_path, "Activity data preparation")
#     final_results_folder = os.path.join(output_folder, "final results")

#     # Section 1: Data Preprocessing
#     preprocessed_data_path, scaler = preprocess_activity_data(file_path, output_folder)

#     # Load preprocessed data for further processing
#     activity_data = pd.read_csv(preprocessed_data_path)
    
#     # Section 2: Time Series Formatting
#     print("\nSection 2: Time Series Formatting")
#     dates = activity_data['date'].tolist()
#     activity_data = activity_data.drop(columns=['date'])

#     sequence_length = determine_dynamic_sequence_length(activity_data)
#     print(f"Determined sequence length for activity data: {sequence_length}")

#     X_activity, y_activity, sequence_dates = create_activity_sequences(activity_data, sequence_length, dates)

#     print(f"\nActivity data sequences: {X_activity.shape}, Targets: {y_activity.shape}")

#     # Save all results
#     os.makedirs(final_results_folder, exist_ok=True)

#     # Save preprocessed and sequence data
#     np.save(os.path.join(output_folder, 'X_activity.npy'), X_activity)
#     np.save(os.path.join(output_folder, 'y_activity.npy'), y_activity)
#     pd.DataFrame(sequence_dates).to_csv(os.path.join(output_folder, 'sequence_dates_activity.csv'), index=False, header=False)

#     print(f"\nAll results have been saved successfully in {output_folder}.")

#     return X_activity, y_activity, scaler

# # Section 4: LSTM Model Training and Evaluation
# def train_and_evaluate_lstm(X_activity, y_activity, scaler):
#     # Split the data into training and testing sets (80% train, 20% test)
#     train_size = int(len(X_activity) * 0.8)
#     X_train, X_test = X_activity[:train_size], X_activity[train_size:]
#     y_train, y_test = y_activity[:train_size], y_activity[train_size:]

#     # Build the LSTM model
#     model = Sequential()
#     model.add(LSTM(128, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=True))
#     model.add(Dropout(0.1))
#     model.add(LSTM(64, activation='relu', return_sequences=False))
#     model.add(Dense(1))
#     model.compile(optimizer=RMSprop(learning_rate=0.001), loss='mse')

#     # Train the model
#     model.fit(X_train, y_train[:, 0], epochs=300, batch_size=4, verbose=1, validation_data=(X_test, y_test[:, 0]))

#     # Predict on the test set
#     y_pred = model.predict(X_test)

#     # Inverse scaling to get the original values
#     y_pred_inv = scaler.inverse_transform(np.hstack([y_pred, np.zeros((y_pred.shape[0], y_test.shape[1] - 1))]))[:, 0]
#     y_test_inv = scaler.inverse_transform(np.hstack([y_test[:, 0].reshape(-1, 1), np.zeros((y_test.shape[0], y_test.shape[1] - 1))]))[:, 0]

#     # Calculate R-squared score for model accuracy
#     r2 = r2_score(y_test_inv, y_pred_inv)
#     accuracy_percentage = r2 * 100

#     print(f'R² Score: {r2:.2f}')
#     print(f'Accuracy: {accuracy_percentage:.2f}%')

#     # Prepare the training set to plot on the same graph
#     y_train_pred = model.predict(X_train)
#     y_train_inv = scaler.inverse_transform(np.hstack([y_train_pred, np.zeros((y_train_pred.shape[0], y_train.shape[1] - 1))]))[:, 0]

#     # Plot the results
#     plt.figure(figsize=(14, 7))
#     plt.plot(range(len(y_train_inv)), y_train_inv, label='Training Data', color='blue')
#     plt.plot(range(len(y_train_inv), len(y_train_inv) + len(y_test_inv)), y_test_inv, label='Test Data', color='green')
#     plt.plot(range(len(y_train_inv), len(y_train_inv) + len(y_test_inv)), y_pred_inv, label='LSTM Predictions', color='orange')
#     plt.legend()
#     plt.title(f'LSTM Model: Train Data, Test Data, and Predictions\nAccuracy: {accuracy_percentage:.2f}%')
#     plt.xlabel('Time')
#     plt.ylabel('Activity')
#     plt.show()

#     return model


# # Example usage
# activity_file_path = 'C:/Users/Jyothesh karnam/Desktop/Trial/TrialActivity.csv'

# # Process the data
# X_activity, y_activity, scaler = process_activity_data(activity_file_path)

# # Train and evaluate the LSTM model
# model = train_and_evaluate_lstm(X_activity, y_activity, scaler)


# //


# import numpy as np
# import pandas as pd
# from sklearn.preprocessing import MinMaxScaler
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import LSTM, Dense
# from sklearn.model_selection import train_test_split

# # Load the dataset
# file_path = 'C:/path_to_your_dataset/trialActivity.csv'
# data = pd.read_csv(file_path)

# # Extract the 'Group mean' column for comparison
# group_mean = data['Group mean'].values

# # Extract the dates for future usage
# dates = data['Unnamed: 0'].values

# # Drop the 'Group mean' and 'Unnamed: 0' (date) columns
# data_without_group_mean = data.drop(columns=['Group mean', 'Unnamed: 0'])

# # Normalize the data
# scaler = MinMaxScaler()
# data_scaled = scaler.fit_transform(data_without_group_mean)

# # Split the data into training and testing sets (80/20 split)
# train_data, test_data = train_test_split(data_scaled, test_size=0.2, shuffle=False)

# # Define the sequence length
# sequence_length = 5

# # Function to create sequences for LSTM input
# def create_sequences(data, sequence_length):
#     sequences = []
#     for i in range(len(data) - sequence_length):
#         sequence = data[i:i + sequence_length]
#         sequences.append(sequence)
#     return np.array(sequences)

# # Create sequences for training and testing data
# X_train = create_sequences(train_data, sequence_length)
# X_test = create_sequences(test_data, sequence_length)

# # Use the next time step as the target for prediction
# y_train = train_data[sequence_length:]
# y_test = test_data[sequence_length:]

# # Reshape X_train and X_test for LSTM input
# X_train = X_train.reshape((X_train.shape[0], sequence_length, X_train.shape[2]))
# X_test = X_test.reshape((X_test.shape[0], sequence_length, X_test.shape[2]))

# # Build the LSTM model
# model = Sequential([
#     LSTM(50, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])),
#     Dense(28)  # Predicting the next activity for each of the 28 cows
# ])

# # Compile the model
# model.compile(optimizer='adam', loss='mean_squared_error')

# # Train the model
# history = model.fit(X_train, y_train, epochs=50, batch_size=16, validation_data=(X_test, y_test), verbose=1)

# # Generate predictions for the entire dataset (train + test combined)
# full_data = np.vstack([train_data, test_data])
# X_full = create_sequences(full_data, sequence_length)
# predictions_full = model.predict(X_full)

# # Inverse transform the predictions to the original scale
# predictions_full_inverse = scaler.inverse_transform(predictions_full)

# # Averaging the predictions across all cows to get a single prediction line representing the entire herd
# herd_full_prediction = predictions_full_inverse.mean(axis=1)

# # Inverse transform to get actual values for the full dataset (train + test combined)
# actual_train_values = scaler.inverse_transform(train_data[sequence_length:]).mean(axis=1)
# actual_test_values = scaler.inverse_transform(test_data).mean(axis=1)

# # Combine actual values for the full dataset
# actual_values = np.concatenate([actual_train_values, actual_test_values])

# # Skip the first five rows in the Group Mean to align it with the actual and predicted values
# group_mean_adjusted = group_mean[5:]

# # Ensure the lengths match for comparison
# comparison_length = min(len(actual_values), len(herd_full_prediction), len(group_mean_adjusted))

# # Prepare the table for comparison
# comparison_table = pd.DataFrame({
#     "Date": dates[5:comparison_length+5],
#     "Actual Values": actual_values[:comparison_length],
#     "Prediction Line": herd_full_prediction[:comparison_length],
#     "Group Mean": group_mean_adjusted[:comparison_length]
# })

# # Compare which values match (either actual and group mean or actual and prediction line)
# comparison_table["Actual vs Group Mean Match"] = np.isclose(comparison_table["Actual Values"], comparison_table["Group Mean"], atol=1e-2)
# comparison_table["Actual vs Prediction Match"] = np.isclose(comparison_table["Actual Values"], comparison_table["Prediction Line"], atol=1e-2)

# # Display the comparison table
# print(comparison_table)

# # Optionally, save the table to a CSV file for further analysis
# comparison_table.to_csv('comparison_table.csv', index=False)
