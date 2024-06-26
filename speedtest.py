import subprocess
import os
import errno
import json
import datetime
from pymongo import mongo_client
import time
import logging
from dotenv import load_dotenv
from timeout import timeout

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


@timeout(120, os.strerror(errno.ETIMEDOUT))
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


def create_collections(mongo_uri, database, collection):
    try:
        # insert object in db
        client = mongo_client.MongoClient(mongo_uri)
        db = client[database]

        filter = {"name": {"$regex": rf"^(?!system\.)\b(\w*{collection}\w*)\b"}}
        collection_list = db.list_collection_names(filter=filter)
        get_module_logger(__name__).debug(
            "Collection list filtered: {0}".format(collection_list)
        )

        if collection not in collection_list:
            db.command("create", collection)
            get_module_logger(__name__).info(
                "Created collection {0}".format(collection)
            )
        else:
            get_module_logger(__name__).debug(
                "Collection {0} already exists".format(collection)
            )

        if "normalized_" + collection not in collection_list:
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
                "normalized_" + collection,
                viewOn=collection,
                pipeline=pipeline,
            )
            get_module_logger(__name__).info(
                "Created view {0}".format("normalized_" + collection)
            )
        else:
            get_module_logger(__name__).debug(
                "View {0} already exists".format("normalized_" + collection)
            )

        client.close()
    except Exception as e:
        get_module_logger(__name__).error(
            "Error in create_collection function: {0}".format(e)
        )


def main():
    try:
        load_dotenv()
        # get config main config
        delay_seconds = int(os.getenv("DELAY_SECONDS", 60))
        get_module_logger(__name__).debug(
            "Delay between speetests is {0}".format(delay_seconds)
        )

        logging_level_string = os.getenv("LOGGING_LEVEL", "DEBUG")
        get_module_logger(__name__).debug(
            "Logging level is {0}".format(logging_level_string)
        )

        # specific mongo config
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        get_module_logger(__name__).debug("MongoDB URI is {0}".format(mongo_uri))

        database = os.getenv("MONGODB_DB", "network_monitoring")
        get_module_logger(__name__).debug("MongoDB DB is {0}".format(database))

        collection = os.getenv("MONGODB_COLLECTION", "speedtest")
        get_module_logger(__name__).debug(
            "MongoDB collection is {0}".format(collection)
        )

        # speedtest config
        speedtest_server_id = os.getenv("SPEEDTEST_SERVER_ID", "")
        get_module_logger(__name__).debug(
            "Speedtest server id is {0}".format(speedtest_server_id)
        )

        # set logging level
        set_global_logging_level(logging_level_string)

        starttime = time.time()
        while True:
            time.sleep(delay_seconds - ((time.time() - starttime) % delay_seconds))
            get_module_logger(__name__).debug(
                "Waiting for {0} seconds".format(delay_seconds)
            )
            create_collections(mongo_uri, database, collection)
            speedtest(mongo_uri, database, collection, speedtest_server_id)
    except Exception as e:
        get_module_logger(__name__).error("Error in main function: {0}".format(e))


if __name__ == "__main__":
    main()
