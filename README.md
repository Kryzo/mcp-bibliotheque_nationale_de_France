# BnF API Server

Un serveur MCP (Model-Client-Protocol) pour accéder à l'API Gallica de la Bibliothèque nationale de France (BnF) et générer des rapports de recherche séquentiels.

## Fonctionnalités

- **Recherche dans Gallica** : Recherche de documents, images, cartes et autres ressources dans la bibliothèque numérique Gallica
- **Génération de rapports séquentiels** : Création automatique de rapports de recherche structurés sur n'importe quel sujet
- **Intégration de graphiques** : Inclusion d'images et de cartes pertinentes dans les rapports générés
- **Citations formatées** : Génération automatique de bibliographies avec citations correctement formatées

## Installation

### Prérequis

- Python 3.8 ou supérieur
- Pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le dépôt**:
   ```bash
   git clone https://github.com/votre-nom/mcp-bnf.git
   cd mcp-bnf
   ```

2. **Installer les dépendances**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration avec Claude Desktop

1. **Installer Claude Desktop** si ce n'est pas déjà fait.

2. **Ouvrir la configuration de Claude Desktop**:
   - Accéder aux paramètres de Claude Desktop
   - Ouvrir le fichier de configuration (généralement situé à `%APPDATA%\Claude\claude_desktop_config.json`)

```json
{
 "bnf": {
  "command": "py",
  "args": [
    "c:\\chemin\\vers\\mcp-bnf\\bnf_server.py"
  ],
  "cwd": "c:\\chemin\\vers\\mcp-bnf"
},
```

Remplacez `chemin\\vers\\mcp-bnf` par le chemin réel vers votre répertoire d'installation.

3. **Enregistrer le fichier de configuration** et redémarrer Claude Desktop

## Outils MCP disponibles

Une fois configuré, les outils suivants seront disponibles dans Claude Desktop:

### Recherche dans Gallica

Permet de rechercher des documents dans la bibliothèque numérique Gallica de la BnF en utilisant différents critères (titre, auteur, sujet, date, type de document).

### Génération de rapports séquentiels

Crée des rapports de recherche complets sur n'importe quel sujet en utilisant les sources de Gallica. Les rapports incluent:
- Une bibliographie formatée
- Une introduction
- Un contexte historique
- Une analyse
- Une conclusion
- Des images et cartes pertinentes (optionnel)

## Structure du projet

```
mcp-bnf/
│
├── bnf_server.py              # Serveur MCP principal
├── requirements.txt           # Dépendances du projet
│
└── bnf_api/                   # Package API BnF
    ├── __init__.py            # Exports du package
    ├── api.py                 # Client API Gallica BnF
    ├── search.py              # Fonctions de recherche
    ├── config.py              # Constantes et configuration
    └── sequential_reporting.py # Outil de génération de rapports séquentiels
```

## Utilisation

Une fois configuré avec Claude Desktop, vous pouvez demander à Claude d'utiliser les outils BnF pour:

1. **Rechercher des documents**:
   - "Recherche des livres sur Victor Hugo dans Gallica"
   - "Trouve des cartes de Paris du 19ème siècle"

2. **Générer des rapports**:
   - "Crée un rapport sur l'impressionnisme en France"
   - "Génère un rapport sur l'histoire du Liban sous mandat français avec des images"

## Développement

Pour contribuer au projet:

1. Forker le dépôt
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committer vos changements (`git commit -am 'Ajouter une nouvelle fonctionnalité'`)
4. Pousser vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.
