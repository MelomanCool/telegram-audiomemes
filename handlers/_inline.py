from datetime import datetime, timedelta

from telegram import InlineQueryResultCachedVoice

import model
import logzero

logger = logzero.setup_logger(__name__)

meme_storage = model.get_storage()

PAGE_SIZE = 50

# results that have more than PAGE_SIZE items, by query
large_results = {}


def filter_old_results(results):
    now = datetime.now()
    return {q:res for q,res in results.items()
            if res['expires'] > now}


def save_result(results, query, res):
    new_results = results.copy()
    new_results[query] = {'items': res,
                          'expires': datetime.now() + timedelta(minutes=5)}
    return new_results


def get_result(results, query):
    return results[query]['items']


def inlinequery(_, update):
    global large_results

    inl_q = update.inline_query
    query = inl_q.query
    offset = int(inl_q.offset) if inl_q.offset else 0

    if offset == 0 or query not in large_results:
        if query:
            memes = meme_storage.find(query)
        else:
            memes = meme_storage.get_most_popular()

        if len(memes) > PAGE_SIZE:
            large_results = save_result(large_results, query, memes)

    else:
        memes = get_result(large_results, query)

    large_results = filter_old_results(large_results)

    have_next_page = bool(len(memes) - offset > PAGE_SIZE)
    next_offset=str(offset+PAGE_SIZE) if have_next_page else ''
    logger.info('Query: %s, items: %s, offset: %d, has next page: %d, next offset: %s',
                query, len(memes), offset, have_next_page, next_offset)

    results = [
        InlineQueryResultCachedVoice(meme.id, meme.file_id, title=meme.name)
        for meme in memes[offset:offset+PAGE_SIZE]
    ]
    update.inline_query.answer(results, cache_time=0, next_offset=next_offset)


def chosen_inline_result(_, update):
    meme_storage.inc_times_used(update.chosen_inline_result.result_id)
