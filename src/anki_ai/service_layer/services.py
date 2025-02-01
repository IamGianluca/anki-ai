import html
import re
from copy import deepcopy
from pathlib import Path

import fire
from jinja2 import Template
from loguru import logger
from openai import APIConnectionError
from tqdm import tqdm

from anki_ai.adapters.chat_completion import (
    ChatCompletionsServiceProtocol,
)
from anki_ai.domain.deck import Deck
from anki_ai.domain.note import Note, NoteChanges


def format_deck(
    in_path: Path, out_path: Path, chat: ChatCompletionsServiceProtocol
) -> None:
    deck = Deck()
    deck.read_txt(in_path)

    for note in tqdm(deck):
        try:
            new_note = format_note_workflow(note=note, chat=chat)
            deck.update(guid=note.guid, changes=new_note)
        except APIConnectionError as e:
            raise APIConnectionError(
                request=e.request,
                message="LLM inference server is not reachable. Make sure you have started it with `make vllm` command.",
            ) from e
        except Exception as e:
            logger.warning(f"Skipping note {note}: {e}")

    deck.write_txt(out_path)


def format_note_workflow(note: Note, chat: ChatCompletionsServiceProtocol) -> Note:
    note = _format_note(note, chat)
    note = _remove_alt_tags(note)
    return note


def _format_note(note: Note, chat: ChatCompletionsServiceProtocol) -> Note:
    user_msg = (
        lambda note: f"""Front: {remove_html_tags(note.front)}\nBack: {remove_html_tags(note.back)}\nTags: {note.tags}\n"""
    )
    system_msg = lambda note: system_msg_tmpl.render(input_note=note)
    prompt = system_msg(user_msg(note))

    response = chat.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct",
        prompt=prompt,
        temperature=0,
        max_tokens=500,
        extra_body={
            "guided_json": Note.model_json_schema(),
        },
    )

    json_data = response.choices[0].text
    suggested_changes = NoteChanges.model_validate_json(json_data)

    new_note = deepcopy(note)
    new_note.front = suggested_changes.front
    new_note.back = suggested_changes.back
    return new_note


system_msg_tmpl = Template(r"""Your job is to optimize Anki notes, and particularly to make each note:
- Concise, simple, distinct
- Follow formatting rules
- Use valid Markdown syntax

You will be present with an existing note, including front, back, and tags. You must create a new note preserving its original meaning, and preserving any image, code block, and math block. 

### Formatting rules

The following rules apply to both front and back of each note.

Terminal commands must follow this format:
```bash
$ command <placeholder>
```

Code snippets must follow this format:
```language
code here
```

Name of programs, utilities, and tools like nvim, systemctl, pandas, grep, etc. must follow this format:
`nvim`, `systemctl`, `pandas`, `grep`

Keyboard keys and keymaps must follow this format:
`<C-aa>`, `x`, `J`, `gg`, `<S-p>`

In code blocks, use only the following placeholders: <file>, <path>, <link>, <command>.

Represent newlines with the `<br>` tag instead of `\n`. 

### Other rules

Always copy to the new note, without any modification, code bdlocks and images from the original note. 

Wrap back of a note within double quotes.

No explanations.

Return results using this JSON schema:
{
    "title": "Note",
    "type": "object",
    "properties": {
        "front": {"type": "string"},
        "back": {"type": "string"},
        "tags": {"type": "string"},
    },
    "required": ["front", "back", "tags"]
}

### Examples

Example 1: Code block
Input: Front: What command does extract files from a zip archive?
Back: ```bash
$ unzip <file>
Tags: ['linux']
```
Output: { "front": "Extract zip files", "back": "\"```bash<br>$ unzip <file><br>```\"", "tags": ['linux'] }

Example 2: Cloze completion
Input: Front: What type of memory do GPUs come equipped with?
* \{\{c1::Dynamic RAM (HBM)\}\}
* \{\{c2::Static RAM (L1 + L2 + Registers)\}\}
Back: 
Tags: ['recsys'] 
```
Output: { "front": "Type of memory on a GPU:<br>* \{\{c1::Dynamic RAM (HBM)\}\}<br>* \{\{c2::Static RAM (L1 + L2 + Registers)\}\}", "back": "\"\"", "tags": ['linux'] }

Example 3: Code block with placeholders
Input: Front: What command creates a soft link?
Back: ```bash
$ ln -s <file_name> <link_name>
```
Tags: ['linux']
Output: { "front": "Create soft link", "back": "\"```bash<br>$ ln -s <file> <link><br>```\"", "tags": ['linux'] }

Example 4: Code block and inline code block
Input: Front: In the `ln -s` command, what is the order of file name and link name?
Back: ```bash
$ ln -s <file_name> <link_name>
```
Tags: ['linux']
Output: { "front": "`ln -s` argument order", "back": "\"<file> then <link>\"", "tags": ['linux'] }

Example 5: Math
Input: Front: What is the range of the Leaky ReLU function?
Back: $ [ -0.01, + \infty ] $
Tags: ['dl']
Output: { "front": "Leaky ReLU range", "back": "\"$ [-0.01, +\infty] $\"", "tags": ['dl'] }

Example 6: Inline code block
Input: Front: What key returns the `^` in the shifted state?
Back: "`6`"
Tags: ['keyboard']
Output: { "front": "Keyboard key for `^` in shifted state", "back": "\"`6`\"", "tags": ['keyboard'] }


Input: {{ input_note }}
Output: """)


def _remove_alt_tags(note: Note) -> Note:
    note.front = re.sub(r'<img\s+alt="+[^"]*"+', "<img ", note.front)
    note.back = re.sub(r'<img\s+alt="+[^"]*"+', "<img ", note.back)
    return note


def add_html_tags(s: str) -> str:
    return html.escape(s).replace("\n", "<br>")


def remove_html_tags(s: str) -> str:
    return html.unescape(s).replace("<br>", "\n")


if __name__ == "__main__":
    fire.Fire(format_deck)
