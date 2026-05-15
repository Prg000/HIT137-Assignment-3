 # gamestate.py

import math
from alterations import Alteration


class GameState:
    # Manages all  games logic for the Spot the Difference game.
    # shows the  encapsulation and class interaction.

    MAX_MISTAKES = 3      # mistakes allowed per image
    CLICK_TOLERANCE = 45  # px radius for a hit detection

    def __init__(self):
        # Initialise with 0 cumulatives score and  empty round.
        self.total_found: int = 0
        self._reset_round()

    # Public methods

    def new_round(self, alterations: list):
        # Start a new fresh round with the given lists of Alteration objects.
        self.alterations = alterations
        self.found_flags = [False] * len(alterations)
        self.mistakes = 0
        self.locked = False

    def check_click(self, canvas_x: int, canvas_y: int) -> tuple:
        # Check if  click hit any unfound difference region.
        # Returns (index,   already found)

        if self.locked:
            return -1, False

        for i, alt in enumerate(self.alterations):
            cx, cy = alt.get_center()
            dist = math.hypot(canvas_x - cx, canvas_y - cy)

            if dist <= self.CLICK_TOLERANCE:
                if self.found_flags[i]:
                    return i, True  # already found

                # New found
                self.found_flags[i] = True
                self.total_found += 1
                return i, False

        # Miss    count as a mistake
        self.mistakes += 1

        if self.mistakes >= self.MAX_MISTAKES:
            self.locked = True

        return -1, False

    def all_found(self) -> bool:
        # Return True if all difference in this round have been found.
        return all(self.found_flags)

    def remaining(self) -> int:
        # Return the  number of difference still unfound in this round.
        return self.found_flags.count(False)

    def unfound_alterations(self) -> list:
        # Retur  lists  of Alteration objects not yet found.
        return [
            alt for alt, found in zip(self.alterations, self.found_flags)
            if not found
        ]

    # Private methods

    def _reset_round(self):
        # Reset all the  round-specific state.
        self.alterations: list = []
        self.found_flags: list = []
        self.mistakes: int = 0
        self.locked: bool = False