# Desafio Técnico - Data Engineer CIVITAS

Pipeline de ELT para captura de dados GPS do BRT usando Prefect 1.4.1 e DBT.

## Stack

- Python 3.10 + Poetry
- Prefect 1.4.1
- DBT 1.5.0
- Google Cloud (BigQuery + Storage)
- Docker + Docker Compose

## Configuração Inicial

### 1. Configurar GCP

```bash
# Autenticar
gcloud auth application-default login

# Definir projeto
gcloud config set project SEU_PROJECT_ID

# Criar bucket
gsutil mb gs://SEU_BUCKET_NAME
```

### 2. Configurar .env

Copie `.env.example` para `.env` e ajuste:

```bash
cp .env.example .env
```

Edite `.env` com seus valores:
```env
GCP_PROJECT_ID=seu-projeto-id
GCS_BUCKET_NAME=seu-bucket-brt
```

Se usar service account, descomente e configure:
```env
GOOGLE_APPLICATION_CREDENTIALS=credentials/seu-arquivo.json
```

### 3. Configurar DBT

```bash
# Copiar profiles
cp queries/profiles.yml.example ~/.dbt/profiles.yml

# Editar com seu project_id se necessário
```

## Execução

### Opção 1: Com Docker (Recomendado)

```bash
# Subir Prefect Server
docker-compose up -d

# Instalar dependências localmente (para registro)
poetry install

# Registrar flow
poetry run python register_flows.py

# Acessar UI
http://localhost:8080
```

### Opção 2: Local (Desenvolvimento)

```bash
# Instalar
poetry install

# Terminal 1: Prefect Server
poetry run prefect backend server
poetry run prefect server start

# Terminal 2: Agent
poetry run prefect agent local start --label civitas

# Terminal 3: Registrar
poetry run python register_flows.py
```

## Estrutura

```
pipelines/
  brt/extract_load/
    tasks.py      # Captura, CSV, Upload
    flows.py      # Orquestração
    schedules.py  # Agendamentos
  flows.py        # Registro central

queries/           # DBT (Bronze → Silver → Gold)
  models/
  macros/
  seeds/
```