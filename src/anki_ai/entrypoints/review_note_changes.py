from pathlib import Path
from typing import Callable, Literal

import fire

from anki_ai.adapters.chat_completion import ChatCompletionsService
from anki_ai.domain.model import Deck
from anki_ai.service_layer.services import format_note, get_chat_completion


def review_notes_changes(old_fpath: Path, new_fpath: Path, out_fpath: Path):
    """Annotate notes that we can later be used to evaluate the capabilities
    of a LLM judge.
    """
    deck = Deck("original")
    deck.read_txt(Path(old_fpath))

    llm = get_chat_completion()

    ra = ReviewApp(deck=deck, llm=llm)
    ra.review()
    ra.save(out_fpath)


class ReviewApp:
    def __init__(
        self,
        deck: Deck,
        llm: ChatCompletionsService,
        input_provider: Callable[[str], str] = input,
        output_provider: Callable[[str], None] = print,
    ):
        self.__deck = deck
        self.__llm = llm
        self.input_provider = input_provider
        self.output_provider = output_provider
        self.__reviews: dict = {}

    def n_reviewed(self) -> int:
        return len(self.__reviews)

    def review(self, n_reviews: int = 25) -> None:
        self.__reviews = {}

        for i, note in enumerate(self.__deck[:n_reviews]):
            self.output_provider(f"\nCard {i + 1} of {n_reviews}")

            orig = self.__deck.get(note.guid)[0]
            self.output_provider(
                f"Front: {orig.front}\nBack: {orig.back}\nTags: {orig.tags}\n"
            )
            proposed_note = format_note(note, self.__llm)
            self.output_provider(
                f"Front: {proposed_note.front}\nBack: {proposed_note.back}\nTags: {proposed_note.tags}\n"
            )

            msg = "Is it correct? (Y/N/S/Q) - Y: Yes, N: No, S: Skip, Q: Quit: "
            response = self._process_response(msg)

            if response == "quit":
                self.output_provider("Exiting review.")
                break
            elif response is None:
                self.output_provider("Skipping this card.")
                self.__reviews[note.guid] = None
            else:
                self.__reviews[note.guid] = response

            self.output_provider("\n")

    # TODO: refactor to return either a bool or raise an exception
    def _process_response(self, prompt) -> bool | Literal["quit"] | None:
        while True:
            response = self.input_provider(prompt).strip().lower()
            if response == "y":
                return True
            elif response == "n":
                return False
            elif response == "s":
                return None
            elif response == "q":
                return "quit"
            else:
                self.output_provider(
                    "Invalid input. Please enter Y (Yes), N (No), S (Skip), or Q (Quit)."
                )

    def save(self, fpath: Path) -> None:
        with open(fpath, "w") as f:
            for guid, score in self.__reviews.items():
                f.write(f"{guid}\t{score}\n")
        self.output_provider(f"Progress saved in file `{fpath}`.")

    def load(self, fpath: Path) -> None:
        with open(fpath, "r") as f:
            for line in f.readlines():
                guid, score = line.split("\t")
                self.__reviews[guid] = score


if __name__ == "__main__":
    fire.Fire(review_notes_changes)
