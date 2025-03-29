import json
import os

CONFIG_FILE = 'upload_config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def get_uploaded_data_paths():
    """
    Returns the uploaded file paths for activity and temperature data.
    """
    config = load_config()
    return config.get('activity_levels_file_path'), config.get('temperature_analysis_file_path')
