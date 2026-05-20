# Host Checker

Small learning project for building a host-checking backend step by step.

Current version:

```text
User -> FastAPI service <-> MongoDB
```

The long-term idea is to later add SQS, a health-check service, and an analyzer service. For now, the project only stores hosts and reads them back.

## What Works Now

- FastAPI app
- MongoDB connection
- Docker Compose for local running
- Create a host
- List hosts
- Get one host by id

## Run

Start the app and MongoDB:

```powershell
docker compose up --build
```

Open API docs:

```text
http://localhost:8000/docs
```

Check app health:

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/health"
```

## Try The API

Create a host:

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/hosts" -ContentType "application/json" -Body (@{ name = "Google"; url = "https://google.com"; check_interval_seconds = 300 } | ConvertTo-Json)
```

List hosts:

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/hosts"
```

Get one host:

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/hosts/<host_id>"
```

## Project Structure

```text
api-service/
  app/
    main.py       FastAPI routes
    database.py   MongoDB settings and connection
    schemas.py    request and response models
```

## Current Endpoints

```text
GET  /health
POST /hosts
GET  /hosts
GET  /hosts/{host_id}
```

## Next Steps

- Add deactivate host endpoint
- Add activate host endpoint
- Add SQS after basic host CRUD feels clear
