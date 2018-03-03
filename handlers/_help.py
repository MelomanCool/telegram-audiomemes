def help_(_, update):
    update.message.reply_text(
        'This bot can remember audiomemes to help you find them more easily.\n'
        '\n'
        'To add a meme, just send it here. After adding, you can reply to it'
        ' with commands — /name, /rename and /delete.\n'
        '\n'
        'There is also a command /my, which will show you a list of your memes.'
    )