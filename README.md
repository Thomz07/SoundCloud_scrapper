# 🎵 SoundCloud Scrapper

Ce projet permet de télécharger des musiques depuis SoundCloud facilement

### Fonctionnalités

- Téléchargement en 320kb/s 
- Ajoute de l'artwork 
- Ajout du genre pour les sons qui le permettent
- Gestion des doublons lors des téléchargements
- Téléchargement de sons uniques
- Téléchargement de playlists 
- Téléchargement à partir d'une page artiste

### Pré-requis
 
- **Python 3** (tutoriel d'installation ci-dessous)  

### Installation du script
1. Télécharger le [script](https://github.com/Thomz07/SoundCloud_scrapper/archive/refs/heads/main.zip) et le placer là où vous souhaitez
2. Télécharger Python ([MacOS](https://www.python.org/ftp/python/3.13.2/python-3.13.2-macos11.pkg)) ([Windows](https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe))
3. Suivre les instructions de l'installeur python (Attention : pour Windows, bien cocher "Add python to path")

### Installation des dépendances

#### Windows
Pour installer les dépendances sur Windows, il faut simplement lancer le fichier `install.bat`

Si ça ne fonctionne pas, essayer d'exécuter le fichier en tant qu'administrateur 

#### MacOS

Pour installer les dépendances sur MacOS, il faut d'abord lancer un terminal. Cela peut être fait avec `Cmd + Espace` et chercher `Terminal` ou simplement chercher l'application depuis le launchpad dans le dossier `Autre` ou `Utilitaires`

Une fois le terminal lancé, tapez la commande suivante : 

`cd chemin/vers/le/dossier/du/script`

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