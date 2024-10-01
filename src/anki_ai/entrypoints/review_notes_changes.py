"""This entrypoint is to annotate notes that we can later use to evaluate the
capabilities of a LLM judge.
"""

from pathlib import Path
from typing import Callable

import fire

from anki_ai.domain.model import Deck


def review_notes(in_fpath: Path, out_fpath: Path):
    deck = Deck("edited")
    deck.read_txt(Path(in_fpath))
    ra = ReviewApp(deck)
    ra.review()
    ra.save(out_fpath)


class ReviewApp:
    def __init__(
        self,
        deck: Deck,
        input_provider: Callable[[str], str] = input,
        output_provider: Callable[[str], None] = print,
    ):
        self.deck = deck
        # NOTE: This is unconventional in Python. Here is a great article by
        # James Shore to learn about the benefits of this approach:
        # https://www.jamesshore.com/v2/projects/nullables/testing-without-mocks
        self.input_provider = input_provider
        self.output_provider = output_provider
        self.__reviews: list = []

    def n_reviewed(self) -> int:
        return len(self.__reviews)

    def review(self, n_reviews: int = 10):
        self.__reviews = []
        for i, note in enumerate(self.deck[:n_reviews]):
            self.output_provider(f"\nCard {i+1} of {len(self.deck)}")
            self.output_provider(
                f"Front: {note.front}\nBack: {note.back}\nTags: {note.tags}\n"
            )

            prompt = "Is it correct? (Y/N/S/Q) - Y: Yes, N: No, S: Skip, Q: Quit: "
            response = self._get_boolean_input(prompt)

            if response == "quit":
                self.output_provider("Exiting review.")
                break
            elif response is None:
                self.output_provider("Skipping this card.")
                self.__reviews.append(None)
            else:
                self.__reviews.append([note.guid, response])

            self.output_provider("\n")

    def _get_boolean_input(self, prompt):
        while True:
            response = self.input_provider(prompt).strip().lower()
            if response in ("y", "yes", "true", "1"):
                return True
            elif response in ("n", "no", "false", "0"):
                return False
            elif response == "s":
                return None
            elif response == "q":
                return "quit"
            else:
                self.output_provider(
                    "Invalid input. Please enter Y (Yes), N (No), S (Skip), or Q (Quit)."
                )

    def save(self, fpath: Path):
        with open(fpath, "w") as f:
            for review in self.__reviews:
                guid, score = review
                f.write(f"{guid}\t{score}\n")
        self.output_provider(f"Progress saved in file `{fpath}`.")

    def load(self, fpath: Path):
        with open(fpath, "r") as f:
            for line in f.readlines():
                guid, score = line.split("\t")
                self.__reviews.append([guid, score])


if __name__ == "__main__":
    fire.Fire(review_notes)
