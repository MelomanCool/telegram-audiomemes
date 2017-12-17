import model
from model.exceptions import Unauthorized
from utils import inject_quoted_voice_id

meme_storage = model.get_storage()


@inject_quoted_voice_id
def rename(_, update, args, quoted_voice_id):
    """Changes the name of the meme"""

    message = update.message
    new_name = ' '.join(args)

    if not new_name:
        message.reply_text('Usage: /rename <i>new name</i>',
                           parse_mode='HTML')
        return

    try:
        meme = meme_storage.get_by_file_id(quoted_voice_id)
    except KeyError:
        message.reply_text("Sorry, I don't know that meme.")
        return

    try:
        meme_storage.rename(meme.id, new_name, message.from_user.id)
    except Unauthorized:
        message.reply_text("Sorry, you can only rename the memes you added yourself.")
        return

    message.reply_text('The meme has been renamed to "{}"'.format(new_name))
