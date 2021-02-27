import locale
import curses
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict
)

from tetris import Window
from tetris.core import Game
from tetris.exceptions import CollisionError, OutOfBoundsError
from tetris.user_interface import (
    UserInterface,
    create_screens
)

if TYPE_CHECKING:
    from tetris.core import Block
else:
    Block = Any


KEY_BINDINGS: Dict[int, Callable[[Block], None]] = {
    curses.KEY_LEFT: lambda block: block.move_sideways("left"),
    curses.KEY_RIGHT: lambda block: block.move_sideways("right"),
    curses.KEY_DOWN: lambda block: block.move_down(),
    ord("s"): lambda block: block.move_all_the_way_down(),
    ord("a"): lambda block: block.rotate("left"),
    ord("d"): lambda block: block.rotate("right"),
}


def main(stdscr: Window) -> None:
    locale.setlocale(locale.LC_ALL, "")
    stdscr.nodelay(True)
    curses.curs_set(False)

    border_screen, inner_screen = create_screens(stdscr)

    assert border_screen is not None, "minimum screen size required"
    assert inner_screen is not None, "minimum screen size required"

    inner_screen.timeout(100)
    inner_screen.keypad(True)

    user_interface = UserInterface(inner_screen)
    game = Game(inner_screen, user_interface)

    while True:
        for screen in (inner_screen, border_screen, stdscr):
            screen.erase()

        border_screen.box(0, 0)

        user_interface.renderer.render_landed_blocks(game.grid)
        user_interface.renderer.render_current_block(game.block)
        user_interface.display_next_block(stdscr, game.next_block)
        user_interface.display_score(stdscr, game.score)

        stdscr.refresh()
        inner_screen.refresh()

        if not game.paused:
            game.handle_falling()
            game.clear_rows()

        try:
            user_input = inner_screen.getch()
        except curses.error:
            continue
        except KeyboardInterrupt:
            sys.exit()

        if user_input == ord("p"):
            game.pause()

        elif user_input == ord("q"):
            sys.exit()

        elif not game.paused and user_input in KEY_BINDINGS:
            try:
                KEY_BINDINGS[user_input](game.block)
            except (CollisionError, OutOfBoundsError):
                continue
