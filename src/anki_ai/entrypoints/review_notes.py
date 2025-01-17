import re
from copy import deepcopy
from pathlib import Path

import fire

from anki_ai.domain.model import Deck


def review_notes(old_fpath: Path, out_fpath: Path):
    """Ask an LLM to improve an existing Anki note, and allow user to make
    further changes to what suggested by the AI. Both original, AI suggestion,
    and human reviewed version will be saved.
    """
    deck = Deck("original")
    deck.read_txt(Path(old_fpath))
    deck.shuffle()

    # TODO: In the future, we should probably be smarter in terms of what notes
    # we select for review (maybe those flagged in a certain way), and also
    # which notes should not be reviewed anymore (already reviewed in the past).
    # Ideally, I would like to use flags for that (everything with an orange flag
    # is eligible for review), but let's see.
    for note in deck:
        from html import unescape

        from prompt_toolkit import prompt

        edited_note = prompt(
            "> ", default=f"{note.tags} {unescape(note.front)}\n{unescape(note.back)}"
        )
        new_note = deepcopy(note)
        match = re.search(r"\[(.*?)\] (.*)\n(.*)", edited_note)
        if match:
            tags, front, back = match.groups()
            new_note.front = front
            new_note.back = back
            new_note.tags = [e.replace("'", "") for e in tags.split(",")]
        else:
            print("Could not parse edited note.")
        print()


if __name__ == "__main__":
    fire.Fire(review_notes)
