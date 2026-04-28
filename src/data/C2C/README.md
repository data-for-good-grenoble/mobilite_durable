# Extraire les données du .dump

On suppose que les commandes sont lancées à la racine du projet.

Adapter `C2C_DUMP_NAME` au nom du fichier que C2C vous avez envoyé.

On extrait ici le schéma complet de la BDD mais que la table `guidebook.stopareas`.

```bash
export C2C_DATA_PATH="$PWD/src/data/C2C"
export C2C_DUMP_NAME="c2corg-anonymized.2025-12-10.dump"
export C2C_SCHEMA_DUMP_NAME="$(basename $C2C_DUMP_NAME .dump).schema.sql"
export C2C_STOPAREAS_DUMP_NAME="$(basename $C2C_DUMP_NAME .dump).sql"
export C2C_ACCESS_POINTS_EXPORT_NAME="$(basename $C2C_DUMP_NAME .dump).access_points.csv"

# Start a postgis container and wait 10s to let the database be ready
docker run --rm --name c2cdb -e POSTGRES_PASSWORD=password -v $C2C_DATA_PATH:/data -p 5432:5432 -d docker.io/postgis/postgis:9.6-2.5
sleep 10

# Check postgres and postgis versions
docker exec -u postgres c2cdb pg_restore -l /data/$C2C_DUMP_NAME | head -30
docker exec -u postgres c2cdb pg_restore -f - /data/$C2C_DUMP_NAME | grep -i "postgis"

# Extract the full schema
docker exec c2cdb pg_restore --schema-only -f /data/$C2C_SCHEMA_DUMP_NAME /data/$C2C_DUMP_NAME

# Restore the full schema (includes custom types)
docker exec -u postgres c2cdb psql -d postgres -c "CREATE ROLE \"www-data\";"
docker exec -u postgres c2cdb pg_restore --schema-only -d postgres /data/$C2C_DUMP_NAME

# Fill langs table because documents_locales needs it
docker exec -u postgres c2cdb pg_restore --data-only -d postgres --table=langs /data/$C2C_DUMP_NAME

# Create st_simplify function for documents_geometries table
docker exec -u postgres c2cdb psql -d postgres -c "
CREATE OR REPLACE FUNCTION guidebook.st_simplify(geom public.geometry, tol integer)
RETURNS public.geometry AS
\$BODY\$
  SELECT public.st_simplify(geom, tol::double precision);
\$BODY\$
LANGUAGE sql
IMMUTABLE
SECURITY DEFINER;
"

# Restore tables
docker exec -u postgres c2cdb pg_restore --data-only -d postgres --table=stopareas --table=documents --table=documents_locales --table=documents_geometries --table=waypoints /data/$C2C_DUMP_NAME

# Extract stopareas table in a .sql file
docker exec -u postgres c2cdb pg_dump --inserts -t guidebook.stopareas postgres > $C2C_DATA_PATH/$C2C_STOPAREAS_DUMP_NAME

# Extract waypoints table in a .csv file
docker exec -u postgres c2cdb psql -d postgres -c "\copy (
  SELECT
    dg.document_id,
    ST_X(
      CASE WHEN GeometryType(dg.geom) = 'POINT'
           THEN ST_Transform(dg.geom, 4326)
           ELSE ST_Transform(ST_Centroid(dg.geom), 4326)
      END
    ) AS lon,
    ST_Y(
      CASE WHEN GeometryType(dg.geom) = 'POINT'
           THEN ST_Transform(dg.geom, 4326)
           ELSE ST_Transform(ST_Centroid(dg.geom), 4326)
      END
    ) AS lat,
    title,
    description,
    summary
  FROM guidebook.documents_geometries dg
  JOIN guidebook.waypoints w
    ON w.document_id = dg.document_id
    AND w.waypoint_type = 'access'
  LEFT JOIN guidebook.documents_locales dl
    ON w.document_id = dl.document_id
    AND dl.lang = 'fr'
) TO STDOUT WITH CSV HEADER" > $C2C_DATA_PATH/$C2C_ACCESS_POINTS_EXPORT_NAME

# Stop (and remove) postgres container
docker stop c2cdb

# Clean volume
docker volume prune
```

# Générer une documentation du schéma

Les commandes suivantes permettent de générer la documentation des schémas de BDD  qui sont dans le zip `c2corg-anonymized.2025-12-10.schema_doc.zip`.

```bash
# Set the env variables (see above)

# Install a postgres driver
mkdir $C2C_DATA_PATH/drivers
wget https://jdbc.postgresql.org/download/postgresql-42.7.8.jar -O $C2C_DATA_PATH/drivers/postgresql.jar

# Create directory where documentation will be stored
mkdir $C2C_DATA_PATH/schema_doc
chmod +777 $C2C_DATA_PATH/schema_doc

# Deploy Postgres schema in a container
docker network create schemaspy-net
docker run --rm --name postgres_schema -e POSTGRES_PASSWORD=password --network schemaspy-net -d docker.io/postgis/postgis:17-3.6-alpine
docker exec -i postgres_schema psql -U postgres < $C2C_DATA_PATH/$C2C_SCHEMA_DUMP_NAME

# Run schemaspy
docker run --rm \
 -v $C2C_DATA_PATH/schema_doc:/output \
 -v $C2C_DATA_PATH/drivers:/drivers \
 --network schemaspy-net \
 docker.io/schemaspy/schemaspy:latest \
 -t pgsql \
 -dp /drivers/postgresql.jar \
 -host postgres_schema \
 -port 5432 \
 -db postgres \
 -u postgres \
 -p password \
 -all

 # Stop (and remove) postgres container
docker stop postgres_schema

# Clean volume
docker volume prune
```