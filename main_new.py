#!/usr/bin/env python3
"""
Télécharge un morceau / une playlist / les titres d’un artiste SoundCloud.
  • MP3 320 kbps via soundcloudtomp3.biz
  • (optionnel) intégration de l’artwork, du genre et de l’URL source
  • évite les doublons grâce aux tags COMMENT des fichiers existants
"""

import os, re, time, shutil, requests
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, COMM, TCON

from tkinter.filedialog import askdirectory


# ───────────────────────────────
# Config utilisateur
# ───────────────────────────────
HEADLESS = True     # Chrome sans-tête
CLASSIFY = True     # écrire URL & genre dans les tags ID3
ARTWORK  = True     # télécharger et intégrer la pochette

GENRES = [
    "Deep House", "House", "Tech House", "Electro House", "Dance", "Eurodance",
    "Progressive House", "Trance", "Psytrance", "Techno", "Dubstep",
    "Drum & Bass", "Hard Trance", "Hard Techno", "Schranz", "Hardstyle",
    "Rawstyle", "Hardcore", "Hardcore Techno", "Frenchcore", "Uptempo",
    "Speedcore"
]


# ───────────────────────────────
# Selenium helpers
# ───────────────────────────────
def chrome_opts() -> webdriver.ChromeOptions:
    o = webdriver.ChromeOptions()
    if HEADLESS:
        o.add_argument("--headless=new")
        o.add_argument("--window-size=1920,1080")
    o.add_experimental_option("excludeSwitches", ["enable-logging"])
    o.add_argument("--log-level=3")
    return o


# ───────────────────────────────
# Utilitaires généraux
# ───────────────────────────────
def strip_query(url: str) -> str:
    return url.split("?", 1)[0]


