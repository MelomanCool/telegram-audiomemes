from io import BytesIO
from functools import wraps


def download_file(bot, file_id):
    f = BytesIO()
    info = bot.get_file(file_id)
    info.download(out=f)
    f.seek(0)
    return f


def requires_quoted_meme(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        quoted_message = update.message.reply_to_message
        if not quoted_message or not quoted_message.voice:
            update.message.reply_text('You should reply to a meme with this command.')
            return
        return func(bot, update, *args, **kwargs)
    return wrapped
