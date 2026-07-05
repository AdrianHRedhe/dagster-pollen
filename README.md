# Dagster pollen project
This project is a showcase of how dagster can be used to
orchestrate a simple ingestion of data into postgres. And
then to notify a user via telegram on certain events.

Specifically it will fetch data on pollen levels in
Stockholm. It will save the data each day and construct an
SCD2 table containing the valid from and valid to dates of
each status.

If there is a change in the pollen status, a message will be
sent out to the user via telegram, using a bot and a token +
chat id.

The project runs as a **Dagster code server** — it exposes
pipeline code over gRPC and registers with
[dagster-hub](https://github.com/adrianhredhe/dagster-hub.git), which hosts the shared
webserver, daemon, and run storage. This makes it easy to
add new automations as separate repos without duplicating
orchestration infrastructure.

I use uv to manage the packages. You don't need it installed
locally since everything runs in docker. You will need docker
on your machine though. Docker engine should suffice.

## Architecture
```
dagster-hub  <------------------------------------------.
  webserver (port 3001)                                  |
  daemon                                                 |
  postgres (run/event storage)                           |
                                                         | gRPC
dagster-pollen  (this repo)                              |
  code-server (port 4000) --------------------------------'
  pollen-postgres (port 5434, pollen data)
```

The hub discovers this service via its `workspace.yaml`.
See [dagster-hub](../dagster-hub) for how to register a new
code location.

## How to run
In the root of the project first fill in a .env file since
that will not be part of the repo. You need to fill in
certain values for PG and others for Telegram:

### Postgres .env values
As long as you don't make any changes to the compose file,
these values should work for postgres:
```
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypass
POSTGRES_HOST=pollen-postgres
POSTGRES_PORT=5432
```

### dagster .env values
If you are planning on running via a hub instead of
standalone.
```
DAGSTER_PG_PASSWORD=your_dagster_hub_env_password
```

### Telegram .env values
For telegram you need to create an account and message
@BotFather to create a new bot. This will give you a token.
Then you can message your bot to start the conversation, you
need to write the first message before a bot can contact
you. You can then save the message id of your conversation
with your bot. Once you have done this you can fill in the
following values in the .env file
```
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

### Starting the code server
Make sure dagster-hub is already running (it creates the
`dagster-hub_default` network that this service joins).
Then in the root of this repo:
```
docker compose up -d
```
This starts the code server on port 4000 and pollen-postgres
on port 5434.

### Checking in on runs
The program will automatically run at 07:00 UTC every day.
Go to the dagster-hub UI at `http://mini.local:3001` to
check upcoming runs, view logs, and trigger runs manually.

## Running standalone (without dagster-hub)
If you don't want to depend on dagster-hub you can run
everything locally using `dagster dev`. This starts a
combined webserver and daemon in a single process and uses
SQLite for run/event storage by default — no extra Postgres
needed for Dagster itself.

1. Start only pollen-postgres (the app still needs it):
```
docker compose up -d pollen-postgres
```

2. Install dependencies and launch the dev server via uv:
```
uv run dagster dev -w workspace.yaml
```

This starts the Dagster UI at `http://localhost:3000`. From
there you can trigger runs manually, inspect logs, and
enable the schedule.

The `DAGSTER_PG_PASSWORD` env var is only needed for the
hub setup, so you can omit it from your `.env` when running
standalone.

## Repo structure
```
.
├── compose.yaml         -- Boots the code-server and pollen-postgres; joins dagster-hub network
├── defs                 -- Contains all code for dagster to run
│   ├── __init__.py
│   ├── definitions.py   -- Contains definitions for dagster e.g. what jobs and schedules and resources to use
│   ├── jobs.py          -- Contains jobs in this instance only one of them
│   ├── operations.py    -- Contains smaller building blocks operations that make up jobs
│   ├── resources.py     -- Contains resources that can be reused between operations such as connections to db
│   └── schedules.py     -- Contains schedules for jobs
├── Dockerfile           -- Runs dagster code-server on port 4000 using uv
├── pyproject.toml       -- UV description of dependencies etc
├── README.md            -- Describes purpose of repo and how to run
├── tests                -- Contains pytest tests for dagster code
├── uv.lock
└── workspace.yaml       -- Describes entry point for dagster i.e. defs/definitions.py
```
