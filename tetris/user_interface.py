import curses
from typing import (
    List,
    Optional,
    Tuple
)

from tetris import Window
from tetris.core import (
    COLORS,
    GRID_HEIGHT,
    GRID_WIDTH,
    Block,
)

SCREEN_WIDTH: int = GRID_WIDTH * 2
SCREEN_HEIGHT: int = GRID_HEIGHT


def ensure_terminal_size() -> bool:
    """
    Helper method to ensure correct terminal size
    """
    if curses.LINES >= 24 and curses.COLS >= 80:
        return True
    return False

def make_color_pairs() -> None:
    """
    Helper method to make curses color pairs
    """
    curses.init_color(curses.COLOR_YELLOW, 1000, 1000, 0)
    for color in COLORS.values():
        curses.init_pair(color, color, color)

def create_screens(outer_screen: Window) -> Tuple[Optional[Window], Optional[Window]]:
    if ensure_terminal_size():
        border_screen = outer_screen.subwin(
            1 + SCREEN_HEIGHT + 1,
            1 + SCREEN_WIDTH + 1,
            (curses.LINES - SCREEN_HEIGHT) // 2 - 1,
            (curses.COLS - SCREEN_WIDTH) // 2 - 1,
        )
        inner_screen = border_screen.subwin(
            SCREEN_HEIGHT,
            SCREEN_WIDTH,
            (curses.LINES - SCREEN_HEIGHT) // 2,
            (curses.COLS - SCREEN_WIDTH) // 2,
        )
    else:
        return None, None
    return border_screen, inner_screen


class UserInterface:
    def __init__(self, stdscr: Window, inner_screen: Window):
        self.stdscr = stdscr
        self.inner_screen = inner_screen
        make_color_pairs()

    def render_score(self, score: int) -> None:  # pylint: disable=no-self-use
        """
        Renders current score at the lower left-hand side of the screen.
        """
        y = (curses.LINES - SCREEN_HEIGHT) // 2 + SCREEN_HEIGHT + 1
        x = (curses.COLS - SCREEN_WIDTH) // 2 - 1
        self.stdscr.addstr(y, x, f" SCORE: {score} ", curses.A_BOLD)

    def render_next_block(self, block: Block) -> None:  # pylint: disable=no-self-use
        """
        Renders incoming block at the right-hand side of the play field.
        """
        y = (curses.LINES - SCREEN_HEIGHT) // 2
        x = (curses.COLS - SCREEN_WIDTH) // 2

        self.stdscr.addstr(y, x + SCREEN_WIDTH + 3, "NEXT", curses.A_BOLD)

        for rowidx, row in enumerate(block.shape):
            for colidx, _ in enumerate(row):
                if block.shape[rowidx][colidx] != 0:
                    self.stdscr.addstr(
                        rowidx + y + 2,
                        (colidx * 2) + x + SCREEN_WIDTH + 3,
                        "██",
                        block.color,
                    )

    def render_landed_blocks(self, grid: List[List[List[Optional[int]]]]) -> None:
        """
        Renders all the landed tetrominos.
        """
        for rowidx, row in enumerate(grid):
            for colidx, col in enumerate(row):
                if grid[rowidx][colidx][0] != 0:
                    assert col[1] is not None
                    self._addstr(rowidx, colidx * 2, "██", col[1])

    def render_current_block(self, block: Block) -> None:
        """
        Renders a current tetromino.
        """
        for rowidx, row in enumerate(block.shape):
            for colidx, _ in enumerate(row):
                if block.shape[rowidx][colidx] != 0:
                    y, x = block.topleft
                    self._addstr(rowidx + y, (colidx + x) * 2, "██", block.color)

    def _addstr(self, y: int, x: int, text: str, color_info_stuff: int) -> None:
        """
        Works around curses' limitation of drawing at bottom right corner
        of the screen, as seen on https://stackoverflow.com/q/36387625
        """
        screen_height, screen_width = self.inner_screen.getmaxyx()
        if x + len(text) == screen_width and y == screen_height - 1:
            try:
                self.inner_screen.addstr(y, x, text, color_info_stuff)
            except curses.error:
                pass
        else:
            self.inner_screen.addstr(y, x, text, color_info_stuff)
