# Host Checker

Small learning project for building a host-checking backend step by step.

## What Works Now

- FastAPI app
- MongoDB connection
- LocalStack SQS for local queue practice
- Docker Compose for local running
- Create a host
- List hosts
- Get one host by id
- Activate and deactivate a host
- Send SQS message when a host is created
- Read SQS messages in `health-check-service`

## Run

Start everything locally:

```powershell
docker compose up --build
```

Open API docs:

```text
http://localhost:8000/docs
```

## Project Structure

```text
api-service/
  app/
    main.py       FastAPI routes
    database.py   MongoDB connection and  settings
    queue.py      SQS client and message sender
    schemas.py    request and response models
health-check-service/
  app/
    main.py       SQS consumer loop
localstack/
  init/
    ready.d/
      create-sqs-queue.sh   creates the local SQS queue
```

## Current Endpoints

```text
GET  /health
POST /hosts
GET  /hosts
GET  /hosts/{host_id}
POST /hosts/{host_id}/deactivate
POST /hosts/{host_id}/activate
```

Deactivate one host:

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/hosts/<host_id>/deactivate"
```

Activate it again:

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/hosts/<host_id>/activate"
```

## Local SQS

The project runs SQS locally through LocalStack. On startup, it creates one queue:

```text
host-checks
```

List local queues:

```powershell
docker compose exec localstack awslocal sqs list-queues
```

When `POST /hosts` creates a host, the API sends a small SQS message:

```json
{
  "host_id": "mongo-object-id",
  "reason": "created"
}
```

Read messages from the queue:

```powershell
docker compose exec localstack awslocal sqs receive-message --queue-url http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/host-checks
```

If `health-check-service` is running, it may consume and delete messages before you read them manually.

Check consumer logs:

```powershell
docker compose logs -f health-check-service
```

Current consumer behavior:

```text
read SQS message -> print message -> delete message
```

## Next Steps

- Make `health-check-service` load the host from MongoDB by `host_id`
