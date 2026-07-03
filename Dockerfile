# Legal Research & Paralegal MCP Server
# Optional container image. Runs the server over SSE by default.
FROM python:3.12-slim

# Avoid interactive prompts and keep Python output unbuffered.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source.
COPY . .

# Bind to all interfaces inside the container so the port is reachable.
ENV HOST=0.0.0.0 \
    PORT=8000 \
    MCP_TRANSPORT=sse

EXPOSE 8000

# Feature flags for optional live integrations (disabled by default).
# Override at runtime, e.g.:
#   docker run -e COURTLISTENER_ENABLED=true \
#              -e COURTLISTENER_API_TOKEN=... legal-mcp
ENV COURTLISTENER_ENABLED=false \
    PACER_ENABLED=false \
    PACER_ENVIRONMENT=qa

CMD ["python", "main.py"]
