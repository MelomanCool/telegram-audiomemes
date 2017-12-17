import model
from utils import inject_quoted_voice_id

meme_storage = model.get_storage()


@inject_quoted_voice_id
def name(_, update, quoted_voice_id):
    """Returns the name of a meme"""

    message = update.message

    try:
        meme = meme_storage.get_by_file_id(quoted_voice_id)
    except KeyError:
        message.reply_text("I don't know that meme, sorry.")
        return

    message.reply_text(meme.name)
