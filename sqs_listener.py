import json
import asyncio
import os
from aiobotocore.session import get_session
from botocore.config import Config
import motor.motor_asyncio

AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
QUEUE_URL = os.getenv("SQS_QUEUE_URL", "REDACTED")
BOTO3_CONFIG = Config(max_pool_connections=10)

MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "iot_telemetry")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "sensor_data")

async def consume_sqs_messages(sqs_client, mongo_collection, queue_url):
    while True:
        try:
            response = await sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=10,
            )
            for msg in response.get('Messages', []):
                try:
                    data = json.loads(msg['Body'])
                    data["_sqsMessageId"] = msg.get("MessageId")
                    res = await mongo_collection.insert_one(data)
                    print(f"Inserted message into MongoDB with _id: {res.inserted_id} and SQS MessageId: {msg.get('MessageId')}")
                except:
                    print(f"Failed to insert SQS MessageId: {msg.get('MessageId')} Error: 1") 

                try:
                    await sqs_client.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=msg['ReceiptHandle']
                    )
                except:
                    print(f"Failed to delete SQS MessageId: {msg.get('MessageId')} Error: 2")  

        except asyncio.CancelledError:
            break
        except:
            await asyncio.sleep(5)

async def main():
    if not MONGODB_CONNECTION_STRING:
        return

    session = get_session()
    async with session.create_client('sqs', region_name=AWS_REGION, config=BOTO3_CONFIG) as sqs_client:
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
        mongo_collection = mongo_client[MONGODB_DATABASE_NAME][MONGODB_COLLECTION_NAME]

        try:
            await consume_sqs_messages(sqs_client, mongo_collection, QUEUE_URL)
        finally:
            mongo_client.close()

if __name__ == "__main__":
    asyncio.run(main())
