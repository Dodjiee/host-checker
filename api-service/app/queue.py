import json
import os

import boto3


AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
SQS_QUEUE_NAME = os.environ.get("SQS_QUEUE_NAME", "host-checks")
SQS_ENDPOINT_URL = os.environ.get("SQS_ENDPOINT_URL", "http://localhost:4566")


def get_sqs_client():
    return boto3.client(
        "sqs",
        region_name=AWS_REGION,
        endpoint_url=SQS_ENDPOINT_URL,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


def get_queue_url() -> str:
    sqs_client = get_sqs_client()
    response = sqs_client.get_queue_url(QueueName=SQS_QUEUE_NAME)
    return response["QueueUrl"]


def send_host_check_message(host_id: str, reason: str, host_name) -> None:
    sqs_client = get_sqs_client()
    queue_url = get_queue_url()
    message_body = {
        "host_id": host_id,
        "reason": reason,
        "host_name":host_name,
    }

    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body),
    )
