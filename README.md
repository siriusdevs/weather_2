# creating docker container with postgres
docker run -d --name weather -p 5555:5432 -e POSTGRES_DBNAME=test \
    -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test postgres

# connecting to postgres with psql
psql -h 127.0.0.1 -p 5555 -U test test # password test

# creating table
CREATE TABLE city (name TEXT NOT NULL, latitude FLOAT NOT NULL, longtitude FLOAT NOT NULL);

# inserting values
INSERT INTO city (name, latitude, longtitude) VALUES ('city', 1.0, 1.0);

# unique city constraint
ALTER TABLE city ADD CONSTRAINT unique_city UNIQUE(name, latitude, longtitude);
