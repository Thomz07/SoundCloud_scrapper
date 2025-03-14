import os
import time
import shutil
import re
import requests
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, COMM, TCON
from tkinter import Tk
from tkinter.filedialog import askdirectory

HEADLESS = True
CLASSIFY = True
ARTWORK = True

styles = [
    "Deep House",
    "House",
    "Tech House",
    "Electro House",
    "Dance",
    "Eurodance",
    "Progressive House",
    "Trance",
    "Psytrance",
    "Techno",
    "Dubstep",
    "Drum & Bass",
    "Hard Trance",
    "Hard Techno",
    "Schranz",
    "Hardstyle",
    "Rawstyle",
    "Hardcore",
    "Hardcore Techno",
    "Frenchcore",
    "Uptempo",
    "Speedcore"
]

def create_chrome_opts():
    opts = webdriver.ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.add_argument("--log-level=3")
    return opts

def get_genre_from_tags(track_tags, style_list):
    for style in reversed(style_list):
        normalized_style = style.replace(" ", "").lower()
        for tag in track_tags:
            normalized_tag = tag.replace(" ", "").lower()
            if normalized_style in normalized_tag:
                return style
    return None

def fetch_playlist_urls(playlist_url):
    opts = create_chrome_opts()
    service = Service(log_path=os.devnull)
    driver = webdriver.Chrome(service=service, options=opts)
    driver.get(playlist_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.trackList__list")))
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    elems = driver.find_elements(By.CSS_SELECTOR, "a.trackItem__trackTitle")
    urls = []
    for e in elems:
        href = e.get_attribute("href")
        if href:
            urls.append(urljoin("https://soundcloud.com", href))
    driver.quit()
    return list(set(urls))

def fetch_artist_tracks(artist_url):
    opts = create_chrome_opts()
    service = Service(log_path=os.devnull)
    driver = webdriver.Chrome(service=service, options=opts)
    driver.get(artist_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.sc-link-primary.soundTitle__title.sc-link-dark.sc-text-h4"))
    )
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    elems = driver.find_elements(By.CSS_SELECTOR, "a.sc-link-primary.soundTitle__title.sc-link-dark.sc-text-h4")
    urls = []
    for e in elems:
        href = e.get_attribute("href")
        if href:
            urls.append(urljoin("https://soundcloud.com", href))
    driver.quit()
    return list(set(urls))

def wait_for_mp3_download(folder, timeout=300):
    end = time.time() + timeout
    while time.time() < end:
        try:
            files = [f for f in os.listdir(folder) if os.path.exists(os.path.join(folder, f))]
        except Exception:
            time.sleep(1)
            continue
        if not files:
            time.sleep(1)
            continue
        try:
            files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))
        except Exception:
            time.sleep(1)
            continue
        latest = files[-1]
        path = os.path.join(folder, latest)
        if latest.endswith(".crdownload"):
            time.sleep(1)
            continue
        elif latest.endswith(".mp3"):
            try:
                s1 = os.path.getsize(path)
                time.sleep(2)
                s2 = os.path.getsize(path)
                if s1 == s2:
                    return path
                else:
                    continue
            except Exception:
                time.sleep(1)
                continue
        else:
            time.sleep(1)
    return None

def fetch_artwork_and_tags(track_url):
    opts = create_chrome_opts()
    service = Service(log_path=os.devnull)
    driver = webdriver.Chrome(service=service, options=opts)
    driver.get(track_url)
    artwork_url = None
    tags = []
    determined_genre = None
    try:
        elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.listenArtworkWrapper span"))
        )
        style_txt = elem.get_attribute("style")
        match = re.search(r'url\(["\']?(.*?)["\']?\)', style_txt)
        if match:
            artwork_url = match.group(1)
        if CLASSIFY:
            try:
                collapse_btn = driver.find_element(By.CSS_SELECTOR, "a.truncatedAudioInfo__collapse")
                if collapse_btn.is_displayed() and collapse_btn.text.strip().lower() in ["afficher plus", "show more"]:
                    collapse_btn.click()
                    time.sleep(3)
            except Exception:
                pass
            genre_elems = driver.find_elements(By.CSS_SELECTOR, "span.sc-tagContent")
            tags = [g.text for g in genre_elems]
            print("Tags récupérés sur SoundCloud:", tags)
            determined_genre = get_genre_from_tags(tags, styles)
            print("Genre déterminé :", determined_genre)
        else:
            print("Gestion des tags et genre désactivée")
    except Exception as ex:
        print("Erreur dans fetch_artwork_and_tags:", ex)
    driver.quit()
    return artwork_url, tags, determined_genre

