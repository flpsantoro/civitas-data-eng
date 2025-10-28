# Desafio Técnico - Data Engineer CIVITAS

Pipeline de ELT para captura de dados GPS do BRT usando Prefect 1.4.1 e DBT.

## Stack

- Python 3.10 + Poetry
- Prefect 1.4.1
- DBT 1.5.0
- Google Cloud (BigQuery + Storage)
- Docker + Docker Compose

## 🚀 Quick Start (Um Comando!)

### Pré-requisito

- Docker Desktop instalado e rodando
- Arquivo `.env` configurado (já está!)
- Credenciais GCP em `credentials/` (já está!)

### Setup Completo

```powershell
# Windows
.\run.ps1 setup
```

```bash
# Linux/Mac
make setup
```

**Isso fará:**
1. ✅ Build das imagens Docker com Poetry + Google Cloud SDK
2. ✅ Subir Prefect Server + Agent + PostgreSQL
3. ✅ Criar bucket GCS e datasets BigQuery
4. ✅ Validar todo ambiente
5. ✅ Registrar flows no Prefect

**Acesse:** http://localhost:8080

## 📋 Comandos Disponíveis

### Windows (PowerShell)

```powershell
.\run.ps1 help          # Ver todos comandos
.\run.ps1 up            # Subir serviços
.\run.ps1 test          # Testar API BRT
.\run.ps1 validate      # Validar ambiente
.\run.ps1 shell         # Shell no container
.\run.ps1 logs          # Ver logs
.\run.ps1 down          # Parar tudo
```

### Linux/Mac (Makefile)

```bash
make help               # Ver todos comandos
make up                 # Subir serviços
make test               # Testar API BRT
make validate           # Validar ambiente
make shell              # Shell no container
make logs               # Ver logs
make down               # Parar tudo
```

## 🔧 Comandos GCP (dentro do Docker)

```powershell
# Windows
.\run.ps1 gcloud auth list
.\run.ps1 gsutil ls
.\run.ps1 bq ls civitas-data-eng:brt_raw
.\run.ps1 dbt debug

# Linux/Mac
make gcloud ARGS="auth list"
make gsutil ARGS="ls"
make bq ARGS="ls civitas-data-eng:brt_raw"
make dbt ARGS="debug"
```

## 📁 Estrutura

```
docker/                # Configurações Docker
  docker-compose.yml   # Stack completa
  Dockerfile           # Imagem com Poetry + gcloud

scripts/               # Utilitários
  test_brt_api.py     # Testar API BRT
  validate_environment.py  # Validar setup
  register_flows.py   # Registrar flows

pipelines/             # Código Prefect
  brt/extract_load/
    tasks.py          # Captura, CSV, Upload
    flows.py          # Orquestração
    schedules.py      # Agendamentos

queries/              # DBT (Bronze → Silver → Gold)
  models/
  macros/
  
run.ps1               # Script PowerShell (Windows)
Makefile              # Make commands (Linux/Mac)
```

## 🐛 Troubleshooting

### Erro de permissões GCP

```powershell
# Autenticar no container
.\run.ps1 shell
gcloud auth login
gcloud auth application-default login
```

### Reconstruir imagens

```powershell
.\run.ps1 build
```

### Limpar tudo

```powershell
.\run.ps1 clean
```