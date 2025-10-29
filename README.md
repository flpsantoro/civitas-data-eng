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

## 🔍 Visualizar Dados (Público)

Os dados processados podem ser consultados diretamente no BigQuery:

### Bronze (External Table - 731 registros)
https://console.cloud.google.com/bigquery?project=civitas-data-eng&ws=!1m5!1m4!4m3!1scivitas-data-eng!2scivitas_bronze!3sbrt_gps_external

### Silver (View transformada)
https://console.cloud.google.com/bigquery?project=civitas-data-eng&ws=!1m5!1m4!4m3!1scivitas-data-eng!2scivitas_silver!3sstg_brt_gps

### Gold (Tabelas Analíticas)
- **Linhas BRT (36):** https://console.cloud.google.com/bigquery?project=civitas-data-eng&ws=!1m5!1m4!4m3!1scivitas-data-eng!2scivitas_gold!3sdim_brt_linhas
- **Veículos (731):** https://console.cloud.google.com/bigquery?project=civitas-data-eng&ws=!1m5!1m4!4m3!1scivitas-data-eng!2scivitas_gold!3sdim_brt_veiculos
- **Viagens (731):** https://console.cloud.google.com/bigquery?project=civitas-data-eng&ws=!1m5!1m4!4m3!1scivitas-data-eng!2scivitas_gold!3sfct_brt_viagens
- **Métricas Horárias (40):** https://console.cloud.google.com/bigquery?project=civitas-data-eng&ws=!1m5!1m4!4m3!1scivitas-data-eng!2scivitas_gold!3sagg_metricas_horarias

> **Nota:** Para tornar os datasets públicos, execute no GCP Cloud Shell:
> ```bash
> bq update --set_iam_policy <(echo '{"bindings":[{"role":"roles/bigquery.dataViewer","members":["allAuthenticatedUsers"]}]}') civitas-data-eng:civitas_bronze
> bq update --set_iam_policy <(echo '{"bindings":[{"role":"roles/bigquery.dataViewer","members":["allAuthenticatedUsers"]}]}') civitas-data-eng:civitas_silver
> bq update --set_iam_policy <(echo '{"bindings":[{"role":"roles/bigquery.dataViewer","members":["allAuthenticatedUsers"]}]}') civitas-data-eng:civitas_gold
> ```

---

**Desafio:** https://github.com/prefeitura-rio/civitas-desafio-data-eng/
