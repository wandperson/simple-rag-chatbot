# ----- Use a specific images for supply chain security -----
# Python 3.12-slim
ARG PYTHON_IMAGE=python:3.12-slim
# uv 0.11.7-python3.12-trixie
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.11.7-python3.12-trixie@sha256:3b66071aa339eec6e5149dbc7f2c07144d71f4c25c6aab3959e87747e5c45e35


# -------------------- BUILD --------------------
FROM ${UV_IMAGE} AS uv
FROM ${PYTHON_IMAGE} AS builder

# Install uv
COPY --from=uv /usr/local/bin/uv /bin/

# Install the application dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-cache


# -------------------- RUNTIME --------------------
FROM ${PYTHON_IMAGE}

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos "" appuser

# Copy the application dependencies
COPY --from=builder /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Copy the application source
COPY src/app /app

# Grant ownership of the database directory to the non-root user
RUN chown -R appuser:appuser /app/database

# Expose the application port
EXPOSE 8000

# Switch to the non-root user
USER appuser

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
