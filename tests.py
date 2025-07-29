from pathlib import Path
from mutagen.id3 import ID3, ID3NoHeaderError, COMM, Encoding

def set_comment(mp3_path, text):
    mp3_path = Path(mp3_path)
    try:
        tags = ID3(mp3_path)
    except ID3NoHeaderError:
        tags = ID3()
    tags.delall('COMM')
    tags.add(COMM(encoding=Encoding.UTF16, lang='eng', desc='', text=text))
    tags.save(mp3_path, v1=0, v2_version=3)  # pas d’ID3v1, ID3 v2.3

set_comment(r'/Volumes/MUSIC/Music_thomas/Hard trance/01 Funk Tribu - Viento Extended Mix ARTCORE Records.mp3', 'This is a test comment.')