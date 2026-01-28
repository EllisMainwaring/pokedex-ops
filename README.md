PokéDex Ops

PokéDex Ops is a backend data service that ingests Pokémon data from an external API, stores it in a relational database, and exposes analytics and reporting endpoints through a RESTful API.

Although Pokémon is used as the dataset, the project focuses on backend architecture, data modelling, and API design, this is meant to mirror how how real systems integrate and analyse third-party data.

Project Overview

Modern applications often rely on external APIs for data, but directly querying those APIs can be slow, unreliable, or limiting.
PokéDex Ops solves this by:

pulling data from an external API (PokéAPI)

normalising and storing it locally in a SQL database

exposing clean, fast endpoints for querying and analytics

This approach reflects how production systems handle third-party data sources.

Key Features

External API Integration
Fetches Pokémon data from PokéAPI using HTTP requests.

Relational Data Storage
Stores Pokémon, stats, and types in a SQL database using SQLAlchemy ORM.

Proper Data Modelling
Implements many-to-many relationships (Pokémon ↔ Types).

Batch Data Ingestion
Supports automated syncing of Pokémon data in bulk (e.g. gen 1 IDs 1–151).

Analytics Endpoints
Provides aggregated insights such as:

Top Pokémon by stat (attack, speed, etc.)

Pokémon count per type

Health & Monitoring Endpoint
Includes a lightweight /health endpoint to confirm service availability.

Interactive API Documentation
Automatically generated Swagger UI via FastAPI (/docs).


FastAPI handles routing and request/response logic

SQLAlchemy abstracts SQL queries into Python objects

SQLite is used for development; easily swappable for PostgreSQL in production

Tech Stack:

Python

FastAPI

SQLAlchemy (ORM)

SQLite (development database)

PokéAPI (external data source)

Uvicorn (ASGI server)

API Endpoints (Examples)
Health Check
GET /health


Confirms the API is running and responsive.

Sync Pokémon Data
POST /sync/pokemon/{pokemon_id}
POST /sync/pokemon/batch?start=1&end=151


Fetches Pokémon data from PokéAPI and stores it locally.

Query Stored Data
GET /pokemon


Returns all stored Pokémon.

Analytics
GET /analytics/top?stat=attack&limit=10
GET /analytics/type-distribution


Provides aggregated insights from the local database.

How to Run Locally
1. Clone the repository

git clone https://github.com/EllisMainwaring/pokedex-ops.git
cd pokedex-ops

2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows

3. Install dependencies
pip install -r requirements.txt

4. Run the API
uvicorn app.main:app --reload

5. Open the API docs
http://127.0.0.1:8000/docs

Design Decisions

Why store data locally instead of querying PokéAPI directly?
To improve reliability, performance, and enable analytics without repeated external calls.

Why SQLite?
Lightweight and simple for development. The architecture supports migrating to PostgreSQL for production use.

Why FastAPI?
Modern, high-performance framework with automatic documentation and strong typing support.

Project Status

- Core backend complete
- Data ingestion and analytics implemented
- Ready for extension (authentication, background jobs, production DB)

Author

Ellis Mainwaring
BSc Computer Science — Manchester Metropolitan University test2