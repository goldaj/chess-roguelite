"""Source-only checks for playtest save isolation, no Pygame needed."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from playtest_entry import data_directory, initialise_save


class PlaytestEntryTests(unittest.TestCase):
    def test_explicit_playtest_directory_never_targets_original_save(self):
        from src.meta import save

        original = save.SAVE_PATH
        with tempfile.TemporaryDirectory() as tmp:
            desired = Path(tmp) / "my-playtest"
            with patch.dict(os.environ, {
                "CHESS_ROGUELITE_PLAYTEST_DATA_DIR": str(desired)
            }):
                self.assertEqual(data_directory(), desired.resolve())
                self.assertEqual(initialise_save(), desired.resolve())
                self.assertEqual(Path(save.SAVE_PATH), desired.resolve() / "save.json")
                save.save_meta({"playtest": True})
                self.assertTrue((desired / "save.json").exists())
                self.assertFalse((Path(tmp) / "src" / "meta" / "save.json").exists())
        save.SAVE_PATH = original

    def test_default_playtest_path_not_inside_project(self):
        with patch.dict(os.environ, {"CHESS_ROGUELITE_PLAYTEST_DATA_DIR": ""}):
            path = data_directory()
            project = Path(__file__).resolve().parents[1]
            self.assertNotEqual(path, project / "src" / "meta")
            self.assertEqual(path.name.lower(), (
                "chessrogueliteplaytest" if os.name == "nt"
                else "chess-roguelite-playtest"
            ))


if __name__ == "__main__":
    unittest.main()
