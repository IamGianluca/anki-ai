from typing import List, Optional

from pydantic import BaseModel


class Note(BaseModel):
    guid: str
    front: str
    back: str
    tags: Optional[List[str]] = None
    notetype: Optional[str] = None
    deck_name: Optional[str] = None

    def to_file_str(self) -> str:
        tags_str = "" if not self.tags else " ".join(self.tags)
        return f"{self.guid}\t{self.notetype}\t{self.deck_name}\t{self.front}\t{self.back}\t\t\t\t{tags_str}\n"


class NoteChanges(BaseModel):
    front: str
    back: str
    tags: Optional[List[str]] = None
