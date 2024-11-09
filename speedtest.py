import subprocess
import os
import json
import datetime
from pymongo import mongo_client
import time
import logging
from dotenv import load_dotenv
from ping3 import ping
import schedule
import threading

logging_level = logging.DEBUG


def get_module_logger(mod_name):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    global logging_level
    logger = logging.getLogger(mod_name)
    # reset the logger.handlers if it already exists.
    if logger.handlers:
        logger.handlers = []
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging_level)
    return logger


def set_global_logging_level(logging_level_string):
    global logging_level
    switcher = {
        "DEBUG": logging.DEBUG,
        "ERROR": logging.ERROR,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "CRITICAL": logging.CRITICAL,
    }
    logging_level = switcher.get(logging_level_string, logging.DEBUG)


def check_internet_latency(host="8.8.8.8"):
    """
    Pings the specified host to check connectivity and measure latency.
    Returns a tuple (is_connected, latency).
    - is_connected: True if the ping is successful, False otherwise.
    - latency: The round-trip time in milliseconds if connected, None otherwise.
    """
    try:
        latency = ping(host, timeout=3, unit="ms")
        if latency is not None:
            return True, latency
        else:
            return False, None
    except Exception:
        return False, None


def speedtest(mongo_uri, database, collection, speedtest_server_id):
    try:
        get_module_logger(__name__).info("Performing speedtest...")

        # get speedtest
        command = ["speedtest", "--format=json", "--accept-license", "--accept-gdpr"]
        if speedtest_server_id != "":
            command.append("--server-id={0}".format(speedtest_server_id))

        get_module_logger(__name__).info(
            "Running command: {0}".format(" ".join(command))
        )

        result = json.loads(
            subprocess.run(command, stdout=subprocess.PIPE).stdout.decode("utf-8")
        )
        get_module_logger(__name__).debug("speedtest result: {0}".format(result))

        # convert timestamp
        result["timestamp"] = datetime.datetime.strptime(
            result["timestamp"], "%Y-%m-%dT%H:%M:%S%z"
        )

        # insert object in db
        client = mongo_client.MongoClient(mongo_uri)
        db = client[database]
        collection = db[collection]
        object_id = collection.insert_one(result).inserted_id
        get_module_logger(__name__).debug("object id: {0}".format(object_id))
        get_module_logger(__name__).debug(
            "inserted obj: {0}".format(collection.find_one({"_id": object_id}))
        )
        client.close()

        get_module_logger(__name__).info("Speedtest completed!")
    except Exception as e:
        get_module_logger(__name__).error("Error in speedtest function: {0}".format(e))


def log_connection_status(mongo_uri, database, collection, ping_host):
    """
    Checks internet connection status and latency, logs them to MongoDB.
    """
    is_connected, latency = check_internet_latency(ping_host)
    status = "Connected" if is_connected else "Disconnected"
    timestamp = datetime.datetime.now()

    entry = {
        "status": status,
        "timestamp": timestamp,
        "latency_ms": latency if is_connected else None,
        "host": ping_host,
    }

    client = mongo_client.MongoClient(mongo_uri)
    db = client[database]
    collection = db[collection]
    collection.insert_one(entry)
    client.close()

    get_module_logger(__name__).info(
        f"Connection status: {status}, Latency: {latency if latency else 'N/A'} ms"
    )


