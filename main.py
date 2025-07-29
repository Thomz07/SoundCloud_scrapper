import os
import time
import shutil
from urllib.parse import urlparse
from tkinter.filedialog import askdirectory

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import ARTWORK, CLASSIFY
from selenium_utils import create_driver, wait_for_mp3_download
from soundcloud_scraper import fetch_playlist_urls, fetch_artist_tracks, download_cover
from audio_processor import add_cover, add_url_comment, add_genre, add_artist, get_already_downloaded_tracks


def process_track_item(track_url, out_folder):
    track_url = track_url.split("?")[0]
    print(f"▶ Téléchargement : {track_url}")

    driver = create_driver()
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

    if artist:
        add_artist(dst, artist)
        print("    • artiste ajouté au MP3")

    driver.quit()
    print("✔️ Terminé\n")


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