FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 🔴 REQUIRED by Hugging Face
ENV PORT=7860
ENV OLLAMA_HOST=http://127.0.0.1:11434

# 🔴 Persist Ollama models on HF storage
ENV OLLAMA_MODELS=/data/ollama

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama (CPU)
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure binaries are on PATH
ENV PATH="/root/.local/bin:/root/.cargo/bin:/usr/local/bin:${PATH}"

WORKDIR /app

# Copy dependency files first (cache-friendly)
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# 🔴 Hugging Face persistent storage mount
VOLUME ["/data"]

# 🔴 Hugging Face expects 7860
EXPOSE 7860

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
