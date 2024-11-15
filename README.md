# Speedtest to MongoDB

This utility send the speedtest of the network on which it is performed on a MongoDB database.

[![Docker Hub](https://img.shields.io/docker/v/ajeje93/speedtest-to-mongodb?label=Docker%20Hub&sort=date)](https://hub.docker.com/r/ajeje93/speedtest-to-mongodb)

[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fajeje93%2Fspeedtest-to-mongodb%2Fbadge%3Fref%3Dmaster&style=flat)](https://actions-badge.atrox.dev/ajeje93/speedtest-to-mongodb/goto?ref=master)

## Configuration

All configurations are contained in the `.env` file.

The possible keys in the file are:

* `MONGODB_URI`, the URI to the MongoDB database
* `MONGODB_DB`, the MongoDB database name
* `SPEEDTEST_COLLECTION`, the MongoDB collection name for speedtest data
* `SPEEDTEST_DELAY_SECONDS`, the delay between each speedtest in seconds
* `SPEEDTEST_SERVER_ID`, the <https://www.speedtest.net> server ID (e.g.: 4302 for Vodafone IT). If missing the speedtest-cli will autoselect a server
* `PING_COLLECTION`, the MongoDB collection name for ping data
* `PING_DELAY_SECONDS`, the delay between each ping in seconds
* `PING_HOST`, the host to ping
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
