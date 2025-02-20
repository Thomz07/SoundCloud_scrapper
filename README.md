# 🎵 SoundCloud Downloader & Tagger

Ce projet permet de télécharger des morceaux ou playlists depuis SoundCloud, de récupérer leur artwork et leurs tags, et d'ajouter automatiquement ces métadonnées aux fichiers MP3, tout ça en 320kb/s !

---

## Fonctionnalités

- Téléchargement de morceaux ou playlists SoundCloud  
- Récupération automatique de l'image de l'artwork  
- Récupération des tags SoundCloud directement sur le fichier
- Détermination du genre des musiques 

---

## Installation et utilisation

### Pré-requis

- **Google Chrome** : Ce script utilise Selenium avec Chrome, donc **Google Chrome** doit être installé sur la machine.  
- **Python 3** : Le script est écrit en Python, il vous faudra l'installer si vous ne l'avez pas déjà (tutoriel en dessous).  
- **Chromedriver** : Selenium a besoin de `chromedriver` pour fonctionner. Vous pouvez le télécharger ici :  [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)  
  Une fois téléchargé, placez `chromedriver.exe` (Windows) ou `chromedriver` (Mac/Linux) dans le dossier du script.

---

### Récupération du script

#### Méthode 1 : Télécharger l’archive ZIP
1. Aller sur le dépôt GitHub du projet.  
2. Cliquer sur le bouton bleu avec écrit **"Code"**  
3. Cliquer sur **"Download ZIP"**  
4. Dézipper l'archive téléchargée  
5. Placer le dossier où vous le souhaitez

#### Méthode 2 : Cloner avec Git (optionnel, pour les utilisateurs avancés)
Si vous utilisez Git, vous pouvez cloner le dépôt directement avec la commande :
```sh
git clone https://github.com/TON_REPO/SoundCloud-Downloader.git
```

---

### Installation de Python

Si vous n'avez pas encore Python installé sur votre ordinateur, suivez ces étapes :

#### Windows

1. Téléchargez l'installateur depuis le site officiel :  [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Lancez l’installateur (`python-3.x.x.exe`).
3. **IMPORTANT** : Sur l'écran d'installation, **cochez la case "Add Python to PATH"** en bas.
4. Cliquez sur **Install Now** et laissez l'installation se terminer.
5. Vérifiez l'installation en ouvrant l'Invite de Commande (`cmd`) et en tapant :  
   ```sh
   python --version
   ```
   Vous devriez voir la version de Python s'afficher.

#### macOS

1. Ouvrez le Terminal (`Cmd + Espace`, tapez `Terminal` et appuyez sur `Entrée`).
2. Installez Python avec **Homebrew** (si Homebrew n'est pas installé, suivez les instructions sur [https://brew.sh/](https://brew.sh/)) :
   ```sh
   brew install python
   ```
3. Vérifiez l'installation en tapant :
   ```sh
   python3 --version
   ```

#### Linux (Ubuntu/Debian)

1. Ouvrez un terminal (`Ctrl + Alt + T`).
2. Tapez la commande suivante pour installer Python :
   ```sh
   sudo apt update && sudo apt install python3 python3-pip -y
   ```
3. Vérifiez l'installation en tapant :
   ```sh
   python3 --version
   ```

---

### Installation des dépendances

Une fois Python installé, vous devez installer les bibliothèques nécessaires au script.  
Ouvrez un terminal ou une invite de commande et exécutez :

```sh
pip install -r requirements.txt
```

Cela installera automatiquement toutes les bibliothèques nécessaires.

---

### Utilisation du script

1. Ouvrez un terminal ou une invite de commande.  
2. Exécutez la commande suivante pour lancer le script :
   ```sh
   python script.py
   ```
3. Entrez l'URL d'un **morceau** ou d'une **playlist** SoundCloud lorsque le script vous le demande.  
4. Indiquez un dossier de sortie où les fichiers MP3 seront stockés.  
5. Le script téléchargera les morceaux, ajoutera les tags et les artworks automatiquement.  

---

## Dépendances

- **Selenium** : Automatisation du navigateur pour récupérer les URLs et informations des morceaux.
- **Mutagen** : Ajout des métadonnées aux fichiers MP3 (artwork, tags, genre).
- **Requests** : Téléchargement des images d'album.
- **ChromeDriver** : Pilote pour Google Chrome via Selenium.

---

## FAQ / Problèmes fréquents

**Problème : Le script ne trouve pas ChromeDriver**  
**Solution** : Téléchargez `chromedriver.exe` depuis [ici](https://chromedriver.chromium.org/downloads), et placez-le dans le même dossier que le script.  

**Problème : "chromedriver" n’est pas reconnu sur macOS/Linux**  
**Solution** : Ajoutez ChromeDriver au PATH en exécutant la commande suivante :  
```sh
sudo mv chromedriver /usr/local/bin/
```

**Problème : "ModuleNotFoundError: No module named 'selenium'"**  
**Solution** : Vous avez oublié d’installer les dépendances. Exécutez :  
```sh
pip install -r requirements.txt
```

---

## Remarque

- Ce projet ne contourne pas les protections de SoundCloud et ne doit être utilisé que pour des morceaux autorisés au téléchargement.  
- Assurez-vous d'avoir **Google Chrome** installé avant d'exécuter le script.
