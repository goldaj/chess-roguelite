"""One-shot Pygame smoke test on CI's SDL dummy display.

Unlike unittest's AST harness this instantiates the real game UI and lets the
computer execute a real move. No actual physical screen or human QA claimed.
The user save path is redirected to a temporary directory.
"""
import os
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.meta import save


def run():
    with tempfile.TemporaryDirectory(prefix="chess_qa_") as tmp:
        save.SAVE_PATH = os.path.join(tmp, "isolated-save.json")
        from src.main import App

        app = App()
        assert app.state == "menu"
        assert app.ai_difficulty == "normal"
        app.open_options()
        assert app.state == "options"
        assert any("Normal" in button.text for button in app.opt_btns)
        app.cycle_ai_difficulty()
        assert app.ai_difficulty == "hard"
        assert save.load_meta()["ai_difficulty"] == "hard"

        app.back_to_prev_from_options()
        app.start_game()
        assert app.state == "play"
        app.draw_play()  # real assets + UI render on SDL dummy backend
        assert app.board.locate_king(app.player_color)
        assert app.board.locate_king(app.enemy_color)

        app.turn = app.enemy_color
        before = app.enemy_ticks
        app.do_enemy_turn()  # actual tactical search, sprite and animation
        assert app.turn == app.player_color
        assert app.enemy_ticks < before
        assert app.board.locate_king(app.enemy_color)
        print("pygame-smoke: menu/options/persisted difficulty/play/one enemy move OK")
        pygame.quit()


if __name__ == "__main__":
    run()
