FROM python:3.10-slim

LABEL maintainer="Data Engineer Challenge"
LABEL description="Pipeline BRT - CIVITAS"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.5.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Adicionar Poetry ao PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Instalar Poetry
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock* ./

# Instalar dependências
RUN poetry install --no-root --no-dev

# Copiar código
COPY pipelines/ ./pipelines/
COPY queries/ ./queries/

# Criar diretórios
RUN mkdir -p data logs credentials

CMD ["prefect", "agent", "docker", "start"]
