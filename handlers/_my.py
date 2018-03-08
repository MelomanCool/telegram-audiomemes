from utils import chunks
import model

meme_storage = model.get_storage()


def my(_, update):
    """Prints memes added by user"""

    message = update.message
    user_id = update.message.from_user.id

    memes = meme_storage.get_for_owner(user_id)

    for chunk in chunks(memes, 20):
        text = '\n\n'.join(
            '<b>{meme.name}</b>\n'
            'Times used: {meme.times_used}\n'
            '/{meme.id}'
            .format(meme=meme)
            for meme in chunk
        )
        message.reply_text(text, parse_mode='HTML')
