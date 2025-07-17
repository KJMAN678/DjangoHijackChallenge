FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.7.21 /uv /bin/uv

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
COPY . /app
RUN uv sync --dev
