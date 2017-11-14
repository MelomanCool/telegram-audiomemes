from pydub import AudioSegment
from io import BytesIO


def convert_to_ogg(f):
    bio = BytesIO()

    (AudioSegment.from_file(f)
                 .set_channels(1)  # for compatibility with Android
                 .export(bio, format='ogg', codec='libopus'))
    bio.seek(0)

    return bio
