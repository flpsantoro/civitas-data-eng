# Próximos Passos

## ✅ Configuração Completa

- ✅ Estrutura organizada (padrão pipelines_rj_civitas)
- ✅ Credenciais GCP em `credentials/civitas-data-eng-8feab1c31a9a.json`
- ✅ `.env` configurado corretamente
- ✅ Docker com Poetry + Google Cloud SDK
- ✅ Scripts de automação (`run.ps1` / `Makefile`)

## 🚀 Setup Completo (Um Comando!)

### Pré-requisito

✅ **Docker Desktop** instalado e rodando

### Executar Setup

```powershell
# Windows
.\run.ps1 setup
```

```bash  
# Linux/Mac
make setup
```

**O que esse comando faz:**

1. 🔨 Build das imagens Docker (Poetry + Google Cloud SDK inclusos)
2. 🚀 Sobe Prefect Server + Agent + PostgreSQL
3. 🪣 Cria bucket GCS: `gs://civitas-brt-data`
4. 📊 Cria datasets BigQuery: `brt_raw`, `brt_staging`, `brt_gold`
5. ✅ Valida todo ambiente (credenciais, recursos, conexões)
6. 📝 Registra flows no Prefect Server

### Acessar UI

Após o setup: **http://localhost:8080**

## 📋 Comandos Úteis

### Controle de Serviços

```powershell
# Windows
.\run.ps1 up           # Subir serviços
.\run.ps1 down         # Parar serviços
.\run.ps1 restart      # Reiniciar serviços
.\run.ps1 logs         # Ver logs em tempo real

# Linux/Mac
make up
make down
make restart
make logs
```

### Scripts Utilitários

```powershell
# Windows
.\run.ps1 test         # Testar API do BRT
.\run.ps1 validate     # Validar ambiente completo
.\run.ps1 register     # Registrar flows
.\run.ps1 shell        # Abrir shell no container

# Linux/Mac
make test
make validate
make register
make shell
```

### Comandos GCP (dentro do Docker)

Todos os comandos GCP rodam dentro do container com as credenciais já configuradas:

```powershell
# Windows
.\run.ps1 gcloud config get-value project
.\run.ps1 gsutil ls gs://civitas-brt-data
.\run.ps1 bq ls civitas-data-eng:brt_raw
.\run.ps1 dbt debug

# Linux/Mac
make gcloud ARGS="config get-value project"
make gsutil ARGS="ls gs://civitas-brt-data"
make bq ARGS="ls civitas-data-eng:brt_raw"
make dbt ARGS="debug"
```

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
docker compose -f docker/docker-compose.yml build --no-cache

# Restart
docker compose -f docker/docker-compose.yml restart
```

### Erro no DBT

```bash
# Verificar profiles
cat ~/.dbt/profiles.yml

# Testar conexão
poetry run dbt debug --project-dir queries
```
