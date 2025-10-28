# Desafio Técnico - Data Engineer CIVITAS

Pipeline de ELT para captura de dados GPS do BRT usando Prefect 1.4.1 e DBT.

## Stack

- Python 3.10 + Poetry
- Prefect 1.4.1
- DBT 1.5.0
- Google Cloud (BigQuery + Storage)
- Docker + Docker Compose

## Configuração Inicial

### 1. Credenciais GCP

**Opção A: Service Account (Já configurado)**

Você já tem o arquivo JSON em `credentials/civitas-data-eng-8feab1c31a9a.json`. O `.env` está pronto.

Valide as permissões necessárias:
```bash
# A service account precisa das roles:
# - BigQuery Admin (ou Data Editor + Job User)
# - Storage Admin (ou Object Admin)
```

**Opção B: OAuth (Alternativa)**

Se preferir usar sua conta pessoal:
```bash
# 1. Autenticar
gcloud auth application-default login

# 2. Editar .env e comentar GOOGLE_APPLICATION_CREDENTIALS
# GOOGLE_APPLICATION_CREDENTIALS=credentials/civitas-data-eng-8feab1c31a9a.json
```

### 2. Configurar GCP Resources

```bash
# Definir projeto
gcloud config set project civitas-data-eng

# Criar bucket (ajuste o nome se necessário)
gsutil mb -l us-east1 gs://civitas-brt-data

# Criar datasets BigQuery
bq mk --dataset --location=us-east1 civitas-data-eng:brt_raw
bq mk --dataset --location=us-east1 civitas-data-eng:brt_staging
bq mk --dataset --location=us-east1 civitas-data-eng:brt_gold
```

### 3. Configurar DBT

```bash
# Copiar profile de exemplo
cp queries/profiles.yml.example ~/.dbt/profiles.yml

# Editar ~/.dbt/profiles.yml
# Como você usa service account, o method já é correto (oauth)
# O DBT vai usar automaticamente GOOGLE_APPLICATION_CREDENTIALS do .env
```

## Execução

### Validar Ambiente

Antes de tudo, valide se está tudo configurado:

```bash
# Instalar dependências
poetry install

# Validar ambiente completo
poetry run python validate_environment.py
```

O script verifica:
- ✅ Variáveis de ambiente (.env)
- ✅ Credenciais GCP
- ✅ Bucket GCS existe
- ✅ Datasets BigQuery existem
- ✅ Prefect Server acessível

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