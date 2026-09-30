# URL Shortener API

Learning-project API built with FastAPI.

## Milestone 2: PostgreSQL Database Connection

Install PostgreSQL locally and make sure the PostgreSQL server is running. Then open `psql` as a PostgreSQL administrator and create a database user and database:

```sql
CREATE USER url_shortener WITH PASSWORD 'change-me';
CREATE DATABASE url_shortener OWNER url_shortener;
```

Copy the environment template and update the password if you chose a different one:

```powershell
Copy-Item .env.example .env
```

The default `.env` value expects PostgreSQL at `localhost:5432`:

```text
DATABASE_URL=postgresql+psycopg://url_shortener:change-me@localhost:5432/url_shortener
```

Create and activate a virtual environment, then install the project and development dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -e ".[dev]"
```

Verify the configured database connection manually without starting the API:

```powershell
py -c "from app.database import verify_database_connection; verify_database_connection(); print('Database connection OK')"
```

The application does not connect to PostgreSQL during module import, so it can still start when PostgreSQL is unavailable. The manual verification command performs the connection check explicitly.

## Milestone 2: Create a Short Link

Apply the initial database migration after configuring PostgreSQL:

```powershell
py -m alembic upgrade head
```

Create a link:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/links -ContentType "application/json" -Body '{"url":"https://example.com/article?id=123"}'
```

The API returns the generated short code, public short URL, original URL, database ID, and creation timestamp. Redirect behavior is intentionally deferred to Milestone 3.

## Milestone 3: Code Lookup and Redirects

Existing short codes can now redirect to their stored original URLs:

```text
GET http://localhost:8000/{short_code}
```

Known codes return `302 Found` with a `Location` header. Unknown codes return `404 Not Found`. Redirects do not fetch the destination server-side and do not record click statistics yet.

## Milestone 4: Duplicate URL Handling

Equivalent URLs reuse the existing short link. A newly stored URL returns `201 Created`; a matching normalized URL returns `200 OK` with `X-Link-Existing: true`. The original URL is preserved for redirects, while `normalized_url` is used only for duplicate comparison.

Apply the latest migration after configuring PostgreSQL:

```powershell
py -m alembic upgrade head
```

## Milestone 5: Statistics

Successful `GET /{short_code}` redirects now increment the link's aggregate click count and update `last_clicked_at` atomically. Statistics are available without incrementing the count:

```text
GET http://localhost:8000/api/v1/links/{short_code}/stats
```

The statistics response includes `short_code`, `original_url`, `click_count`, `last_clicked_at`, and `created_at`. Per-click event history, visitor data, and analytics are not stored.

## Milestone 1: Health Check

Run the API:

```powershell
uvicorn app.main:app --reload
```

The health endpoint is available at `http://127.0.0.1:8000/health` and the interactive API documentation is at `http://127.0.0.1:8000/docs`.

Run the tests:

```powershell
py -m pytest
```

The default test suite does not require a running PostgreSQL server. The database verification tests use in-memory SQLite or mocked failures. A live PostgreSQL test is optional and should be run manually with the verification command above after configuring `.env`.