FROM python:3.11-slim as base

LABEL maintainer="Data Engineer Challenge"
LABEL description="Pipeline BRT - CIVITAS"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.5.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    DEBIAN_FRONTEND=noninteractive

# Adicionar Poetry ao PATH
ENV PATH="$POETRY_HOME/bin:/app/scripts:$PATH"

WORKDIR /app

    # Instalar dependências do sistema + Google Cloud SDK
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
            curl \
            gnupg \
            apt-transport-https \
            ca-certificates && \
        # Instalar Google Cloud SDK (método moderno - sem apt-key)
        echo "deb [signed-by=/usr/share/keyrings/cloud.google.asc] https://packages.cloud.google.com/apt cloud-sdk main" | \
            tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
        curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
            gpg --dearmor -o /usr/share/keyrings/cloud.google.asc && \
        apt-get update && \
        apt-get install -y google-cloud-cli && \
        # Instalar Poetry
        curl -sSL https://install.python-poetry.org | python3 - && \
        # Limpar
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock* ./

# Instalar dependências Python
RUN poetry install --no-root --no-dev

# Copiar código
COPY pipelines/ ./pipelines/
COPY dbt/ ./dbt/
COPY .env* ./

# Criar diretórios
RUN mkdir -p data logs credentials

# Instalar DBT com adaptador BigQuery
RUN pip install --no-cache-dir \
    dbt-core==1.7.0 \
    dbt-bigquery==1.7.0 \
    'google-cloud-bigquery<3.11.0'

# Prefect Agent
FROM base as agent
CMD ["tail", "-f", "/dev/null"]
