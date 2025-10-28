# Desafio Técnico - Data Engineer CIVITAS

Pipeline de ELT para captura de dados GPS do BRT usando Prefect 1.4.1 e DBT.

## Stack

- Python 3.10
- Prefect 1.4.1
- DBT 1.5.0
- Google Cloud (BigQuery + Storage)
- Docker

## Setup Rápido

```bash
# 1. Setup automático (credenciais GCP + .env)
python setup.py

# 2. Instalar dependências
poetry install

# 3. Subir Prefect
docker-compose up -d

# 4. Testar API
poetry run python test_brt_api.py

# 5. Registrar flow
poetry run python register_flows.py

# 6. Acessar UI
# http://localhost:8080
```

## Arquitetura

```
API BRT → Captura minuto a minuto → CSV (10min) → GCS → BigQuery
                                                     ↓
                                                   DBT (Bronze → Silver → Gold)
```

## Estrutura

```
pipelines/brt/extract_load/
  ├── tasks.py      # Captura, CSV, Upload
  ├── flows.py      # Orquestração
  └── schedules.py  # Agendamentos

dbt/
  ├── models/       # Transformações SQL
  └── profiles.yml  # Config BigQuery
```