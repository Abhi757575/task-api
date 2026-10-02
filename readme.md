# 📝 Task API

A RESTful CRUD API built with **FastAPI**, now backed by **PostgreSQL** for persistent storage.

The entire stack — app, database, and cache — runs with a single `docker compose up`.

---

## 🚀 Features

- FastAPI backend with async Postgres (asyncpg)
- Full CRUD operations with input validation
- **Pluggable repository pattern** — swap storage without touching routes or service logic
- PostgreSQL with Docker volume for data persistence
- Redis container ready for Week 4 (cache / pub-sub)
- Automatic Swagger UI documentation
- One-command startup via Docker Compose
- `.env`-driven configuration (gitignored; `.env.example` committed)

---

## 🛠️ Tech Stack

| Layer        | Technology           |
|--------------|----------------------|
| API          | FastAPI + Uvicorn    |
| Validation   | Pydantic v2          |
| Database     | PostgreSQL 16        |
| DB Driver    | asyncpg              |
| Cache        | Redis 7 (stretch)    |
| Container    | Docker + Compose     |

---

## 📦 Project Structure

```
task-api/
├── main.py               # FastAPI app — routes & lifespan
├── repository.py          # Abstract TaskRepository interface
├── memory_repository.py   # In-memory implementation (original A2)
├── pg_repository.py       # PostgreSQL implementation (Week 3)
├── requirements.txt       # Python dependencies
├── Dockerfile             # App container image
├── docker-compose.yml     # Full stack (app + db + redis)
├── .env.example           # Sample environment variables
├── .env                   # Real env vars (gitignored)
├── .dockerignore
├── db/
│   └── init.sql           # Table creation + seed data
├── docs/
│   └── swagger-ui.png
└── readme.md
```

---

## ▶️ Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Clone & configure

```bash
git clone https://github.com/Abhi757575/task-api.git
cd task-api
git checkout week-3
cp .env.example .env      # defaults work out of the box
```

### 2. Start the stack

```bash
docker compose up --build
```

This starts:
| Service | Port  |
|---------|-------|
| App     | 8000  |
| Postgres| 5432  |
| Redis   | 6379  |

### 3. Use the API

- **Swagger UI** → [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** → [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health check** → [http://localhost:8000/health](http://localhost:8000/health)

---

## 🔌 API Endpoints

| Method | Endpoint         | Description              |
|--------|------------------|--------------------------|
| GET    | `/`              | API information          |
| GET    | `/health`        | Health check + backend   |
| GET    | `/tasks`         | List all tasks           |
| GET    | `/tasks/{id}`    | Get a task by ID         |
| POST   | `/tasks`         | Create a new task        |
| PUT    | `/tasks/{id}`    | Update an existing task  |
| DELETE | `/tasks/{id}`    | Delete a task            |

---

## 🏗️ Architecture — Repository Pattern

**Service and routes are unchanged from Week 2.** Only the storage layer was swapped.

```
Routes (main.py)  →  TaskRepository (interface)  →  PgTaskRepository
                                                  or MemoryTaskRepository
```

- [`repository.py`](repository.py) — abstract interface
- [`memory_repository.py`](memory_repository.py) — original in-memory list (unchanged from A2)
- [`pg_repository.py`](pg_repository.py) — new PostgreSQL implementation

The active backend is selected automatically:
- If `DATABASE_URL` is set → Postgres
- If not → in-memory fallback

**No route or schema code was modified to add Postgres support.** That's the architecture proving itself.

---

## 🔒 Environment Variables

| Variable       | Purpose                    | Default (in `.env.example`)                     |
|----------------|----------------------------|-------------------------------------------------|
| `DATABASE_URL` | Postgres connection string | `postgresql://taskuser:taskpass@db:5432/taskdb`  |
| `REDIS_URL`    | Redis connection string    | `redis://redis:6379/0`                           |

`.env` is gitignored. `.env.example` is committed so new contributors know what to set.

---

## ✅ Persistence Proof

How to verify that data survives a full restart:

```bash
# 1. Start the stack
docker compose up --build -d

# 2. Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Persist me!\"}"

# 3. Confirm it exists
curl http://localhost:8000/tasks

# 4. Stop & destroy the containers (volume survives)
docker compose down

# 5. Start again
docker compose up -d

# 6. Check — the task is still there
curl http://localhost:8000/tasks
```

The task created in step 2 is still returned in step 6 because the Postgres data lives in the `pgdata` Docker volume, which is **not** removed by `docker compose down`.

> To truly wipe data, run `docker compose down -v` (the `-v` flag removes volumes).

---

## 🧪 Running Without Docker (dev mode)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

**Without Postgres** (falls back to in-memory):
```bash
uvicorn main:app --reload
```

**With a local Postgres**:
```bash
set DATABASE_URL=postgresql://taskuser:taskpass@localhost:5432/taskdb
uvicorn main:app --reload
```

---

## 🚀 Stretch Goals

### ✅ Redis in Compose
Redis 7 is included in `docker-compose.yml`. On startup the app pings Redis and logs the result:
```
✅ Redis ping → True
```

### Index + EXPLAIN ANALYZE (optional)
```sql
-- Connect to the database
docker compose exec db psql -U taskuser -d taskdb

-- Before index
EXPLAIN ANALYZE SELECT * FROM tasks WHERE title = 'Persist me!';

-- Create index
CREATE INDEX idx_tasks_title ON tasks (title);

-- After index
EXPLAIN ANALYZE SELECT * FROM tasks WHERE title = 'Persist me!';
```

---

## 📄 License

This project was created for educational purposes as part of a FastAPI CRUD API assignment (Week 3).