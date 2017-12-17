from uuid import uuid4

from telegram import InlineQueryResultCachedVoice

import model
from inline_results_storage import InlineResultsRingBuffer
import logzero

logger = logzero.setup_logger(__name__)

meme_storage = model.get_storage()
inline_results_by_id = InlineResultsRingBuffer(limit=1000)


def inlinequery(_, update):
    query = update.inline_query.query
    logger.info('Inline query: %s', query)

    if query:
        memes = meme_storage.find(query, max_count=20)
    else:
        memes = meme_storage.get_most_popular(max_count=20)

    results = []
    for meme in memes:
        id_ = uuid4()
        results.append(InlineQueryResultCachedVoice(
            id_, meme.file_id, title=meme.name
        ))
        inline_results_by_id.add(str(id_), meme.file_id,
                                 update.inline_query.from_user.id)

    update.inline_query.answer(results, cache_time=0)


def chosen_inline_result(_, update):
    try:
        file_id = inline_results_by_id.get(update.chosen_inline_result.result_id)
    except KeyError:
        logger.warning("Can't find result in cache. You should increase cache size.")
        return

    meme_storage.inc_times_used(file_id)
