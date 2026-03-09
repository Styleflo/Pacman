# PacManIA

## Présentation

Le projet utilise une version préexistante d'un jeu PacMan pour y implémenter une IA

## Installation

### Étape 1 : cloner le projet
```bash
    git clone https://github.com/Styleflo/Pacman.git
```

### Étape 2 : créez un environnement virtuel et activez-le
```bash
  python -m venv venv
  source venv/bin/activate
```

### Étape 3 : Installez les dépendances
```bash
  pip install -r requirements.txt
```

### Étape 4 : Exécution

Lancer le jeu avec :
```bash
  python run.py
```

## Structure du projet

- `run.py` : point d'entrée du jeu.
- `requirements.txt` : dépendances Python.
- `pacman/` : code principal du jeu (game loop, scènes, gestion des sons, skins, stockage, etc.).
- `assets/` : images, fonts, sons et maps.
- `pacmania/` : scripts et configuration pour l'IA.
- `storage.json` : fichier JSON utilisé pour persister scores, paramètres et skins.
