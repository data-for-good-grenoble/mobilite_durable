# Extraire les données du .dump

On suppose que les commandes sont lancées à la racine du projet.

Adapter `C2C_DUMP_NAME` au nom du fichier que C2C vous avez envoyé.

On extrait ici le schéma complet de la BDD mais que la table `guidebook.stopareas`.

```bash
export C2C_DATA_PATH="$PWD/src/data/C2C"
export C2C_DUMP_NAME="c2corg-anonymized.2025-12-10.dump"
export C2C_SCHEMA_DUMP_NAME="$(basename $C2C_DUMP_NAME .dump).schema.sql"
export C2C_STOPAREAS_DUMP_NAME="$(basename $C2C_DUMP_NAME .dump).sql"

# Start a postgis container
docker run --rm --name c2cdb -e POSTGRES_PASSWORD=password -v $C2C_DATA_PATH:/data -p 5432:5432 -d docker.io/postgis/postgis:17-3.6-alpine

# Extract the full schema
docker exec c2cdb pg_restore --schema-only -f /data/$C2C_SCHEMA_DUMP_NAME /data/$C2C_DUMP_NAME

# Restore the stopareas table in the container
docker exec -u postgres c2cdb psql -d postgres -c "CREATE ROLE \"www-data\";"
docker exec -u postgres c2cdb psql -d postgres -c "CREATE SCHEMA IF NOT EXISTS guidebook AUTHORIZATION postgres;"
docker exec -u postgres c2cdb pg_restore -d postgres --table=stopareas /data/$C2C_DUMP_NAME

# Extract stopareas table in a .sql file
docker exec -u postgres c2cdb pg_dump --inserts -t guidebook.stopareas postgres > $C2C_DATA_PATH/$C2C_STOPAREAS_DUMP_NAME

# Stop (and remove) postgres container
docker stop c2cdb

# Clean volume
docker volume prune
```
