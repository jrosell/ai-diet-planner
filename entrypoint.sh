#!/usr/bin/env bash
set -e

echo "Starting Ollama..."
ollama serve &

echo "Waiting for Ollama to be ready..."
until curl -s http://127.0.0.1:11434/api/tags > /dev/null; do
  sleep 1
done

echo "Starting Streamlit..."
exec uv run streamlit run app.py \
  --server.port=7860 \
  --server.address=0.0.0.0 \
  --server.enableCORS=false