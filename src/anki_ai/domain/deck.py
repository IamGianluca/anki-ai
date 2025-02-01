import csv
import random
from collections.abc import Generator
from io import StringIO
from pathlib import Path
from typing import Any, List, Optional

from loguru import logger

from anki_ai.domain.note import Note


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
                        attrs = self._process_row(line)
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
            raise NotImplementedError(
                "Only files including HTML tags are supported. See documentation for more help."
            )

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

    def _process_row(self, row: str) -> dict[str, Any]:
        attrs = dict()
        with StringIO(row) as f:
            data = list(csv.reader(f, delimiter="\t", quotechar='"'))[0]
            if self.__deck_ncol > 0:
                guid, notetype, deck_name = data[: self.__deck_ncol]
                attrs["guid"] = guid
                attrs["notetype"] = notetype
                attrs["deck_name"] = deck_name
            front, back, _, _, _, tags = data[self.__deck_ncol :]
            attrs["front"] = front
            attrs["back"] = back
            attrs["tags"] = tags.split(" ")
            return attrs

    def write_txt(self, fpath) -> None:
        with open(fpath, "w", newline="") as f:
            writer = csv.writer(f, delimiter="\t", quotechar='"', lineterminator="\n")
            self._write_header(writer)
            for note in self:
                self._write_note(writer, note)

    def _write_header(self, f) -> None:
        f.writerow([f"#separator:{symbol2sep[self.__sep]}"])
        f.writerow([f"#html:{symbol2html[self.__html]}"])
        if self.__guid_ncol:
            f.writerow([f"#guid column:{self.__guid_ncol}"])
        if self.__notetype_ncol:
            f.writerow([f"#notetype column:{self.__notetype_ncol}"])
        if self.__deck_ncol:
            f.writerow([f"#deck column:{self.__deck_ncol}"])
        if self.__tags_ncol:
            f.writerow([f"#tags column:{self.__tags_ncol}"])

    def _write_note(self, f, note) -> None:
        out = []
        if self.__guid_ncol:
            out.append(note.guid)
        if self.__notetype_ncol:
            out.append(note.notetype)
        if self.__deck_ncol:
            out.append(note.deck_name)
        out.append(note.front)
        out.append(note.back)
        out.append("")
        out.append("")
        out.append("")
        if self.__tags_ncol:
            tags_str = "" if not note.tags else " ".join(note.tags)
            out.append(tags_str)
        f.writerow(out)

    def shuffle(self, seed: int = 42) -> None:
        random.seed(seed)
        random.shuffle(self.__collection)


sep2symbol = {"tab": "\t"}
symbol2sep = {v: k for k, v in sep2symbol.items()}
html2symbol = {"true": True, "false": False}
symbol2html = {v: k for k, v in html2symbol.items()}
