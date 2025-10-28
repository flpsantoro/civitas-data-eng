# Próximos Passos

## ✅ Configuração Completa

- ✅ Estrutura organizada (padrão pipelines_rj_civitas)
- ✅ Credenciais GCP em `credentials/civitas-data-eng-8feab1c31a9a.json`
- ✅ `.env` configurado corretamente
- ✅ Poetry para gerenciamento de dependências
- ✅ Docker Compose para ambiente local

## 🚀 Para Rodar o Pipeline

### 1. Criar Recursos no GCP

```bash
# Verificar se está no projeto correto
gcloud config get-value project  # Deve retornar: civitas-data-eng

# Criar bucket GCS
gsutil mb -l us-east1 gs://civitas-brt-data

# Criar datasets BigQuery
bq mk --dataset --location=us-east1 civitas-data-eng:brt_raw
bq mk --dataset --location=us-east1 civitas-data-eng:brt_staging
bq mk --dataset --location=us-east1 civitas-data-eng:brt_gold
```

### 2. Validar Permissões

```bash
# Ver permissões da service account
gcloud projects get-iam-policy civitas-data-eng \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:civitas@civitas-data-eng.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
```

Se necessário, adicione as roles (ver `credentials/README.md`)

### 3. Validar Ambiente

```bash
# Instalar dependências
poetry install

# Executar validação completa
poetry run python validate_environment.py
```

Este script valida automaticamente:
- Variáveis de ambiente
- Credenciais GCP
- Bucket GCS
- Datasets BigQuery
- Prefect Server

Se tudo estiver OK, prossiga para o próximo passo.

### 4. Testar Conexão

```bash
# Testar API BRT
poetry run python test_brt_api.py

# Deve retornar JSON com dados de ônibus
```

### 5. Subir Prefect

```bash
# Subir servidor e agent
docker-compose up -d

# Verificar logs
docker-compose logs -f
```

### 6. Registrar Flow

```bash
# Instalar dependências
poetry install

# Registrar flow no Prefect
poetry run python register_flows.py
```

### 7. Acessar UI

Abra: http://localhost:8080

- Você verá o flow "brt-extract-load" registrado
- Pode executar manualmente ou aguardar o schedule

## 📊 Implementar Transformações DBT

Os modelos DBT ainda não estão implementados. Estrutura sugerida:

```
queries/models/
  ├── bronze/           # Dados raw (external tables)
  │   └── brt_gps.sql
  ├── staging/          # Limpeza e padronização
  │   └── stg_brt_gps.sql
  └── marts/            # Agregações e métricas
      └── brt_trips.sql
```

## 🐛 Troubleshooting

### Erro de Permissões

```bash
# Adicionar roles necessárias (ver credentials/README.md)
```

### Erro no Docker

```bash
# Rebuild da imagem
docker-compose build --no-cache

# Restart
docker-compose restart
```

### Erro no DBT

```bash
# Verificar profiles
cat ~/.dbt/profiles.yml

# Testar conexão
poetry run dbt debug --project-dir queries
```
