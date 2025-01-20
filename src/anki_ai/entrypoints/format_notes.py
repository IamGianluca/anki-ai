import re
from copy import deepcopy
from html import unescape
from pathlib import Path
from typing import Callable

import fire
from loguru import logger
from prompt_toolkit import prompt

from anki_ai.adapters.chat_completion import ChatCompletionsService
from anki_ai.domain.model import Deck
from anki_ai.service_layer.services import format_note, get_chat_completion


def format_notes(deck_fpath: Path, out_fpath: Path):
    """Use a LLM to improve existing Anki notes, and allow user to either
    accept the suggested changes, decline them, or make further manual changes.
    """
    deck = Deck()
    deck.read_txt(Path(deck_fpath))
    deck.shuffle()

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
                f"{orig.tags} {unescape(orig.front)}\n{unescape(orig.back)}\n"
            )

            proposed_note = format_note(note, self.__llm)
            self.output_provider(
                f"{proposed_note.tags} {proposed_note.front}\n{proposed_note.back}\n"
            )

            msg = "Accept AI suggestions? (Y/N/E/Q) - Y: Yes, N: No, E: Edit, Q: Quit: "
            # response = self._process_response(msg)
            response = self.input_provider(msg).strip().lower()
            while True:
                if response == "y":
                    self.__reviews[note.guid] = True  # TODO: save new note
                    break
                elif response == "n":
                    self.output_provider("Skipping this card.")
                    self.__reviews[note.guid] = False
                    break
                elif response == "e":
                    reviewed_note = prompt(
                        "",
                        default=f"{proposed_note.tags} {unescape(proposed_note.front)}\n{unescape(proposed_note.back)}",
                    )
                    new_note = deepcopy(note)
                    match = re.search(r"\[(.*?)\] (.*)\n(.*)", reviewed_note)
                    if match:
                        tags, front, back = match.groups()
                        new_note.front = front
                        new_note.back = back
                        new_note.tags = [e.replace("'", "") for e in tags.split(",")]
                        self.__reviews[note.guid] = False
                        break
                    else:
                        logger.warning("Could not parse edited note.")
                        break
                elif response == "q":
                    self.output_provider("Exiting review.")
                    # NOTE: we need to handle this outside of the while loop. If the use wants to quit
                    # the app, we need to quit and save.
                    # The while loop is needed to
                    return
                else:
                    print("Invalid input. Please enter A (Accept), S (Skip), E (Edit).")
                    continue
            self.output_provider("\n")

    # TODO: refactor to return either a bool or raise an exception
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
    fire.Fire(format_notes)
