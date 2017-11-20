import shelve
import logging

from fuzzywuzzy import fuzz, process

from .meme import Meme
from .exceptions import Unauthorized


logger = logging.getLogger(__name__)


class MemeStorage(object):

    def __init__(self, filename):
        self.memes = shelve.open(filename, writeback=True)

    def add(self, new_meme: Meme):
        self.memes[new_meme.file_id] = new_meme
        self.memes.sync()

    def delete(self, meme, from_user_id):
        """Delete a meme by id or a Meme object"""
        if isinstance(meme, Meme):
            file_id = meme.file_id
        else:
            file_id = meme

        if from_user_id != self.memes[file_id].owner_id:
            raise Unauthorized

        del self.memes[file_id]
        self.memes.sync()

    def rename(self, meme, new_name, from_user_id):
        self.delete(meme, from_user_id)
        self.add(Meme(
            name=new_name,
            file_id=meme.file_id,
            owner_id=meme.owner_id
        ))

    def find(self, keywords):
        keywords = [word.lower() for word in keywords]

        logger.debug('Searching with keywords: %s', keywords)

        return [
            meme for meme in self.memes.values()
            if any(keyword in meme.name.lower() for keyword in keywords)
        ]

    def __contains__(self, file_id):
        return file_id in self.memes

    def new_find(self, search_query):
        scored_matches = process.extractBests(search_query, self.get_all(),
                                              key=lambda meme: meme.name,
                                              scorer=fuzz.token_set_ratio,
                                              limit=None,
                                              score_cutoff=30)

        if not scored_matches:
            return []

        matches, _ = zip(*scored_matches)
        return matches

    def get(self, file_id):
        """Get a meme by it's file_id"""

        return self.memes[file_id]

    def get_all(self):
        """Returns all memes"""

        return self.memes.values()
