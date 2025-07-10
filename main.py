import os, re, time, shutil, requests
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, COMM, TCON, TPE1

from tkinter.filedialog import askdirectory

HEADLESS = True
CLASSIFY = True
ARTWORK  = True

styles = [
    "Deep House", "House", "Tech House", "Electro House", "Dance", "Eurodance",
    "Progressive House", "Trance", "Psytrance", "Techno", "Dubstep",
    "Drum & Bass", "Hard Trance", "Hard Techno", "Schranz", "Hardstyle",
    "Rawstyle", "Hardcore", "Hardcore Techno", "Frenchcore", "Uptempo",
    "Speedcore"
]

# ───────────────────────────────
# Selenium / Chrome
# ───────────────────────────────
def create_chrome_opts():
    opts = webdriver.ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1920,1080")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.add_argument("--log-level=3")
    return opts


# ───────────────────────────────
# Aide à la détection du genre
# ───────────────────────────────
def get_genre_from_tags(track_tags, style_list):
    for style in reversed(style_list):
        if style.replace(" ", "").lower() in [t.replace(" ", "").lower() for t in track_tags]:
            return style
    return None


# ───────────────────────────────
# Scrolling utilitaire
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


# ───────────────────────────────
# Collecte des URLs depuis SC
# ───────────────────────────────
def fetch_playlist_urls(playlist_url):
    print("🔎 Analyse de la playlist…")
    driver = webdriver.Chrome(
        service=Service(log_path=os.devnull),
        options=create_chrome_opts()
    )
    driver.get(playlist_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.trackList__list"))
    )
    scroll_to_bottom(driver)

    urls = list(
        {
            urljoin("https://soundcloud.com", e.get_attribute("href"))
            for e in driver.find_elements(By.CSS_SELECTOR, "a.trackItem__trackTitle")
            if e.get_attribute("href")
        }
    )
    driver.quit()
    print(f"  → {len(urls)} titre(s) trouvé(s) dans la playlist")
    return urls


def fetch_artist_tracks(artist_url):
    print("🔎 Analyse de la page artiste…")
    driver = webdriver.Chrome(
        service=Service(log_path=os.devnull),
        options=create_chrome_opts()
    )
    driver.get(artist_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a.sc-link-primary.soundTitle__title.sc-link-dark.sc-text-h4")
        )
    )
    scroll_to_bottom(driver)

    urls = list(
        {
            urljoin("https://soundcloud.com", e.get_attribute("href"))
            for e in driver.find_elements(
                By.CSS_SELECTOR, "a.sc-link-primary.soundTitle__title.sc-link-dark.sc-text-h4"
            )
            if e.get_attribute("href")
        }
    )
    driver.quit()
    print(f"  → {len(urls)} titre(s) public(s) trouvé(s) chez l’artiste")
    return urls


# ───────────────────────────────
# Surveillance du téléchargement
# ───────────────────────────────
def wait_for_mp3_download(folder, timeout=300):
    end = time.time() + timeout
    while time.time() < end:
        files = [f for f in os.listdir(folder) if f.endswith((".mp3", ".crdownload"))]
        if not files:
            time.sleep(1)
            continue
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))
        latest = files[-1]
        path = os.path.join(folder, latest)
        if latest.endswith(".crdownload"):
            time.sleep(1)
            continue
        size1 = os.path.getsize(path)
        time.sleep(2)
        if size1 == os.path.getsize(path):
            return path
    return None


# ───────────────────────────────
# Récupération cover + tags
# ───────────────────────────────
def fetch_artwork_and_tags(track_url):
    driver = webdriver.Chrome(
        service=Service(log_path=os.devnull),
        options=create_chrome_opts()
    )
    driver.get(track_url)
    artwork_url, tags, determined_genre, artist = None, [], None, None
    try:
        elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.listenArtworkWrapper span"))
        )
        m = re.search(r'url\(["\']?(.*?)["\']?\)', elem.get_attribute("style"))
        if m:
            artwork_url = m.group(1)

        # Récupération de l'artiste
        try:
            artist_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.soundTitle__usernameHeroContainer h2.soundTitle__username a"))
            )
            artist = artist_elem.text.strip()
            print(f"    • artiste : {artist}")
        except Exception:
            print("    • artiste : non trouvé")

        if CLASSIFY:
            try:
                try:
                    cookie_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                    )
                    cookie_btn.click()
                    time.sleep(2)
                except Exception:
                    pass  
                
                more = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.truncatedAudioInfo__collapse"))
                )
                if more.is_displayed():
                    driver.execute_script("arguments[0].click();", more)
                    time.sleep(2)
            except Exception:
                pass

            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, "a.sc-tag-medium span.sc-tagContent") or 
                             d.find_elements(By.CSS_SELECTOR, "a.sc-tag-large span.sc-tagContent")
                )

                tags = []
                tags.extend([g.text for g in driver.find_elements(By.CSS_SELECTOR, "a.sc-tag-medium span.sc-tagContent")])
                tags.extend([g.text for g in driver.find_elements(By.CSS_SELECTOR, "a.sc-tag-large span.sc-tagContent")])

                tags = list(set(tags))
                determined_genre = get_genre_from_tags(tags, styles)
            except Exception:
                tags = []
                determined_genre = None

            print(f"    • tags SC : {tags or '—'}")
            if determined_genre:
                print(f"    • genre  : {determined_genre}")

    except Exception as ex:
        print("⚠️ Impossible de récupérer l'artwork / tags :", ex)
    finally:
        driver.quit()

    return artwork_url, tags, determined_genre, artist


