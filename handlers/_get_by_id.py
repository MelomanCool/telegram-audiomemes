import model

meme_storage = model.get_storage()


def get_by_id(_, update, groupdict):
    """Sends meme by id"""

    try:
        meme = meme_storage.get(groupdict['id'])
    except KeyError:
        update.message.reply_text("I don't have meme with that ID, sorry")
        return

    update.message.reply_voice(meme.file_id)
