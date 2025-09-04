# 🕸 🕷 Scrapping 🕷 🕸

## Installation

```sh
uv pip install ".[scrap]"
```

## Exécution

```sh
cd src/scrapping
scrapy crawl transit -O ../data/transit.json
```

## Lancement d'une console pour tester les scrapping

```sh
scrapy shell https://transitapp.com/fr/region/grenoble/ara-cars-r%C3%A9gion-is%C3%A8re-scolaire
```
