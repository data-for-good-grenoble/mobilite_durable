# Projet MDM - Mobilité Durable en Montagne

En collaboration avec :
* DataForGood Grenoble : https://data-for-good-grenoble.github.io/
* CampToCamp : https://www.camptocamp.org/
* ProtectOurWinters : https://protectourwinters.fr/


Spécial remerciement :
* https://transport.data.gouv.fr




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

TESTING
