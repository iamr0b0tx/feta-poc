import time

from fastapi import Depends
from pydantic import BaseModel

from feta.blocks import Blocks
from feta.contributor import Contributor
from feta.dependencies import get_blocks
from feta.router import make_router


class Note(BaseModel):
    text: str
    timestamp: int


class NoteManager:
    def __init__(self, contributor: Contributor):
        self.__contributor = contributor

    def create_note(self, text):
        note = Note(text=text, timestamp=time.time_ns())
        return self.__contributor.blocks.create_block(note.json(), self.__contributor.id)

    def get_note(self, idx):
        return self.__contributor.blocks.retrieve_block(idx, self.__contributor.id)


PRINCIPAL = "hdts5ws8djdeytd"
PRINCIPAL_NAME = "Notes"
router = make_router(PRINCIPAL, PRINCIPAL_NAME, "notes")

_contributor = None


def get_contributor(blocks: Blocks = Depends(get_blocks)):
    global _contributor
    if _contributor is None:
        _contributor = Contributor(blocks, PRINCIPAL)
    return _contributor


_note_manager = None


def get_note_manager(contributor: Contributor = Depends(get_contributor)):
    global _note_manager
    if _note_manager is None:
        _note_manager = NoteManager(contributor)
    return _note_manager


@router.get("/{note_id}")
async def get_note(note_id: str, note_manager: NoteManager = Depends(get_note_manager)):
    return note_manager.get_note(note_id)


@router.post("/")
async def create_note(text: str, note_manager: NoteManager = Depends(get_note_manager)):
    return note_manager.create_note(text)
