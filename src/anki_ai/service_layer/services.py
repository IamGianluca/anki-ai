from copy import deepcopy
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path
from typing import cast

import fire
from loguru import logger
from openai import APIConnectionError
from tqdm import tqdm

from anki_ai.adapters.chat_completion import ChatCompletionsService, get_chat_completion
from anki_ai.domain.model import Deck, Note, NoteChanges


def format_deck(in_path: Path, out_path: Path) -> None:
    chat = get_chat_completion()
    deck = Deck()
    deck.read_txt(in_path)

    for note in tqdm(deck):
        try:
            new_note = format_note(note=note, chat=chat)
            deck.update(guid=note.guid, changes=new_note)
        except APIConnectionError as e:
            raise APIConnectionError(
                request=e.request,
                message="LLM inference server is not reachable. Make sure you have started it with `make vllm` command.",
            ) from e
        except Exception as e:
            logger.warning(f"Skipping note {note}: {e}")

    deck.write_txt(out_path)


def format_note(note: Note, chat: ChatCompletionsService) -> Note:
    # TODO: check if stripping tags is actually compromising performance
    user_msg = f"""Front: {strip_tags(note.front)}\nBack: {strip_tags(note.back)}"""

    messages = [
        {"role": "system", "content": SYSTEM_MSG},
        {"role": "user", "content": user_msg},
    ]

    extra_body = {
        "guided_json": Note.model_json_schema(),
        "guided_whitespace_pattern": r"[\n\t ]*",
    }

    chat_response = chat.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct",
        messages=messages,  # type: ignore
        temperature=0,
        extra_body=extra_body,
    )
    json_data: str = cast(str, chat_response.choices[0].message.content)
    suggested_changes = NoteChanges.model_validate_json(json_data)

    new_note = deepcopy(note)
    new_note.front = suggested_changes.front
    new_note.back = suggested_changes.back
    return new_note


def strip_tags(html):
    s = HTMLStripper()
    s.feed(replace_br_with_newline(html))
    return s.get_data()


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, data):
        self.text.write(data)

    def get_data(self):
        return self.text.getvalue()


def replace_br_with_newline(html_string):
    import re

    return re.sub(r"<br\s*/?>", "\n", html_string)


SYSTEM_MSG = r"""Optimize this Anki note:
- Concise, simple, distinct
- Follow format rules
- Markdown syntax

Reply in this format:
Front: [edited front]
Back: [edited back]

Terminal commands:
```bash
$ command <placeholder>
```

Code:
```language
code here
```

Use the following placeholders only: <file>, <path>, <link>, <command>.

No explanations.

Return results using this JSON schema:
{
    "title": "Note",
    "type": "object",
    "properties": {
        "front": {"type": "string"},
        "back": {"type": "string"},
    },
    "required": ["front", "back"]
}

Example 1:
Front: What command does extract files from a zip archive?
Back: ```bash
$ unzip <file>
```
{ "front": "Extract zip files", "back": "```bash<br>$ unzip <file><br>```" }

Example 2:
Front: What is the command to print manual or get help for a command?
Back: ```bash
$ man ...
```
{ "front": "Get command manual/help", "back": "```bash<br>$ man <command><br>```" }

Example 3: 
Front: What command does create a soft link?
Back: ```bash
$ ln -s <file_name> <link_name>
```
{ "front": "Create soft link", "back": "```bash<br>$ ln -s <file> <link><br>```" }

Example 4:
Front: In the `ln -s` command, what is the order of file name and link name?
Back: ```bash
$ ln -s <file_name> <link_name>
```
{ "front": "`ln -s` argument order", "back": "Back: <file> then <link>" }

Example 5:
Front: What is the range of the Leaky ReLU function?
Back: $ [ -0.01, + \infty ] $
{ "front": "Leaky ReLU range", "back": "$ [-0.01, +\infty] $" }
"""


if __name__ == "__main__":
    fire.Fire(format_deck)
