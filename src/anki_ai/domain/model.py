from pathlib import Path
from typing import Any, List, Optional
from uuid import uuid4

from loguru import logger


class Note:
    def __init__(
        self,
        front: str,
        back: str,
        tags: Optional[List[str]] = None,
        uuid: Optional[str] = None,
        note_type: Optional[str] = None,
        deck_name: Optional[str] = None,
    ) -> None:
        self.uuid = uuid if uuid is not None else uuid4()
        self.note_type = note_type
        self.front = front
        self.back = back
        self.tags = tags
        self.note_type = note_type
        self.deck_name = deck_name

    def __repr__(self) -> str:
        return f"Note(uuid={self.uuid}, front={self.front}, back={self.back}, tags={self.tags}"


class Deck:
    def __init__(self, name: Optional[str] = "default") -> None:
        self.name = name
        self._collection: List = []
        self.sep_ = None
        self.html_ = None
        self.deck_ncols_ = 0
        self.tags_ncols_ = 0

    def __getitem__(self, slice) -> List[Note]:
        return self._collection[slice]

    def __len__(self) -> int:
        return len(self._collection)

    def add(self, note: List[Note]) -> None:
        self._collection.extend(note)

    def read_txt(self, fpath: Path, ignore_media: bool = True) -> None:
        with open(fpath) as f:
            for i, line in enumerate(f):
                if line.startswith("#"):
                    self._parse_header(line)
                else:
                    try:
                        if ignore_media:
                            if "<img src=" in line:
                                continue
                        attrs = self._process_line(line)
                        self._collection.append(Note(**attrs))
                    except ValueError as e:
                        logger.warning(f"Error while processing line {i}: {e}")

    def _process_line(self, line: str) -> dict[str, Any]:
        attrs = dict()
        if self.deck_ncols_ > 0:
            uuid, note_type, deck_name = line.split(self.sep_)[: self.deck_ncols_]
            attrs["uuid"] = uuid
            attrs["note_type"] = note_type
            attrs["deck_name"] = deck_name
        front, back, _, _, _, tags = line.split(self.sep_)[self.deck_ncols_ :]
        attrs["front"] = front
        attrs["back"] = back

        # convert tags as a list of str
        tags = tags.replace("\n", "")
        tags = list(tags.split(" "))
        attrs["tags"] = tags
        return attrs

    def _extract_separator(self, line) -> None:
        _, sep = line.strip().split(":")
        if sep == "tab":
            self.sep_ = "\t"
        else:
            raise ValueError(f"Only tab-separated files are supported. Found {sep}")

    def _parse_header(self, line: str) -> None:
        if "separator" in line:
            self._extract_separator(line)
        if "html" in line:
            self._extract_html(line)
        if "column" in line:
            self._extract_ncols(line)

    def _extract_html(self, line: str) -> None:
        _, html = line.strip().split(":")
        if html == "true":
            self.html_ = True
        else:
            self.html_ = False

    def _extract_ncols(self, line: str) -> None:
        col_type, n_cols = line.split(":")
        if "deck" in col_type:
            self.deck_ncols_ = int(n_cols)
        elif "tags" in col_type:
            self.tags_ncols_ = int(n_cols)