def create_collections(mongo_uri, database, speedtest_collection, ping_collection):
    try:
        # insert object in db
        client = mongo_client.MongoClient(mongo_uri)
        db = client[database]

        collection_list = db.list_collection_names()
        get_module_logger(__name__).debug(
            "Collection list: {0}".format(collection_list)
        )

        collections_to_create = [speedtest_collection, ping_collection]
        for collection in collections_to_create:
            if collection not in collection_list:
                db.command("create", collection)
                get_module_logger(__name__).info(
                    "Created collection {0}".format(collection)
                )
            else:
                get_module_logger(__name__).debug(
                    "Collection {0} already exists".format(collection)
                )

        if "normalized_" + speedtest_collection not in collection_list:
            pipeline = [
                {
                    "$project": {
                        "ts": "$timestamp",
                        "downloadMbps": {"$divide": ["$download.bandwidth", 125000]},
                        "uploadMbps": {"$divide": ["$upload.bandwidth", 125000]},
                        "pingJitter": "$ping.jitter",
                        "pingLatency": "$ping.latency",
                        "packetLoss": 1,
                    }
                }
            ]
            db.command(
                "create",
                "normalized_" + speedtest_collection,
                viewOn=speedtest_collection,
                pipeline=pipeline,
            )
            get_module_logger(__name__).info(
                "Created view {0}".format("normalized_" + speedtest_collection)
            )
        else:
            get_module_logger(__name__).debug(
                "View {0} already exists".format("normalized_" + speedtest_collection)
            )

        if "normalized_" + ping_collection not in collection_list:
            pipeline = [
                {
                    "$project": {
                        "ts": "$timestamp",
                        "pingLatency": "$latency_ms",
                        "status": 1,
                    }
                }
            ]
            db.command(
                "create",
                "normalized_" + ping_collection,
                viewOn=ping_collection,
                pipeline=pipeline,
            )
            get_module_logger(__name__).info(
                "Created view {0}".format("normalized_" + ping_collection)
            )
        else:
            get_module_logger(__name__).debug(
                "View {0} already exists".format("normalized_" + ping_collection)
            )

        client.close()
    except Exception as e:
        get_module_logger(__name__).error(
            "Error in create_collections function: {0}".format(e)
        )


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def main():
    try:
        load_dotenv()

        logging_level_string = os.getenv("LOGGING_LEVEL", "DEBUG")
        get_module_logger(__name__).debug(
            "Logging level is {0}".format(logging_level_string)
        )
        set_global_logging_level(os.getenv("LOGGING_LEVEL", "DEBUG"))

        # MongoDB configuration
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        get_module_logger(__name__).debug("MongoDB URI is {0}".format(mongo_uri))

        database = os.getenv("MONGODB_DB", "network_monitoring")
        get_module_logger(__name__).debug("MongoDB DB is {0}".format(database))

        # Speedtest configuration
        speedtest_collection = os.getenv("SPEEDTEST_COLLECTION", "speedtest")
        get_module_logger(__name__).debug(
            "Speedtest collection is {0}".format(speedtest_collection)
        )
        speedtest_delay = int(os.getenv("SPEEDTEST_DELAY_SECONDS", 300))
        get_module_logger(__name__).debug(
            "Delay between speetests is {0}".format(speedtest_delay)
        )
        speedtest_server_id = os.getenv("SPEEDTEST_SERVER_ID", "")
        get_module_logger(__name__).debug(
            "Speedtest server id is {0}".format(speedtest_server_id)
        )

        # Ping test configuration
        ping_collection = os.getenv("PING_COLLECTION", "ping")
        get_module_logger(__name__).debug(
            "Ping collection is {0}".format(ping_collection)
        )
        ping_delay = int(os.getenv("PING_DELAY_SECONDS", 60))
        get_module_logger(__name__).debug(
            "Delay between pings is {0}".format(ping_delay)
        )
        ping_host = os.getenv("PING_HOST", "8.8.8.8")
        get_module_logger(__name__).debug("Ping host is {0}".format(ping_host))

        create_collections(mongo_uri, database, speedtest_collection, ping_collection)

        schedule.every(speedtest_delay).seconds.do(
            lambda: run_threaded(
                lambda: speedtest(
                    mongo_uri, database, speedtest_collection, speedtest_server_id
                )
            )
        )
        schedule.every(ping_delay).seconds.do(
            lambda: run_threaded(
                lambda: log_connection_status(
                    mongo_uri, database, ping_collection, ping_host
                )
            )
        )

        while True:
            schedule.run_pending()
            time.sleep(0.1)

    except Exception as e:
        get_module_logger(__name__).error("Error in main function: {0}".format(e))


if __name__ == "__main__":
    main()
