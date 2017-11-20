import logging
from uuid import uuid4
from itertools import islice

from telegram import Update, Message, Bot, ParseMode, InlineQueryResultCachedVoice
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, InlineQueryHandler

from config import TOKEN
from converter import convert_to_ogg
from model import MemeStorage, Meme
from utils import download_file
from custom_filters import IsMeme, IsAudioDocument


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

NAME = 1

meme_storage = MemeStorage('memes')

is_meme = IsMeme(meme_storage)
is_audio_document = IsAudioDocument()


def cmd_cancel(bot, update):
    update.message.reply_text('Current operation has been canceled.')

    return ConversationHandler.END


def meme_handler(bot, update):
    """Handles known memes, returns their names"""
    meme = meme_storage.get(update.message.voice.file_id)
    update.message.reply_text('Name: "{}"'.format(meme.name))


def audio_handler(bot: Bot, update: Update, user_data):
    message = update.message  # type: Message

    if message.voice is not None:
        meme_file_id = message.voice.file_id

    else:
        message.reply_text('Converting to voice...', quote=False)

        audio = message.audio or message.document
        audio_file = download_file(bot, audio.file_id)
        meme_file = convert_to_ogg(audio_file)

        response = message.reply_voice(meme_file, quote=False)  # type: Message
        meme_file_id = response.voice.file_id

    user_data['meme_file_id'] = meme_file_id
    message.reply_text('Okay, now send me the name for the meme.')

    return NAME


def name_handler(bot: Bot, update: Update, user_data):
    message = update.message

    meme_name = message.text.strip()
    file_id = user_data['meme_file_id']

    meme = Meme(
        name=meme_name,
        file_id=file_id,
        owner_id=message.from_user.id
    )

    meme_storage.add(meme)
    message.reply_text('Meme has been added.')

    return ConversationHandler.END


def cmd_name(bot, update):
    """Returns the name of a meme"""

    message = update.message  # type: Message
    quoted_message = message.reply_to_message  # type: Message

    if not quoted_message or not quoted_message.voice:
        message.reply_text('You should reply to a meme with this command.')
        return

    try:
        meme = meme_storage.get(quoted_message.voice.file_id)
    except KeyError:
        message.reply_text("I don't know that meme, sorry.", quote=False)
        return

    message.reply_text(meme.name, quote=False)


def cmd_delete(bot, update):
    """Deletes a meme by voice file"""

    message = update.message
    quoted_message = message.reply_to_message

    if not quoted_message or not quoted_message.voice:
        message.reply_text('You should reply to a meme with this command.')
        return

    try:
        meme = meme_storage.get(quoted_message.voice.file_id)
    except KeyError:
        message.reply_text("I don't know that meme, sorry.", quote=False)
        return

    if meme.owner_id != message.from_user.id:
        message.reply_text("Sorry, you can only delete the memes you added yourself.", quote=False)

    meme_storage.delete(meme)
    message.reply_text('The meme "{name}" has been deleted.'.format(name=meme.name), quote=False)


def inlinequery(bot, update):
    query = update.inline_query.query
    logger.info('Inline query: %s', query)

    if query:
        memes = meme_storage.new_find(query)
    else:
        memes = meme_storage.get_all()

    memes = islice(memes, 10)
    results = [
        InlineQueryResultCachedVoice(uuid4(), meme.file_id, title=meme.name)
        for meme in memes
    ]

    update.inline_query.answer(results, cache_time=0)


def cmd_rename(bot, update, args):
    """Changes the name of the meme"""

    message = update.message
    quoted_message = message.reply_to_message
    new_name = ' '.join(args)

    if not new_name:
        message.reply_text('Usage: /rename <i>new name</i>',
                           parse_mode=ParseMode.HTML)
        return

    if not quoted_message or not quoted_message.voice:
        message.reply_text('You should reply to a meme with this command.', quote=False)
        return

    try:
        meme = meme_storage.get(quoted_message.voice.file_id)
    except KeyError:
        message.reply_text("Sorry, I don't know that meme.", quote=False)
        return

    meme_storage.rename(meme, new_name)
    message.reply_text('The meme has been renamed to "{}"'.format(new_name))


def error_handler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(
            ~is_meme & (Filters.audio | Filters.voice | is_audio_document),
            audio_handler,
            pass_user_data=True
        )],

        states={
            NAME: [MessageHandler(
                Filters.text,
                name_handler,
                pass_user_data=True
            )]
        },

        fallbacks=[CommandHandler('cancel', cmd_cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(is_meme, meme_handler))
    dp.add_handler(CommandHandler('name', cmd_name))
    dp.add_handler(CommandHandler('delete', cmd_delete))
    dp.add_handler(CommandHandler('rename', cmd_rename, pass_args=True))
    dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
