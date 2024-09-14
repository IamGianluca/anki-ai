from pathlib import Path
from typing import Any, List, Optional

from loguru import logger
from pydantic import BaseModel


class Note(BaseModel):
    front: str
    back: str
    tags: Optional[List[str]] = None
    guid: Optional[str] = None
    notetype: Optional[str] = None
    deck_name: Optional[str] = None


class Deck:
    def __init__(self, name: str = "default") -> None:
        self.name: str = name
        self._collection: List = []
        self.sep_: str = ""
        self.html_: bool = True
        self.guid_ncol_: Optional[int] = None
        self.notetype_ncol_: Optional[int] = None
        self.deck_ncol_: int = 0
        self.tags_ncol_: int = 0

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
        if self.deck_ncol_ > 0:
            guid, notetype, deck_name = line.split(self.sep_)[: self.deck_ncol_]
            attrs["guid"] = guid
            attrs["notetype"] = notetype
            attrs["deck_name"] = deck_name
        front, back, _, _, _, tags = line.split(self.sep_)[self.deck_ncol_ :]
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
            raise NotImplementedError(
                f"Only tab-separated files are supported. Found {sep}"
            )

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
        if "guid" in col_type:
            self.guid_ncol_ = int(n_cols)
        elif "notetype" in col_type:
            self.notetype_ncol_ = int(n_cols)
        elif "deck" in col_type:
            self.deck_ncol_ = int(n_cols)
        elif "tags" in col_type:
            self.tags_ncol_ = int(n_cols)

    def write_txt(self, fpath) -> None:
        with open(fpath, "w") as f:
            f.write(f"#separator:{symbol2sep[self.sep_]}\n")
            f.write(f"#html:{symbol2html[self.html_]}\n")
            if self.guid_ncol_:
                f.write(f"#guid column:{self.guid_ncol_}\n")
            if self.notetype_ncol_:
                f.write(f"#notetype column:{self.notetype_ncol_}\n")
            if self.deck_ncol_:
                f.write(f"#deck column:{self.deck_ncol_}\n")
            if self.tags_ncol_:
                f.write(f"#tags column:{self.tags_ncol_}\n")
            for note in self:
                out = ""
                if self.guid_ncol_:
                    out += f"{note.guid}\t"
                if self.notetype_ncol_:
                    out += f"{note.notetype}\t"
                if self.deck_ncol_:
                    out += f"{note.deck_name}\t"
                out += f"{note.front}\t{note.back}\t\t\t\t"
                if self.tags_ncol_:
                    tags = " ".join(note.tags)
                    out += f"{tags}"
                f.write(f"{out}\n")


sep2symbol = {"tab": "\t"}
symbol2sep = {v: k for k, v in sep2symbol.items()}
html2symbol = {"true": True, "false": False}
symbol2html = {v: k for k, v in html2symbol.items()}
