# 🎵 SoundCloud Scrapper

Ce projet permet de télécharger des musiques depuis SoundCloud facilement

## Fonctionnalités

- Téléchargement en 320kb/s 
- Ajoute de l'artwork 
- Ajout du genre pour les sons qui le permettent
- Gestion des doublons lors des téléchargements
- Téléchargement de sons uniques
- Téléchargement de playlists 
- Téléchargement à partir d'une page artiste

## Pré-requis
 
- **Python 3** (tutoriel d'installation ci-dessous)  

## Installation du script
1. Télécharger le [script](https://github.com/Thomz07/SoundCloud_scrapper/archive/refs/heads/main.zip) et le placer là où vous souhaitez
2. Télécharger Python ([macOS](https://www.python.org/ftp/python/3.13.2/python-3.13.2-macos11.pkg)) ([Windows](https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe))
3. Suivre les instructions de l'installeur python (Attention : pour Windows, bien cocher "Add python to path")

## Installation des dépendances

### Windows
Pour installer les dépendances sur Windows, il faut simplement lancer le fichier `install.bat`

Si ça ne fonctionne pas, essayer d'exécuter le fichier en tant qu'administrateur 

### macOS

Pour installer les dépendances sur MacOS, il faut d'abord lancer un terminal. Cela peut être fait avec `Cmd + Espace` et chercher `Terminal` ou simplement chercher l'application depuis le launchpad dans le dossier `Autre` ou `Utilitaires`

Une fois le terminal lancé, tapez la commande suivante : 

```
cd chemin/vers/le/dossier/du/script
```

Au lieu de taper le chemin, vous pouvez glisser le dossier dans le terminal après avoir tapé `cd `(bien penser à mettre un espace après `cd`

Votre terminal devrait ressembler à ceci :
![SoundCloud Scrapper Terminal View](https://i.imgur.com/coxxkjU.png)

Une fois ici, exécuter les commandes suivantes : 
```
chmod +x install.command
chmod +x run.command
```
Cela va donner les permissions d'exécutions aux scripts

Vous pouvez fermer le terminal après ça et lancer le fichier `install.command`, cependant vous devriez rencontrer la fenêtre suivante : 

![SoundCloud Scrapper Error View](https://i.imgur.com/CWFt841.png)

Pour régler cela, ouvrez les réglages système dans la section `Confidentialité et sécurité` et cliquez sur `Ouvrir quand même` quand vous y êtes invités

Une fois le script terminé vous pouvez fermer le terminal et les dépendances devraient être correctements installées

## Lancement du script

Pour utiliser le script, il suffit simplement de lancer le fichier `run.command` pour macOS ou `run.bat` pour Windows

Pour macOS, la manipulation `Ouvrir quand même` faite précédement devra être refaite pour le deuxième fichier

## Utilisation

Il suffit simplement de suivre les instructions du script en rentrant l'URL souhaitée et séléctionner le dossier de téléchargement

Les URLs de playlists privées doivent être récupérées depuis le bouton `Copier le lien` sur la page de la playlist pour fonctionner avec le script

L'URL peut être d'une de playlist, d'une musique unique ou d'une page d'artiste dans la section `Titre`
```
https://soundcloud.com/user-297041232/sets/eurodance/s-DSDLlAO9JS0?si=92e786884a314ddd89bd0dd4264845a3&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing
https://soundcloud.com/funktribumusic/i-got-it-for-you-extended
https://soundcloud.com/{Artiste}/tracks
```

Une musique téléchargée grâce à ce script **ne sera pas re-téléchargée** si elle est déjà présente dans le dossier de sortie séléctionné

Vous pouvez re-télécharger la même playlist dans le même dossier et les musiques déjà téléchargées ne seront pas re-téléchargées inutilement

## Notes

La première exécution prendra plus de temps car le webdriver de chrome (chrome automatisé) doit s'installer

Le script s'arrêtera si l'ordinateur se mets en veille

Sur macOS, vous devrez autoriser l'accès aux différents dossiers (Téléchargements, Documents) lorsqu'on vous le demande

Ce script doit être utilisé pour télécharger des musiques que vous avez préalablement acheté de manière légale