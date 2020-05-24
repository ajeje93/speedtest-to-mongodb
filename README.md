# Speedtest to MongoDB

This utility send the speedtest of the network on which it is performed on a MongoDB database.

[![Docker Build](https://img.shields.io/docker/cloud/build/ajeje93/speedtest-to-mongodb)](https://hub.docker.com/r/ajeje93/speedtest-to-mongodb)

## Configuration

All configurations are contained in the `.env` file.

The possible keys in the file are:

* `MONGODB_URI`, the URI to the MongoDB database
* `MONGODB_DB`, the MongoDB database name
* `MONGODB_COLLECTION`, the MongoDB collection name
* `DELAY_SECONDS`, the delay between each speedtest in seconds
* `LOGGING_LEVEL`, the logging level. It can be one of these values: `DEBUG`, `INFO`,`WARNING`,`ERROR`,`CRITICAL`

## Run

### Local

A prerequisite is to install speedtest-cli by Ookla (<https://www.speedtest.net/it/apps/cli>).

Install dependencies with `pip3 install -r requirements.txt`.

To run just type `python3 speedtest.py` in your terminal.

### Docker

Just type `docker-compose up -d` in your terminal.

To have a full stack of the application (speedtest-to-mongodb, [Grafana with MongoDB datasource plugin](https://github.com/ajeje93/grafana-mongodb-docker), MongoDB) use the command `docker-compose -f docker-compose.full-stack.yml up -d`.

If you use the full stack you should add a MongoDB datasource in Grafana using as `URL` <http://localhost:3333>, as `MongoDB URL` the value of the environment variable `MONGODB_URI` (the default is `mongodb://root:password@mongodb:27017`) and as `MongoDB Database` the value of the environment variable `MONGODB_COLLECTION` (the default is `network_monitoring`). Afterwards, you can import the dashboard below to visualize data or create your own.

## Visualize data

### Grafana

You can find a Grafana dashboard to visualize data at <https://grafana.com/grafana/dashboards/12350>.
