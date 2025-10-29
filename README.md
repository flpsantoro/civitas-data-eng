# CIVITAS - Pipeline BRT GPS

Pipeline de dados automatizado para o desafio [Prefeitura Rio - Civitas Data Engineering](https://github.com/prefeitura-rio/civitas-desafio-data-eng/).

---

## 🚀 Como Executar

### 1. Configurar credenciais GCP
```bash
# Copiar arquivo JSON para:
credentials/civitas-data-eng-*.json
```

### 2. Subir container
```bash
cd docker
docker-compose up -d
```

### 3. Executar pipeline
```bash
docker exec civitas-prefect-agent python -m pipelines.brt.extract_load.flows
```

**Tempo:** ~40 segundos

---

## 📦 Entregáveis

### Pipeline Prefect
- **Localização:** `pipelines/brt/extract_load/`
- **Tasks:** 11 tasks automatizadas (cleanup, fetch API, upload GCS, create tables, validações)
- **Arquitetura:** Bronze → Silver → Gold (Medallion)

### Projeto DBT
- **Localização:** `dbt/models/`
- **Bronze:** External Table (`brt_gps_external`)
- **Silver:** View transformada (`stg_brt_gps`)
- **Gold:** 4 tabelas analíticas criadas via SQL nativo

### Dados Processados
- **CSV exemplo:** `csv_exemplo_brt_gps.csv` (~730 registros)
- **API:** https://dados.mobilidade.rio/gps/brt
- **BigQuery:**
  - Bronze: 731 registros
  - Gold: 36 linhas + 731 veículos + 731 viagens + 40 métricas

### Docker
- **Localização:** `docker/`
- **Container:** `civitas-prefect-agent`
- **Stack:** Python 3.11 + Prefect 1.4.1 + DBT 1.7.0

---

## ✅ Validação

```sql
SELECT COUNT(*) FROM `civitas-data-eng.civitas_bronze.brt_gps_external`;
SELECT COUNT(*) FROM `civitas-data-eng.civitas_gold.dim_brt_linhas`;
```

---

**Desafio:** https://github.com/prefeitura-rio/civitas-desafio-data-eng/
