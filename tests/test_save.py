import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.meta import save


class SaveTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'save.json'
            with patch.object(save, 'SAVE_PATH', str(target)):
                self.assertFalse(target.exists())
                save.save_meta({'stats': {'runs': 3}})
                self.assertEqual(save.load_meta()['stats']['runs'], 3)
                self.assertEqual(json.loads(target.read_text(encoding='utf-8'))['stats']['runs'], 3)

    def test_serialization_error_keeps_previous_save(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'save.json'
            target.write_text('{"stats":{"runs":7}}', encoding='utf-8')
            with patch.object(save, 'SAVE_PATH', str(target)):
                with self.assertRaises(TypeError):
                    save.save_meta({'invalid': object()})
                self.assertEqual(save.load_meta()['stats']['runs'], 7)
                self.assertEqual(list(Path(folder).glob('*.tmp')), [])


if __name__ == '__main__':
    unittest.main()
