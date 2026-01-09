FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV OLLAMA_HOST=http://127.0.0.1:11434

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ----------------------
# Install Ollama
# ----------------------
RUN curl -fsSL https://ollama.com/install.sh | sh

# ----------------------
# Install uv
# ----------------------
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure binaries are on PATH
ENV PATH="/root/.local/bin:/root/.cargo/bin:/usr/local/bin:${PATH}"

WORKDIR /app

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Ollama data persistence
VOLUME ["/root/.ollama"]

EXPOSE 8080

CMD uv run streamlit run app.py \
      --server.port=8080 \
      --server.address=0.0.0.0