def download_cover(track_url, mp3_name, out_folder):
    art_url, sc_tags, det_genre, artist = fetch_artwork_and_tags(track_url)
    if not art_url:
        print("    • aucune pochette détectée")
        return None, sc_tags, det_genre, artist

    try:
        r = requests.get(art_url, stream=True, timeout=20)
        if r.status_code == 200:
            img_path = os.path.join(out_folder, f"{os.path.splitext(mp3_name)[0]}.jpg")
            with open(img_path, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print("    • pochette téléchargée")
            return img_path, sc_tags, det_genre, artist
    except Exception as e:
        print("⚠️ Erreur téléchargement cover :", e)
    return None, sc_tags, det_genre, artist


# ───────────────────────────────
# Écriture ID3
# ───────────────────────────────
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


# ───────────────────────────────
# Détection doublons
# ───────────────────────────────
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


# ───────────────────────────────
# Téléchargement d’une piste
# ───────────────────────────────
def process_track_item(track_url, out_folder):
    track_url = track_url.split("?")[0]
    print(f"▶ Téléchargement : {track_url}")

    driver = webdriver.Chrome(
        service=Service(log_path=os.devnull),
        options=create_chrome_opts()
    )
    driver.get("https://soundcloudtomp3.biz/index.php")

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='quality'][value='320']"))
    ).click()

    input_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input.form-control.form-control-lg[name='videoURL']")
        )
    )
    input_box.clear()
    input_box.send_keys(track_url)
    input_box.send_keys(Keys.ENTER)
    print("    • URL soumise pour conversion")

    # ferme éventuelles pop-ups
    time.sleep(1)
    for h in driver.window_handles[1:]:
        driver.switch_to.window(h)
        driver.close()
    driver.switch_to.window(driver.window_handles[0])

    btn = WebDriverWait(driver, 300).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@class,'btn btn-success') and contains(.,'Download your MP3 file')]")
        )
    )
    btn.click()

    dl_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    src = wait_for_mp3_download(dl_folder)
    if not src:
        print("⚠️ Timeout téléchargement")
        driver.quit()
        return

    mp3_name = os.path.basename(src).replace("_", " ")
    dst = os.path.join(out_folder, mp3_name)
    shutil.move(src, dst)
    print(f"    • MP3 enregistré sous : {mp3_name}")

    art_path, sc_tags, det_genre, artist = None, [], None, None
    if ARTWORK or CLASSIFY:
        art_path, sc_tags, det_genre, artist = download_cover(track_url, mp3_name, out_folder)

    if art_path and ARTWORK:
        add_cover(dst, art_path)
        os.remove(art_path)
        print("    • pochette intégrée au MP3")

    if CLASSIFY:
        add_url_comment(dst, track_url)
        print("    • URL ajoutée au MP3")
        add_genre(dst, det_genre)

    # Add artist tag
    if artist:
        add_artist(dst, artist)
        print("    • artiste ajouté au MP3")

    driver.quit()
    print("✔️ Terminé\n")


# ───────────────────────────────
# Programme principal
# ───────────────────────────────
if __name__ == "__main__":
    input_url = input("URL SoundCloud (piste, playlist, artiste) : ").strip()
    print("⬇️  Choisissez le dossier de destination…")
    output_folder = askdirectory(title="Dossier où télécharger les musiques")
    if not output_folder:
        print("Aucun dossier sélectionné, sortie.")
        exit()

    path_parts = [p for p in urlparse(input_url).path.split("/") if p]
    if len(path_parts) > 1 and path_parts[1].lower() == "sets":
        urls = fetch_playlist_urls(input_url)
    elif path_parts and path_parts[-1].lower() in ("tracks", "popular-tracks"):
        urls = fetch_artist_tracks(input_url)
    else:
        urls = [input_url]

    print(f"🎧 {len(urls)} piste(s) à traiter")
    already = get_already_downloaded_tracks(output_folder)

    for u in urls:
        base = u.split("?")[0]
        if base in already:
            print(f"• déjà présent, on ignore : {u}")
            continue
        process_track_item(u, output_folder)