import re
import time
import requests
import os
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_utils import create_driver, scroll_to_bottom
from config import CLASSIFY, STYLES


def get_genre_from_tags(track_tags, style_list):
    for style in reversed(style_list):
        if style.replace(" ", "").lower() in [t.replace(" ", "").lower() for t in track_tags]:
            return style
    return None


def fetch_playlist_urls(playlist_url):
    print("🔎 Analyse de la playlist…")
    driver = create_driver()
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
    driver = create_driver()
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
    print(f"  → {len(urls)} titre(s) public(s) trouvé(s) chez l'artiste")
    return urls


def fetch_artwork_and_tags(track_url):
    driver = create_driver()
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
                determined_genre = get_genre_from_tags(tags, STYLES)
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
