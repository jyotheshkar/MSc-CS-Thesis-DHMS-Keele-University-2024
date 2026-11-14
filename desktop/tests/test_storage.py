from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from dhms.core import DataError
from dhms.storage import load_settings, save_settings


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)/'workspace'
        self.patcher=patch('dhms.storage.workspace_path',return_value=self.folder)
        self.patcher.start(); self.addCleanup(self.patcher.stop)

    def test_missing_corrupt_and_nondict_config_returns_defaults(self):
        self.assertEqual(load_settings(),{})
        self.folder.mkdir()
        for content in ['broken','[]','x'*16385]:
            (self.folder/'settings.json').write_text(content)
            self.assertEqual(load_settings(),{})

    def test_atomic_roundtrip_and_serialization_failure_preserves_old(self):
        save_settings({'window':5,'metric':'temperature'})
        self.assertEqual(load_settings(),{'window':5,'metric':'temperature'})
        for bad in [{'window':float('nan')},{'bad':object()},[],{'oversize':'x'*17000}]:
            with self.subTest(bad=type(bad).__name__),self.assertRaises(DataError): save_settings(bad)
        self.assertEqual(load_settings()['window'],5)

    def test_disk_failure_preserves_old_and_removes_temporary(self):
        save_settings({'window':3})
        with patch('dhms.storage.os.replace',side_effect=OSError('full')),self.assertRaises(DataError): save_settings({'window':4})
        self.assertEqual(load_settings(),{'window':3})
        self.assertEqual(list(self.folder.glob('.settings-*')),[])


if __name__=='__main__': unittest.main()
