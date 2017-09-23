import shelve
import logging

from fuzzywuzzy import fuzz, process

from .meme import Meme


logger = logging.getLogger(__name__)


class MemeStorage(object):

    def __init__(self, filename):
        self.memes = shelve.open(filename, writeback=True)

    def add(self, new_meme: Meme):
        self.memes[new_meme.file_id] = new_meme
        self.memes.sync()

    def delete(self, meme):
        """Delete a meme by id or a Meme object"""
        if isinstance(meme, Meme):
            file_id = meme.file_id
        else:
            file_id = meme

        del self.memes[file_id]
        self.memes.sync()

    def rename(self, meme, new_name):
        assert meme.file_id in self.memes

        self.delete(meme)
        self.add(Meme(
            name=new_name,
            file_id=meme.file_id,
            owner=meme.owner
        ))

    def find(self, keywords):
        keywords = [word.lower() for word in keywords]

        logger.debug('Searching with keywords: %s', keywords)

        return [
            meme for meme in self.memes.values()
            if any(keyword in meme.name.lower() for keyword in keywords)
        ]

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
