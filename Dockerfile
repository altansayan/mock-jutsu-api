# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Layer cache: dependency files first — pip layer reused unless deps change
COPY pyproject.toml setup.py ./
COPY src/ ./src/

RUN pip install --no-cache-dir . granian

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/granian /usr/local/bin/granian
COPY --from=builder /usr/local/bin/mockjutsu /usr/local/bin/mockjutsu

# Copy API source — changes often, stays at end for cache efficiency
COPY api/ ./api/
COPY --chown=appuser:appgroup entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

ENTRYPOINT ["./entrypoint.sh"]
