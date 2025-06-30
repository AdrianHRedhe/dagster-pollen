FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# Verify it works
RUN uv --version

# Copy pyproject.toml
COPY pyproject.toml .
# COPY uv.lock .  # <-- only if you want reproducibility (optional but recommended)

# Install deps
RUN uv sync

# Copy the rest of your Dagster project
COPY . .

EXPOSE 3000

CMD ["uv", "run", "dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]
