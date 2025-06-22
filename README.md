# 🚌 Projet MDM - Mobilité Durable en Montagne ⛰️

En collaboration avec :
* DataForGood Grenoble : https://data-for-good-grenoble.github.io/
* CampToCamp : https://www.camptocamp.org/
* ProtectOurWinters : https://protectourwinters.fr/

Spécial remerciement :
* https://transport.data.gouv.fr

## 📊 Exploration des données

Les notebooks d’analyse de données sont regroupés dans le dossier `src/notebooks`.

⚠️ **Attention à la gestion de version des notebooks Jupyter** : en raison des risques fréquents de **conflits lors des modifications**, il est recommandé de **créer un nouveau notebook** plutôt que de modifier un notebook existant que vous n’avez pas vous-même créé. Une fusion des différentes versions sera effectuée ultérieurement si nécessaire.

### 🗂️ Nomenclature des notebooks

Pour faciliter la collaboration et le suivi des modifications, les notebooks doivent être nommés selon la convention suivante :

```
<date>_<auteur>_<feature>.ipynb
```
- `date` : au format `DD-MM-YYYY` (exemple `19-06-2025`)
- `auteur` : prénom ou identifiant Git (exemple `AReboud`)
- `feature` : description courte (exemple `EPSG`)

```
19-06-2025_AReboud_EPSG.ipynb
```

## Installation

### Dépendances

[Python](https://www.python.org/downloads/) 3.13\
[uv](https://docs.astral.sh/uv/getting-started/installation/), le gestionnaire de paquet

## Générer l'environnement virtuel
```sh
uv sync
uv pip install ".[dev,test]"
```

## Activer l'environnement virtuel
```sh
source .venv/bin/activate
```

## Activation du pre-commit

```sh
pre-commit install
```

## Jouer avec Jupyter Lab

```sh
.venv/bin/jupyter lab
```


## Doc utile

- Format GTFS : https://gtfs.org/documentation/schedule/reference/
- gtfs-kit : https://github.com/mrcagney/gtfs_kit
- …