def sanitize_filename(name: str) -> str:
    """Supprime les caractères interdits dans un nom de fichier Windows/macOS."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


# ───────────────────────────────
# Scraping SoundCloud
# ───────────────────────────────
def scroll_to_bottom(driver):
    last_h = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_h = driver.execute_script("return document.body.scrollHeight")
        if new_h == last_h:
            break
        last_h = new_h


def playlist_tracks(url: str) -> list[str]:
    drv = webdriver.Chrome(service=Service(log_path=os.devnull), options=chrome_opts())
    drv.get(url)
    WebDriverWait(drv, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.trackList__list"))
    )
    scroll_to_bottom(drv)
    links = drv.find_elements(By.CSS_SELECTOR, "a.trackItem__trackTitle")
    urls = [urljoin("https://soundcloud.com", a.get_attribute("href"))
            for a in links if a.get_attribute("href")]
    drv.quit()
    return list(set(urls))


def artist_tracks(url: str) -> list[str]:
    drv = webdriver.Chrome(service=Service(log_path=os.devnull), options=chrome_opts())
    drv.get(url)
    WebDriverWait(drv, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a.sc-link-primary.soundTitle__title.sc-link-dark.sc-text-h4"))
    )
    scroll_to_bottom(drv)
    links = drv.find_elements(
        By.CSS_SELECTOR, "a.sc-link-primary.soundTitle__title.sc-link-dark.sc-text-h4")
    urls = [urljoin("https://soundcloud.com", a.get_attribute("href"))
            for a in links if a.get_attribute("href")]
    drv.quit()
    return list(set(urls))


def detect_genre(tags: list[str]) -> str | None:
    for g in reversed(GENRES):
        g_cmp = g.replace(" ", "").lower()
        for t in tags:
            if g_cmp in t.replace(" ", "").lower():
                return g
    return None


def scrape_track_meta(url: str) -> tuple[str | None, list[str], str | None, str]:
    """Retourne (artwork_url, tags, genre, title)."""
    drv = webdriver.Chrome(service=Service(log_path=os.devnull), options=chrome_opts())
    drv.get(url)

    art, tags, genre, title = None, [], None, "unknown"

    try:
        # titre
        try:
            title = drv.find_element(By.CSS_SELECTOR,
                                     "h1.soundTitle__title span").text.strip()
        except Exception:
            title = drv.title.split("|")[0].strip()

        # artwork
        span = WebDriverWait(drv, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "div.listenArtworkWrapper span")))
        m = re.search(r'url\(["\']?(.*?)["\']?\)', span.get_attribute("style"))
        if m:
            art = m.group(1)

        if CLASSIFY:
            try:
                btn = drv.find_element(By.CSS_SELECTOR,
                                       "a.truncatedAudioInfo__collapse")
                if btn.is_displayed():
                    drv.execute_script("arguments[0].click();", btn)
                    time.sleep(1.5)
            except Exception:
                pass

            tags_elem = drv.find_elements(By.CSS_SELECTOR, "span.sc-tagContent")
            tags = [e.text for e in tags_elem]
            genre = detect_genre(tags)

    except Exception as exc:
        print("Scrape meta KO :", exc)

    drv.quit()
    return art, tags, genre, title


# ───────────────────────────────
# Téléchargement & ID3
# ───────────────────────────────
def wait_download(folder: str, timeout: int = 300) -> str | None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        files = [f for f in os.listdir(folder)
                 if f.endswith(".mp3") or f.endswith(".crdownload")]
        if not files:
            time.sleep(1); continue
        files.sort(key=lambda f: os.path.getmtime(os.path.join(folder, f)))
        last = files[-1]; full = os.path.join(folder, last)
        if last.endswith(".crdownload"):
            time.sleep(1); continue
        size = os.path.getsize(full); time.sleep(2)
        if size == os.path.getsize(full):
            return full
    return None


def embed_art(mp3: str, img: str):
    audio = MP3(mp3, ID3=ID3)
    audio.add_tags() if audio.tags is None else None
    for k in list(audio.tags.keys()):
        if k.startswith("APIC"):
            del audio.tags[k]
    with open(img, "rb") as f:
        audio.tags.add(APIC(encoding=3, mime="image/jpeg", type=3,
                            desc="Cover", data=f.read()))
    audio.save(v2_version=3)


def embed_url(mp3: str, url: str):
    audio = MP3(mp3, ID3=ID3)
    audio.add_tags() if audio.tags is None else None
    for k in list(audio.tags.keys()):
        if k.startswith("COMM"):
            del audio.tags[k]
    audio.tags.add(COMM(encoding=3, desc="Comment", text=strip_query(url)))
    audio.save(v2_version=3)


def embed_genre(mp3: str, genre: str | None):
    if not genre: return
    audio = MP3(mp3, ID3=ID3)
    if "TCON" not in audio.tags or not audio.tags.get("TCON").text:
        audio.tags.add(TCON(encoding=3, text=genre))
        audio.save(v2_version=3)


def existing_urls(folder: str) -> set[str]:
    seen = set()
    for f in os.listdir(folder):
        if not f.lower().endswith(".mp3"): continue
        try:
            audio = MP3(os.path.join(folder, f), ID3=ID3)
            for k in audio.tags or []:
                if k.startswith("COMM"):
                    seen.add(strip_query(audio.tags[k].text[0]))
        except Exception:
            pass
    return seen


def download_track(url: str, out_dir: str):
    url = strip_query(url)
    print("→", url)

    # scrape meta AVANT téléchargement (titre & artwork)
    art_url, tags, genre, title = scrape_track_meta(url)
    title   = sanitize_filename(title) or "track"
    tmp_drv = webdriver.Chrome(service=Service(log_path=os.devnull),
                               options=chrome_opts())
    tmp_drv.get("https://soundcloudtomp3.biz/index.php")

    # 320 kbps
    r320 = WebDriverWait(tmp_drv, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,
                                    "input[name='quality'][value='320']")))
    tmp_drv.execute_script("arguments[0].click();", r320)

    box = WebDriverWait(tmp_drv, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input.form-control.form-control-lg[name='videoURL']")))
    box.send_keys(url); box.send_keys(Keys.ENTER)

    # ferme éventuelle pub
    time.sleep(1)
    for h in tmp_drv.window_handles[1:]:
        tmp_drv.switch_to.window(h); tmp_drv.close()
    tmp_drv.switch_to.window(tmp_drv.window_handles[0])

    dl_link = WebDriverWait(tmp_drv, 300).until(
        EC.element_to_be_clickable((By.XPATH,
                                    "//a[contains(@class,'btn btn-success') and contains(.,'Download your MP3 file')]")))
    dl_link.click()

    dl_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    src = wait_download(dl_folder)
    if not src:
        print("⚠️  Timeout :", url); tmp_drv.quit(); return
    dst = os.path.join(out_dir, f"{title}.mp3")
    shutil.move(src, dst)
    print("✅", dst)

    # artwork + tags
    if ARTWORK and art_url:
        try:
            img_path = os.path.join(out_dir, f"{title}.jpg")
            with requests.get(art_url, stream=True, timeout=20) as r:
                if r.status_code == 200:
                    with open(img_path, "wb") as f:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)
                    embed_art(dst, img_path)
                    os.remove(img_path)
        except Exception as exc:
            print("Artwork KO :", exc)

    if CLASSIFY:
        embed_url(dst, url)
        embed_genre(dst, genre)

    tmp_drv.quit()


# ───────────────────────────────
# Main
# ───────────────────────────────
if __name__ == "__main__":
    sc = input("URL SoundCloud (playlist, /tracks, ou piste) : ").strip()
    print("Choisissez le dossier de sortie…")
    out = askdirectory(title="Dossier destination")
    os.makedirs(out, exist_ok=True)

    parts = [p for p in urlparse(sc).path.split("/") if p]
    if len(parts) > 1 and parts[1].lower() == "sets":
        targets = playlist_tracks(sc)
    elif parts and parts[-1].lower() in ("tracks", "popular-tracks"):
        targets = artist_tracks(sc)
    else:
        targets = [sc]

    print(f"{len(targets)} piste(s) détectée(s)")
    done = existing_urls(out)
    for t in targets:
        if strip_query(t) in done:
            print("• déjà présent", t)
            continue
        download_track(t, out)