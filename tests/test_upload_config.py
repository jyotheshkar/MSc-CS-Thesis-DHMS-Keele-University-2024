import importlib.util
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'Codes/data_utils.py'
spec = importlib.util.spec_from_file_location('upload_config', SOURCE)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

class UploadConfigTests(unittest.TestCase):
    def test_round_trip_does_not_depend_on_working_directory(self):
        with TemporaryDirectory() as home, TemporaryDirectory() as launch:
            path = Path(home) / 'upload_config.json'
            with patch.object(config, 'CONFIG_FILE', path):
                config.save_config({'activity_levels_file_path': 'activity.csv'})
                previous = os.getcwd()
                try:
                    os.chdir(launch)
                    activity, temperature = config.get_uploaded_data_paths()
                finally:
                    os.chdir(previous)
                self.assertEqual(activity, str(Path(home) / 'activity.csv'))
                self.assertIsNone(temperature)
                self.assertEqual(list(Path(home).iterdir()), [path])

    def test_failed_serialization_does_not_destroy_configuration(self):
        with TemporaryDirectory() as home:
            path = Path(home) / 'config.json'
            path.write_text('{"retained": true}')
            with patch.object(config, 'CONFIG_FILE', path):
                with self.assertRaises(TypeError):
                    config.save_config({'bad': object()})
            self.assertEqual(json.loads(path.read_text()), {'retained': True})
            self.assertEqual(list(Path(home).iterdir()), [path])

    def test_non_object_config_fails_explicitly(self):
        with TemporaryDirectory() as home:
            path = Path(home) / 'config.json'
            path.write_text('[]')
            with patch.object(config, 'CONFIG_FILE', path):
                with self.assertRaises(ValueError):
                    config.load_config()

if __name__ == '__main__':
    unittest.main()
