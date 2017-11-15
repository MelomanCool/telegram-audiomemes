from telegram.ext import BaseFilter
from pathlib import Path


class IsMeme(BaseFilter):
    def __init__(self, storage):
        self.storage = storage

    def filter(self, message):
        return (message.voice is not None
                and message.voice.file_id in self.storage)


class IsAudioDocument(BaseFilter):
    EXTENSIONS = ('.mp3', '.ogg')

    def filter(self, message):
        return (message.document is not None
                and Path(message.document.file_name).suffix in self.EXTENSIONS)
