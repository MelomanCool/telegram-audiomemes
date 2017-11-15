from io import BytesIO


def download_file(bot, file_id):
    f = BytesIO()
    info = bot.get_file(file_id)
    info.download(out=f)
    f.seek(0)
    return f
