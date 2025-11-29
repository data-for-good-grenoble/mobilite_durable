# OpenRouteService

On suppose que les commandes sont lancées dans le dossier `src/openrouteservice`.

```sh
cd src/openrouteservice
```

Remarque selon vos versions, il faut remplacer `docker-compose` par `docker compose`.

## Télécharger (ou mettre à jour) les données OSM

```sh
wget https://download.geofabrik.de/europe/france/rhone-alpes-latest.osm.pbf ors-docker/files
```

D'autres fichiers de données peuvent être trouvés sur le site [Geofabrik](https://download.geofabrik.de/).

Dans ce cas pensez à mettre à jour le nom du fichier dans [./ors-docker/config/ors-config.yml](./ors-docker/config/ors-config.yml).

## Démarrer le container

```sh
docker-compose up -d
```

Le premier démarrage, ou le démarrage suite à une mise à jour des données, est long car le service de routing va d'abord calculer le graphe.

On peut voir quand il a fini dans les logs ou en requêtant le endpoint `health` (voir sections suivantes).

**Remarque**: En cas de soucis, vous pouvez augmenter/diminuer le nombre de threads dans le fichier, [./ors-docker/config/ors-config.yml](./ors-docker/config/ors-config.yml) et la RAM dans le fichier [docker-compose.yml](docker-compose.yml).

## Consulter les logs

```sh
docker-compose logs -f
```

**Remarque**: L'argument optionnel `-f` permet d'avoir le flux de logs en direct. Il se quitte avec un `Ctrl+C`.

## Consulter le status du service

```sh
curl 'http://localhost:8080/ors/v2/health'
```

Cela renvoie `{"status":"not ready"}` quand le graphe est en cours de calcul
ou `{"status":"not ready"}` quand c'est fini et que le service est prêt à être requêté.

## Arrêter le container

```sh
docker-compose stop
```

## Ressources

- [Documentation d'installation avec docker](https://giscience.github.io/openrouteservice/run-instance/running-with-docker)

Le fichier `docker-compose.yml` a été récupéré avec la commande suivante

```sh
wget https://github.com/GIScience/openrouteservice/releases/download/v9.5.1/docker-compose.yml
```

La version 9.5.1 a été choisie car c'était la plus récente dans [page des releases](https://github.com/GIScience/openrouteservice/releases).
