from pathlib import Path
from typing import List, Optional
from uuid import uuid4


class Note:
    def __init__(self, front: str, back: str, tags: Optional[List[str]]) -> None:
        self.uuid = uuid4()
        self.front = front
        self.back = back
        self.tags = tags

    def __repr__(self) -> str:
        return f"Note(uuid={self.uuid}, front={self.front}, back={self.back}, tags={self.tags}"


class Deck:
    def __init__(self, name: str) -> None:
        self.name = name
        self._collection: List = []

    def add(self, note: List[Note]) -> None:
        self._collection.extend(note)

    def from_txt(
        self, fpath: Path, ignore_media: bool = True, verbose: bool = False
    ) -> None:
        with open(fpath) as f:
            for i, line in enumerate(f):
                if ignore_media:
                    if "<img src=" in line:
                        continue
                try:
                    front, back, _, _, _, tags = line.split("\t")

                    # convert tags as a list of str
                    tags = tags.replace("\n", "")
                    tags = list(tags.split(" "))

                    self._collection.append(Note(front=front, back=back, tags=tags))
                except ValueError:
                    if verbose:
                        print(f"Was not able to process line {i}: {line}")

    def __getitem__(self, slice) -> List[Note]:
        return self._collection[slice]

    def __len__(self) -> int:
        return len(self._collection)
