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


class Review:
    def __init__(self, human_or_llm: str, deck: Deck):
        self.human_or_llm = human_or_llm
        self.deck = deck


class ReviewApp:
    def __init__(
        self,
        deck: Deck,
        input_provider: Callable[[str], str] = input,
        output_provider: Callable[[str], None] = print,
    ):
        self.deck = deck
        # This is unconventional in Python, but we are trying to avoid using
        # mocks. Here is a great article by James Shore you can read to learn
        # about the benefits of this approach: https://www.jamesshore.com/v2/projects/nullables/testing-without-mocks
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
                self.output_provider("Exiting review. Progress saved.")
                break
            elif response is None:
                self.output_provider("Skipping this card.")
                self.__reviews.append(None)
            else:
                self.__reviews.append(response)

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
        pass

    def load(self, fpath: Path):
        pass

    def accuracy(self):
        if len(self.deck) == len(self.__reviews):
            print(f"Accuracy: {sum(self.__reviews) / len(self.__reviews):.2%}")
        else:
            print("Dataset not fully annotated. Can't compute accuracy yet.")


if __name__ == "__main__":
    fire.Fire(review_notes)
