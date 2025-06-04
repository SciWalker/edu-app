# PostgreSQL Migration Guide

This document outlines the steps taken to migrate the edu-app database from SQLite to PostgreSQL.

## Changes Made

1. **Database Schema**: Created a PostgreSQL-compatible schema in `database/schema.sql`
2. **Database Connection**: Updated `database/db.py` to use `psycopg2` for PostgreSQL connections
3. **Query Syntax**: Changed parameter placeholders from `?` to `%s` and updated SQL syntax
4. **Configuration**: Added a `config.py` file for database connection settings
5. **Docker Support**: Added a `docker-compose.yml` file for easy PostgreSQL setup

## Setup Instructions

### Prerequisites

- Docker and Docker Compose (for containerized PostgreSQL)
- Python 3.7+ with pip

### Setting Up PostgreSQL

1. Start the PostgreSQL container:

```bash
docker-compose up -d
```

2. Verify the container is running:

```bash
docker ps
```

### Environment Variables

You can customize the PostgreSQL connection by setting these environment variables:

```bash
export POSTGRES_DB=edu_app
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
```

### Running the Application

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python backend_server.py
```

## Key Differences Between SQLite and PostgreSQL

1. **Parameter Placeholders**: 
   - SQLite uses `?` for query parameters
   - PostgreSQL uses `%s` for query parameters

2. **Auto-incrementing IDs**:
   - SQLite uses `INTEGER PRIMARY KEY AUTOINCREMENT`
   - PostgreSQL uses `SERIAL PRIMARY KEY`

3. **Returning Inserted IDs**:
   - SQLite provides `cursor.lastrowid`
   - PostgreSQL requires `RETURNING id` clause

4. **Schema Information**:
   - SQLite uses `PRAGMA table_info(table_name)`
   - PostgreSQL uses `information_schema` tables

5. **Case Sensitivity**:
   - PostgreSQL is case-sensitive for identifiers unless quoted
   - SQLite is generally case-insensitive

6. **Transaction Support**:
   - PostgreSQL has more robust transaction support
   - SQLite has simpler transaction model

## Troubleshooting

If you encounter connection issues:

1. Verify PostgreSQL is running: `docker ps`
2. Check connection parameters in `config.py`
3. Ensure PostgreSQL port is accessible: `nc -zv localhost 5432`
4. View PostgreSQL logs: `docker logs edu_app_postgres`
