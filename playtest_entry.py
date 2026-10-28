"""Isolated Chess Roguelite playtest entry point (source and Windows .exe).

Game rules/assets are imported from the active branch. Playtest progress lives
outside the git checkout and never overwrites the user's production save.
No network requests, uploads, tracking or service integration.

Run: python playtest_entry.py
Test: python playtest_entry.py --smoke
"""
from __future__ import annotations

import argparse
import os
import sys
import traceback
from pathlib import Path


def data_directory() -> Path:
    """Dedicated playtest data, not the existing src/meta/save.json."""
    explicit = os.environ.get("CHESS_ROGUELITE_PLAYTEST_DATA_DIR")
    if explicit:
        return Path(explicit).expanduser().resolve()
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        if local:
            return Path(local) / "ChessRoguelitePlaytest"
        return Path.home() / "AppData" / "Local" / "ChessRoguelitePlaytest"
    return Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))) / "chess-roguelite-playtest"


def initialise_save() -> Path:
    from src.meta import save

    folder = data_directory()
    folder.mkdir(parents=True, exist_ok=True)
    save.SAVE_PATH = str(folder / "save.json")
    return folder


def smoke_test() -> None:
    """Actual Pygame App, sprite loading and full shop -> stage transition."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame
    from src.main import App

    game = App()
    try:
        assert game.state == "menu"
        game.open_options()
        game.draw_options()
        game.back_to_prev_from_options()
        game.start_game()
        assert game.state == "play"
        game.draw_play()
        game.turn = game.enemy_color
        game.do_enemy_turn()
        assert game.turn == game.player_color
        game.end_stage(True)  # smoke of transition, not proof of human victory
        assert game.state == "shop"
        game.draw_shop()
        game.select_route("risk")
        game.shop_continue_next()
        assert game.state == "play"
        assert game.active_route == "risk"
        game.draw_play()
        print("PLAYTEST_SMOKE_OK")
    finally:
        pygame.quit()


def report_failure(exc: Exception, folder: Path, smoke: bool) -> None:
    message = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    # Local-only diagnostic. Never copied into a git branch or sent over network.
    try:
        (folder / "last_crash.txt").write_text(message, encoding="utf-8")
    except OSError:
        pass
    if smoke:
        print(message, file=sys.stderr)
    elif sys.platform == "win32":
        try:
            from ctypes import windll
            windll.user32.MessageBoxW(
                None,
                "Le test Chess Roguelite n'a pas pu demarrer.\n"
                "Details locaux :\n" + str(folder / "last_crash.txt"),
                "Chess Roguelite - erreur de lancement",
                0x10,
            )
        except (AttributeError, OSError):
            print(message, file=sys.stderr)
    else:
        print(message, file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Isolated Chess Roguelite playtest")
    parser.add_argument("--smoke", action="store_true", help="Automated SDL smoke test; exits")
    args = parser.parse_args(argv)
    folder = data_directory()
    try:
        initialise_save()
        if args.smoke:
            smoke_test()
        else:
            from src.main import App
            App().run()
    except Exception as exc:
        report_failure(exc, folder, args.smoke)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
