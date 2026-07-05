FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# Verify it works
RUN uv --version

# Copy pyproject.toml and lockfile
COPY pyproject.toml uv.lock ./

# Install deps (skip installing the project itself since source isn't copied yet)
RUN uv sync --no-install-project

# Copy the rest of your Dagster project
COPY . .

EXPOSE 4000

CMD ["uv", "run", "dagster", "code-server", "start", "-h", "0.0.0.0", "-p", "4000", "-f", "defs/definitions.py"]
