import json
import logging
import os
import time

import boto3
from botocore.exceptions import ClientError


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
SQS_QUEUE_NAME = os.environ.get("SQS_QUEUE_NAME", "host-checks")
SQS_ENDPOINT_URL = os.environ.get("SQS_ENDPOINT_URL", "http://localstack:4566")


def get_sqs_client():
    return boto3.client(
        "sqs",
        region_name=AWS_REGION,
        endpoint_url=SQS_ENDPOINT_URL,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


def get_queue_url(sqs_client) -> str:
    while True:
        try:
            response = sqs_client.get_queue_url(QueueName=SQS_QUEUE_NAME)
            return response["QueueUrl"]
        except ClientError:
            logger.info("Queue '%s' is not ready yet. Waiting...", SQS_QUEUE_NAME)
            time.sleep(2)


def handle_message(message: dict) -> None:
    body = json.loads(message["Body"])
    logger.info("Received host check message: %s", body)


def run_consumer() -> None:
    sqs_client = get_sqs_client()
    queue_url = get_queue_url(sqs_client)
    logger.info("Health check service is listening to queue: %s", queue_url)

    while True:
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )

        for message in response.get("Messages", []):
            handle_message(message)
            sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message["ReceiptHandle"],
            )
            logger.info("Message deleted from queue.")


if __name__ == "__main__":
    run_consumer()
