#!/bin/bash

echo "Running database migrations..."
for i in {1..10}; do
  alembic upgrade head && break
  echo "Migration attempt $i failed, retrying in 3s..."
  sleep 3
done

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
