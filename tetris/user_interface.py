import curses
import sys

import trio


GRID_WIDTH = 10
GRID_HEIGHT = 16

INNER_SCREEN_WIDTH = GRID_WIDTH*2
INNER_SCREEN_HEIGHT = GRID_HEIGHT


class UserInterface:

    def __init__(self, screen):
        self.screen = screen
        self.renderer = Renderer(screen)
        self.lines, self.cols = screen.getmaxyx()
        self.make_colour_pairs()

    @staticmethod
    def ensure_terminal_size():
        """
        Helper method to ensure correct terminal size
        """
        if curses.LINES >= INNER_SCREEN_HEIGHT and curses.COLS >= INNER_SCREEN_WIDTH:
            return True
        return False

    @staticmethod
    def make_colour_pairs():
        """
        Helper method to make curses colour pairs
        """
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLUE)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_CYAN)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_WHITE)

    def display_score(self, screen, score):
        """
        Displays current score at the lower left-hand side of the screen.
        """
        y = (curses.LINES // 2 - (INNER_SCREEN_HEIGHT // 2)) + self.lines + 1
        x = (curses.COLS // 2 - (INNER_SCREEN_WIDTH // 2)) - 1
        screen.addstr(y, x, f" SCORE: {score} ", curses.A_BOLD)

    async def display_game_over_screen(self, game):
        """
        Displays game over screen and waits for user input.
        If the input are keys "q" or "r", it quits or restarts the game, respectively.
        """
        self.screen.erase()
        self.screen.addstr(self.lines // 2 - 1, self.cols // 2 - 4, "GAME OVER")
        self.screen.addstr(self.lines // 2, self.cols // 2 - 4, f"SCORE: {game.score}")
        self.screen.addstr(self.lines // 2 + 2, self.cols // 2 - 8, "[r]estart [q]uit")
        self.screen.refresh()
        while True:
            try:
                user_input = self.screen.getch()
            except curses.error:
                await trio.sleep(0.1)
                continue
            if ord("q") == user_input:
                sys.exit()
            if ord("r") == user_input:
                game.restart()
                break

class Renderer:

    def __init__(self, screen):
        self.screen = screen

    def _better_addstr(self, y, x, text, color_info_stuff):
        screen_height, screen_width = self.screen.getmaxyx()
        if x + len(text) == screen_width and y == screen_height-1:
            # https://stackoverflow.com/q/36387625
            try:
                self.screen.addstr(y, x, text, color_info_stuff)
            except curses.error:
                pass
        else:
            self.screen.addstr(y, x, text, color_info_stuff)


    def render_landed_blocks(self, grid):
        for rowidx, row in enumerate(grid):
            for colidx, col in enumerate(row):
                if grid[rowidx][colidx][0] != 0:
                    self._better_addstr(rowidx, colidx * 2, "██", col[1] if col[1] is not None else curses.COLOR_BLACK)

    def render_current_block(self, block):
        for rowidx, row in enumerate(block.shape):
            for colidx, col in enumerate(row):
                if block.shape[rowidx][colidx] != 0:
                    self._better_addstr(rowidx + block.topleft[0], (colidx * 2) + block.topleft[1] * 2, "██", block.colour)
