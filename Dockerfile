FROM python:3.12-slim

WORKDIR /app
COPY app/server.py /app/server.py

RUN useradd --uid 65532 --create-home --shell /usr/sbin/nologin appuser \
    && chown appuser:appuser /app/server.py

USER 65532

ENV PORT=8080 \
    MESSAGE="hello from the exercise" \
    APP_VERSION=0.1.0

EXPOSE 8080

CMD ["python", "-u", "/app/server.py"]
