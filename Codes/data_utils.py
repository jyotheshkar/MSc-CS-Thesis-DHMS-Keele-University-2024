"""Upload persistence shared by the desktop components.

Paths are anchored to this module so launches from another directory agree.
"""
import json
import os
from pathlib import Path
import tempfile

DATA_DIR = Path(__file__).resolve().parent
CONFIG_FILE = DATA_DIR / 'upload_config.json'
SAVE_DIR = DATA_DIR / 'saved_upload_data'


def load_config():
    path = Path(CONFIG_FILE)
    if not path.exists():
        return {}
    with path.open(encoding='utf-8') as handle:
        config = json.load(handle)
    if not isinstance(config, dict):
        raise ValueError('Upload configuration must be a JSON object')
    # Preserve old relative paths, interpreted against the configuration directory.
    for key in ('activity_levels_file_path', 'temperature_analysis_file_path'):
        value = config.get(key)
        if value and not Path(value).is_absolute():
            config[key] = str((path.parent / value).resolve())
    return config


def save_config(config):
    if not isinstance(config, dict):
        raise ValueError('Upload configuration must be a JSON object')
    path = Path(CONFIG_FILE)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                dir=path.parent, prefix='.upload-', suffix='.tmp', delete=False) as handle:
            temporary_path = Path(handle.name)
            json.dump(config, handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def get_uploaded_data_paths():
    config = load_config()
    return config.get('activity_levels_file_path'), config.get('temperature_analysis_file_path')
