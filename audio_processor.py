import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, COMM, TCON, TPE1


def add_cover(mp3_path, art_path):
    audio = MP3(mp3_path, ID3=ID3)
    audio.add_tags() if audio.tags is None else None
    for k in list(audio.tags.keys()):
        if k.startswith("APIC"):
            del audio.tags[k]
    with open(art_path, "rb") as img:
        audio.tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=img.read()))
    audio.save(v2_version=3)


def add_url_comment(mp3_path, url):
    audio = MP3(mp3_path, ID3=ID3)
    audio.add_tags() if audio.tags is None else None
    for k in list(audio.tags.keys()):
        if k.startswith("COMM"):
            del audio.tags[k]
    audio.tags.add(COMM(encoding=3, desc="Comment", text=url.split("?")[0]))
    audio.save(v2_version=3)


def add_genre(mp3_path, genre):
    if not genre:
        return
    audio = MP3(mp3_path, ID3=ID3)
    if "TCON" not in audio.tags or not audio.tags.get("TCON").text:
        audio.tags.add(TCON(encoding=3, text=genre))
        audio.save(v2_version=3)


def add_artist(mp3_path, artist):
    if not artist:
        return
    audio = MP3(mp3_path, ID3=ID3)
    audio.add_tags() if audio.tags is None else None
    audio.tags.add(TPE1(encoding=3, text=artist))
    audio.save(v2_version=3)


def get_already_downloaded_tracks(out_folder):
    urls = set()
    for f in os.listdir(out_folder):
        if not f.lower().endswith(".mp3"):
            continue
        try:
            audio = MP3(os.path.join(out_folder, f), ID3=ID3)
            for k in audio.tags or []:
                if k.startswith("COMM"):
                    urls.add(audio.tags[k].text[0].split("?")[0])
        except Exception:
            pass
    return urls
