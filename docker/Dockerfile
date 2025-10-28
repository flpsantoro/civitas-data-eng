FROM python:3.10-slim as base

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
        ca-certificates \
        lsb-release && \
    # Instalar Google Cloud SDK
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
        tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
        apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && \
    apt-get install -y google-cloud-cli && \
    # Instalar Poetry
    curl -sSL https://install.python-poetry.org | python3 - && \
    # Limpar
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY ../pyproject.toml ../poetry.lock* ./

# Instalar dependências Python
RUN poetry install --no-root --no-dev

# Copiar código
COPY ../pipelines/ ./pipelines/
COPY ../queries/ ./queries/
COPY ../scripts/ ./scripts/
COPY ../.env* ./

# Criar diretórios
RUN mkdir -p data logs credentials

# Imagem para Prefect Agent
FROM base as agent
CMD ["prefect", "agent", "docker", "start", "--label", "civitas"]

# Imagem para scripts utilitários
FROM base as cli
ENTRYPOINT ["python"]
CMD ["scripts/validate_environment.py"]
