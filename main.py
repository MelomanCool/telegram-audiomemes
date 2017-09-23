import logging
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from itertools import islice

from telegram import Update, Message, Bot, ParseMode, InlineQueryResultCachedVoice
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, InlineQueryHandler

from config import TOKEN
from contexts import get_user_context
from converter import convert_to_ogg
from model import MemeStorage, Meme


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

AUDIO, NAME = range(2)

meme_storage = MemeStorage('memes')


def cmd_cancel(bot, update):
    update.message.reply_text('Current operation has been canceled.')

    return ConversationHandler.END


def cmd_add(bot, update):
    update.message.reply_text('Okay, send me an audio.')

    return AUDIO


def audio_handler(bot: Bot, update: Update):
    message = update.message  # type: Message

    if message.audio is not None:
        message.reply_text('Converting audio to voice...', quote=False)

        audio_info = bot.get_file(message.audio.file_id)
        audio_file = BytesIO()
        audio_info.download(out=audio_file)
        audio_file.seek(0)

        voice_file = convert_to_ogg(audio_file)
        response = message.reply_voice(voice_file, quote=False)  # type: Message
        file_id = response.voice.file_id

    elif message.document is not None and Path(message.document.file_name).suffix in ('.mp3', '.ogg'):
        message.reply_text('Converting document to voice...', quote=False)

        doc_info = bot.get_file(message.document.file_id)
        doc_file = BytesIO()
        doc_info.download(out=doc_file)
        doc_file.seek(0)

        voice_file = convert_to_ogg(doc_file)
        response = message.reply_voice(voice_file, quote=False)
        file_id = response.voice.file_id

    elif message.voice is not None:
        file_id = message.voice.file_id

    else:
        message.reply_text('An error occured.')
        raise ValueError('Message does not contain Audio or Voice.')

    context = get_user_context(message.from_user.id)
    context['meme_file_id'] = file_id
    message.reply_text('Okay, now send me the name for the meme.')

    return NAME


def name_handler(bot: Bot, update: Update):
    message = update.message

    meme_name = message.text.strip()
    context = get_user_context(message.from_user.id)
    file_id = context['meme_file_id']

    meme = Meme(
        name=meme_name,
        file_id=file_id,
        owner=message.from_user.id
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

    if meme.owner != message.from_user.id:
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
        entry_points=[MessageHandler(Filters.audio | Filters.voice | Filters.document, audio_handler)],

        states={
            NAME: [MessageHandler(Filters.text, name_handler)]
        },

        fallbacks=[CommandHandler('cancel', cmd_cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('name', cmd_name))
    dp.add_handler(CommandHandler('delete', cmd_delete))
    dp.add_handler(CommandHandler('rename', cmd_rename, pass_args=True))
    dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
