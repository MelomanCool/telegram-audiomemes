from telegram.ext import BaseFilter
from pathlib import Path

import model


class IsInDatabase(BaseFilter):
    def __init__(self, storage):
        self.storage = storage

    def filter(self, message):
        return (message.voice is not None
                and self.storage.has_meme_with_file_id(message.voice.file_id))


class IsAudioDocument(BaseFilter):
    EXTENSIONS = ('.mp3', '.ogg')

    def filter(self, message):
        return (message.document is not None
                and Path(message.document.file_name).suffix in self.EXTENSIONS)


is_audio_document = IsAudioDocument()
is_in_database = IsInDatabase(storage=model.get_storage())
