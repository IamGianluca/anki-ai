import random
from collections.abc import Generator
from pathlib import Path
from typing import Any, List, Optional

from loguru import logger
from pydantic import BaseModel


class Note(BaseModel):
    guid: str
    front: str
    back: str
    tags: Optional[List[str]] = None
    notetype: Optional[str] = None
    deck_name: Optional[str] = None


class NoteChanges(BaseModel):
    front: str
    back: str
    tags: Optional[List[str]] = None


class Deck:
    def __init__(self) -> None:
        self.__collection: List = []
        self.__sep: str = ""
        self.__html: bool = True
        self.__guid_ncol: Optional[int] = None
        self.__notetype_ncol: Optional[int] = None
        self.__deck_ncol: int = 0
        self.__tags_ncol: int = 0

    def __getitem__(self, slice) -> List[Note]:
        return self.__collection[slice]

    def __iter__(self) -> Generator[Note, None, None]:
        yield from self.__collection

    def __len__(self) -> int:
        return len(self.__collection)

    def add(self, note: List[Note]) -> None:
        self.__collection.extend(note)

    def get(self, guid: str) -> List[Note]:
        return [note for note in self if note.guid == guid]

    def update(self, guid: str, changes: Note) -> None:
        note = self.get(guid=guid)[0]
        logger.info(f"Original note: {note}")
        note.front = changes.front
        note.back = changes.back
        logger.info(f"Updated note: {note}")

    def read_txt(self, fpath: Path, exclude_tags: List[str] = []) -> None:
        with open(fpath) as f:
            for i, line in enumerate(f):
                if line.startswith("#"):
                    self._parse_header(line)
                else:
                    try:
                        attrs = self._process_line(line)
                        if bool(set(attrs["tags"]) & set(exclude_tags)):
                            continue
                        self.__collection.append(Note(**attrs))
                    except ValueError as e:
                        logger.warning(
                            f"Error while processing line {i} ({line}) : {e}"
                        )

    def _parse_header(self, line: str) -> None:
        if "separator" in line:
            self._extract_separator(line)
        if "html" in line:
            self._extract_html(line)
        if "column" in line:
            self._extract_ncols(line)

    def _extract_separator(self, line) -> None:
        _, sep = line.strip().split(":")
        if sep == "tab":
            self.__sep = "\t"
        else:
            raise NotImplementedError(
                f"Only tab-separated files are supported. Found {sep}"
            )

    def _extract_html(self, line: str) -> None:
        _, html = line.strip().split(":")
        if html == "true":
            self.__html = True
        else:
            self.__html = False

    def _extract_ncols(self, line: str) -> None:
        col_type, n_cols = line.split(":")
        if "guid" in col_type:
            self.__guid_ncol = int(n_cols)
        elif "notetype" in col_type:
            self.__notetype_ncol = int(n_cols)
        elif "deck" in col_type:
            self.__deck_ncol = int(n_cols)
        elif "tags" in col_type:
            self.__tags_ncol = int(n_cols)

    def _process_line(self, line: str) -> dict[str, Any]:
        attrs = dict()
        if self.__deck_ncol > 0:
            guid, notetype, deck_name = line.split(self.__sep)[: self.__deck_ncol]
            attrs["guid"] = guid
            attrs["notetype"] = notetype
            attrs["deck_name"] = deck_name
        front, back, _, _, _, tags = line.split(self.__sep)[self.__deck_ncol :]
        attrs["front"] = front
        attrs["back"] = back

        # Convert tags as a list of str
        tags = tags.replace("\n", "")
        tags = list(tags.split(" "))
        attrs["tags"] = tags
        return attrs

    def write_txt(self, fpath) -> None:
        with open(fpath, "w") as f:
            self._write_header(f)
            for note in self:
                self._write_note(f, note)

    def _write_header(self, f) -> None:
        f.write(f"#separator:{symbol2sep[self.__sep]}\n")
        f.write(f"#html:{symbol2html[self.__html]}\n")
        if self.__guid_ncol:
            f.write(f"#guid column:{self.__guid_ncol}\n")
        if self.__notetype_ncol:
            f.write(f"#notetype column:{self.__notetype_ncol}\n")
        if self.__deck_ncol:
            f.write(f"#deck column:{self.__deck_ncol}\n")
        if self.__tags_ncol:
            f.write(f"#tags column:{self.__tags_ncol}\n")

    def _write_note(self, f, note) -> None:
        out = ""
        if self.__guid_ncol:
            out += f"{note.guid}\t"
        if self.__notetype_ncol:
            out += f"{note.notetype}\t"
        if self.__deck_ncol:
            out += f"{note.deck_name}\t"
        out += f"{note.front}\t{note.back}\t\t\t\t"
        if self.__tags_ncol:
            tags = " ".join(note.tags)
            out += f"{tags}"
        f.write(f"{out}\n")

    def shuffle(self, seed: int = 42) -> None:
        random.seed(seed)
        random.shuffle(self.__collection)


sep2symbol = {"tab": "\t"}
symbol2sep = {v: k for k, v in sep2symbol.items()}
html2symbol = {"true": True, "false": False}
symbol2html = {v: k for k, v in html2symbol.items()}
