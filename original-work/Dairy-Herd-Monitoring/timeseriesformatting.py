"""Reusable, import-safe activity window generation; no personal data path required."""
import argparse
import numpy as np
import pandas as pd

def determine_dynamic_sequence_length(data, min_proportion=0.1, max_proportion=0.5,
                                      min_length=5, max_length=30):
    size = len(data)
    if size < 2:
        raise ValueError('At least two observations are required for a sequence and target')
    if not 0 < min_proportion <= max_proportion < 1 or not 1 <= min_length <= max_length:
        raise ValueError('Invalid sequence bounds')
    upper = min(max_length, max(1, int(size * max_proportion)), size - 1)
    lower = min(upper, max(min_length, int(size * min_proportion)))
    return max(lower, min(int(np.sqrt(size)), upper))

def create_activity_sequences(activity_data, sequence_length, dates=None):
    if not isinstance(sequence_length, int) or isinstance(sequence_length, bool) or not 0 < sequence_length < len(activity_data):
        raise ValueError('sequence_length must be a positive integer smaller than the row count')
    if activity_data.shape[1] == 0:
        raise ValueError('At least one numeric activity feature is required')
    values = activity_data.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError('Activity features must be finite numeric observations')
    dates = list(activity_data.index if dates is None else dates)
    if len(dates) != len(values):
        raise ValueError('dates must align one-to-one with activity rows')
    X = np.stack([values[i:i + sequence_length] for i in range(len(values) - sequence_length)])
    y = values[sequence_length:].copy()
    sequence_dates = [dates[i:i + sequence_length] for i in range(len(values) - sequence_length)]
    return X, y, sequence_dates

def main():
    parser = argparse.ArgumentParser(description='Prepare activity sequences from an explicit CSV.')
    parser.add_argument('csv_file')
    args = parser.parse_args()
    frame = pd.read_csv(args.csv_file)
    frame.columns = frame.columns.str.strip()
    if 'date' not in frame.columns:
        parser.error('CSV must include a date column and numeric activity columns')
    dates = pd.to_datetime(frame.pop('date'), errors='raise')
    if not dates.is_monotonic_increasing or dates.isna().any():
        parser.error('Dates must be present and sorted in chronological order')
    length = determine_dynamic_sequence_length(frame)
    X, y, sequence_dates = create_activity_sequences(frame, length, dates)
    print(f'Sequence length: {length}; inputs: {X.shape}; targets: {y.shape}')

if __name__ == '__main__': main()
