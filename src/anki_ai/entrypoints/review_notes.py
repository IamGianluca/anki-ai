import re
from copy import deepcopy
from html import unescape
from pathlib import Path

import fire
from prompt_toolkit import prompt

from anki_ai.adapters.chat_completion import get_chat_completion
from anki_ai.domain.model import Deck
from anki_ai.service_layer.services import format_note


def review_notes(old_fpath: Path, out_fpath: Path) -> None:
    """Ask an LLM to improve an existing Anki note, and allow user to make
    further changes to what suggested by the AI. Both original, AI suggestion,
    and human reviewed version will be saved.
    """
    deck = Deck("original")
    deck.read_txt(Path(old_fpath))
    deck.shuffle()

    llm = get_chat_completion()

    for note in deck:
        print("Original note:")
        print(f"{note.tags} {unescape(note.front)}\n{unescape(note.back)}\n")

        print("AI suggestion:")
        proposed_note = format_note(note, llm)
        print(
            f"{proposed_note.tags} {unescape(proposed_note.front)}\n{unescape(proposed_note.back)}\n"
        )

        while True:
            msg = "Accept AI suggestion? (A/S/E) - A: Accept, S: Skip, E: Edit: "
            response = input(msg).strip().lower()
            if response == "a":
                break
            elif response == "s":
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
                    break
                else:
                    print("Could not parse edited note.")
            else:
                print("Invalid input. Please enter A (Accept), S (Skip), E (Edit).")

        print("\n############\n")


# TODO: persist changes to disk


if __name__ == "__main__":
    fire.Fire(review_notes)
