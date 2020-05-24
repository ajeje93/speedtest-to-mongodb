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

## Visualize data

### Grafana

You can find a Grafana dashboard to visualize data at <https://grafana.com/grafana/dashboards/12350>.
