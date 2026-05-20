## What Works Now

- FastAPI app
- MongoDB connection
- Docker Compose for local running
- Create a host
- List hosts
- Get one host by id

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