def download_artwork_file(track_url, mp3_name, out_folder):
    art_url, sc_tags, det_genre = fetch_artwork_and_tags(track_url)
    if art_url:
        try:
            r = requests.get(art_url, stream=True)
            if r.status_code == 200:
                new_img_name = os.path.splitext(mp3_name)[0] + ".jpg"
                new_img_path = os.path.join(out_folder, new_img_name)
                with open(new_img_path, "wb") as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                print("Artwork téléchargé et renommé vers:", new_img_path)
                return new_img_path, sc_tags, det_genre
            else:
                print("Erreur téléchargement artwork, code", r.status_code)
                return None, sc_tags, det_genre
        except Exception as e:
            print("Erreur téléchargement artwork:", e)
            return None, sc_tags, det_genre
    else:
        print("Artwork introuvable pour", track_url)
        return None, [], det_genre

def add_cover_art(mp3_path, art_path):
    audio = MP3(mp3_path, ID3=ID3)
    if audio.tags is None:
        audio.add_tags()
    for key in list(audio.tags.keys()):
        if key.startswith('APIC'):
            del audio.tags[key]
    with open(art_path, 'rb') as img:
        audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=img.read()))
    audio.save(v2_version=3)

def add_comment_tags(mp3_path, tags_list):
    audio = MP3(mp3_path, ID3=ID3)
    if audio.tags is None:
        audio.add_tags()
    for key in list(audio.tags.keys()):
        if key.startswith("COMM"):
            del audio.tags[key]
    comment = ", ".join(tags_list)
    audio.tags.add(COMM(encoding=3, desc="Comment", text=comment))
    audio.save(v2_version=3)

def add_genre_if_missing(mp3_path, genre):
    audio = MP3(mp3_path, ID3=ID3)
    if "TCON" not in audio.tags or not audio.tags.get("TCON").text:
        audio.tags.add(TCON(encoding=3, text=genre))
        audio.save(v2_version=3)

def update_downloaded_file(file_path, track_url):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(track_url + "\n")

def get_downloaded_urls(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def normalize_url(url):
    return url.split('?')[0]

def process_track_item(track_url, out_folder):
    opts = create_chrome_opts()
    service = Service(log_path=os.devnull)
    driver = webdriver.Chrome(service=service, options=opts)
    driver.get("https://soundcloudtomp3.biz/index.php")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='quality'][value='320']"))).click()
    inp = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.form-control.form-control-lg[name='videoURL']")))
    inp.clear()
    inp.send_keys(track_url)
    inp.send_keys(Keys.ENTER)
    time.sleep(1)
    handles = driver.window_handles
    if len(handles) > 1:
        main_handle = driver.current_window_handle
        for h in handles:
            if h != main_handle:
                driver.switch_to.window(h)
                driver.close()
        driver.switch_to.window(main_handle)
    btn = WebDriverWait(driver, 300).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'btn btn-success') and contains(., 'Download your MP3 file')]")))
    btn.click()
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    dl_file = wait_for_mp3_download(downloads_folder, timeout=300)
    if dl_file:
        mp3_new_name = os.path.basename(dl_file).replace("_", " ")
        new_mp3_path = os.path.join(out_folder, mp3_new_name)
        time.sleep(1)
        shutil.move(dl_file, new_mp3_path)
        print("MP3 téléchargé et déplacé vers:", new_mp3_path)
        if ARTWORK:
            art_path, sc_tags, det_genre = download_artwork_file(track_url, mp3_new_name, out_folder)
            if art_path and os.path.exists(art_path):
                add_cover_art(new_mp3_path, art_path)
                print("Artwork intégré dans:", new_mp3_path)
                os.remove(art_path)
            else:
                print("Artwork non intégré pour:", track_url)
        if CLASSIFY:
            if sc_tags:
                add_comment_tags(new_mp3_path, sc_tags)
                print("Tags SoundCloud écrits dans le champ Commentaire")
            if det_genre:
                add_genre_if_missing(new_mp3_path, det_genre)
                print("Genre ajouté dans le champ Genre si absent")
    else:
        print("Timeout ou échec pour:", track_url)
    time.sleep(1)
    driver.quit()

if __name__ == "__main__":
    input_url = input("Entrez l'URL SoundCloud (playlist, artiste ou son unique): ")
    print("Sélectionnez le dossier d'output dans a fenêtre qui vient d'apparaitre")
    output_folder = askdirectory(title="Sélectionnez le dossier où télécharger les musiques")
    parsed = urlparse(input_url)
    path_comps = [comp for comp in parsed.path.split('/') if comp]
    
    downloaded_file = os.path.join(output_folder, "downloaded_urls.txt")
    
    if len(path_comps) > 1 and path_comps[1].lower() == "sets":
        urls = fetch_playlist_urls(input_url)
    elif len(path_comps) > 0 and path_comps[-1].lower() in ("tracks", "popular-tracks"):
        urls = fetch_artist_tracks(input_url)
    else:
        urls = [input_url]
    
    print(len(urls), "musique(s) à télécharger")
    downloaded_urls = get_downloaded_urls(downloaded_file)
    
    for url in urls:
        normalized = normalize_url(url)
        if any(normalize_url(url) == normalize_url(d) for d in downloaded_urls):
            print("Déjà téléchargé:", url)
            continue
        process_track_item(url, output_folder)
        update_downloaded_file(downloaded_file, url)