

import json
import logging.config
import asyncio
import os
from botocore.exceptions import ClientError, EndpointConnectionError
from aiobotocore.session import get_session
from botocore.config import Config
import motor.motor_asyncio

CONSUMER_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] (SQSConsumer) %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "sqs_consumer": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "aiobotocore": {
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False,
        },
        "motor": {
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False,
        }
    },
}
logging.config.dictConfig(CONSUMER_LOGGING_CONFIG)
logger = logging.getLogger("sqs_consumer")

AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
QUEUE_URL = os.getenv("SQS_QUEUE_URL", "REDACTED")
BOTO3_CONFIG = Config(
    max_pool_connections=10
)

MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "iot_telemetry")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "sensor_data")

async def consume_sqs_messages(sqs_client, mongo_collection, queue_url):
    running = True

    while running:
        try:
            response = await sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=10,
            )

            messages = response.get('Messages', [])
            if not messages:
                logger.debug("No messages received from SQS. Waiting...")
                continue

            logger.info(f"Received {len(messages)} message(s) from SQS.")

            for message in messages:
                message_body = message['Body']
                receipt_handle = message['ReceiptHandle']

                try:
                    data = json.loads(message_body)
                    data["_sqsMessageId"] = message.get("MessageId")

                    result = await mongo_collection.insert_one(data)
                    logger.info(f"Inserted message into MongoDB with _id: {result.inserted_id} and SQS MessageId: {message.get('MessageId')}")

                    await sqs_client.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=receipt_handle
                    )
                    logger.info(f"Deleted message from SQS with ReceiptHandle: {receipt_handle}")

                except json.JSONDecodeError as jde:
                    logger.error(f"Error decoding JSON message from SQS: {jde}. Message body: {message_body}")
                    try:
                        await sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
                        logger.warning(f"Deleted malformed JSON message from SQS. ReceiptHandle: {receipt_handle}")
                    except ClientError as e:
                        logger.error(f"Failed to delete malformed message {receipt_handle} from SQS: {e}")
                except Exception as e:
                    logger.error(f"Error processing SQS message or inserting into MongoDB: {e}", exc_info=True)

        except asyncio.CancelledError:
            logger.info("SQS consumer task received cancellation signal. Exiting loop.")
            running = False
        except ClientError as ce:
            if ce.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                logger.error(f"SQS Queue '{queue_url}' does not exist or access denied. Retrying after delay...")
                await asyncio.sleep(60)
            else:
                logger.error(f"SQS ClientError: {ce}", exc_info=True)
                await asyncio.sleep(5)
        except EndpointConnectionError as ece:
            logger.error(f"Network or endpoint connection error to SQS: {ece}. Retrying after delay...")
            await asyncio.usleep(5_000_000)
        except Exception as e:
            logger.error(f"An unexpected error occurred in SQS consumer loop: {e}", exc_info=True)
            await asyncio.sleep(5)

    logger.info("SQS consumer task stopped.")


async def main():
    logger.info("Starting standalone SQS consumer.")

    if not MONGODB_CONNECTION_STRING:
        logger.critical("MONGODB_CONNECTION_STRING environment variable not set. Exiting.")
        return

    sqs_client = None
    mongo_client = None
    try:
        session = get_session()
        sqs_client = await session.create_client('sqs', region_name=AWS_REGION, config=BOTO3_CONFIG).__aenter__()
        logger.info("SQS client initialized for consumer.")

        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
        mongo_db = mongo_client[MONGODB_DATABASE_NAME]
        mongo_collection = mongo_db[MONGODB_COLLECTION_NAME]
        logger.info(f"Connected to MongoDB: {MONGODB_DATABASE_NAME}.{MONGODB_COLLECTION_NAME}")

        await consume_sqs_messages(sqs_client, mongo_collection, QUEUE_URL)

    except Exception as e:
        logger.critical(f"Fatal error during SQS consumer startup or execution: {e}", exc_info=True)
    finally:
        if sqs_client:
            await sqs_client.__aexit__(None, None, None)
            logger.info("SQS client closed by consumer.")
        if mongo_client:
            mongo_client.close()
            logger.info("MongoDB client closed by consumer.")
        logger.info("Standalone SQS consumer finished.")

if __name__ == "__main__":
    asyncio.run(main())
