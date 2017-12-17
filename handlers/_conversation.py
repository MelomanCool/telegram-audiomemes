from enum import Enum, auto

from telegram.ext import ConversationHandler, MessageHandler, Filters, CommandHandler

import model
from converter import convert_to_ogg
from custom_filters import is_in_database, is_audio_document
from model import Meme
from utils import download_file


class States(Enum):
    NAME = auto()


meme_storage = model.get_storage()


def cmd_cancel(_, update):
    update.message.reply_text('Current operation has been canceled.')

    return ConversationHandler.END


def audio_handler(bot, update, user_data):
    message = update.message

    if message.voice is not None:
        meme_file_id = message.voice.file_id

    else:
        message.reply_text('Converting to voice...')

        audio = message.audio or message.document
        audio_file = download_file(bot, audio.file_id)
        meme_file = convert_to_ogg(audio_file)

        response = message.reply_voice(meme_file)
        meme_file_id = response.voice.file_id

    user_data['meme_file_id'] = meme_file_id
    message.reply_text('Okay, now send me the name for the meme.')

    return States.NAME


def name_handler(_, update, user_data):
    message = update.message

    meme_name = message.text.strip()
    file_id = user_data['meme_file_id']

    meme = Meme(
        id=None,  # automatically created by DB
        name=meme_name,
        file_id=file_id,
        owner_id=message.from_user.id,
        times_used=0
    )

    meme_storage.add(meme)
    message.reply_text('Meme has been added.')

    return ConversationHandler.END


conversation = ConversationHandler(
    entry_points=[MessageHandler(
        ~is_in_database & (Filters.audio | Filters.voice | is_audio_document),
        audio_handler,
        pass_user_data=True
    )],

    states={
        States.NAME: [MessageHandler(
            Filters.text,
            name_handler,
            pass_user_data=True
        )]
    },

    fallbacks=[CommandHandler('cancel', cmd_cancel)]
)
