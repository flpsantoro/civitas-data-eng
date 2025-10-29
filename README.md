# CIVITAS - Pipeline BRT GPS

Pipeline de dados automatizado para o desafio [Prefeitura Rio - Civitas Data Engineering](https://github.com/prefeitura-rio/civitas-desafio-data-eng/).

**Autor:** Felipe Santoro Alcantara  
**Contato:** santoro.felipe@gmail.com

---

## 🚀 Como Executar

### 1. Configurar credenciais GCP

**Para avaliadores**: Solicite o arquivo de credenciais ao autor (santoro.felipe@gmail.com) e salve em:
```bash
credentials/civitas-data-eng-8feab1c31a9a.json
```

**Alternativa**: Crie sua própria service account (veja `credentials/README.md`)

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

## � Resultados (BigQuery)

Para visualizar os dados processados, utilize as credenciais incluídas no repositório (`credentials/civitas-data-eng-8feab1c31a9a.json`).

**Projeto GCP:** `civitas-data-eng`

### Tabelas Criadas

| Layer | Dataset | Tabela | Registros | Descrição |
|-------|---------|--------|-----------|-----------|
| 🥉 Bronze | `civitas_bronze` | `brt_gps_external` | 731 | External Table (CSV no GCS) |
| 🥈 Silver | `civitas_silver` | `stg_brt_gps` | 731 | View com transformações |
| 🥇 Gold | `civitas_gold` | `dim_brt_linhas` | 36 | Dimensão de linhas BRT |
| 🥇 Gold | `civitas_gold` | `dim_brt_veiculos` | 731 | Dimensão de veículos |
| 🥇 Gold | `civitas_gold` | `fct_brt_viagens` | 731 | Fato de viagens |
| 🥇 Gold | `civitas_gold` | `agg_metricas_horarias` | 40 | Métricas agregadas |

### Queries de Exemplo

```sql
-- Top 5 linhas com mais veículos
SELECT linha, COUNT(*) as total_veiculos
FROM `civitas-data-eng.civitas_gold.dim_brt_veiculos`
GROUP BY linha
ORDER BY total_veiculos DESC
LIMIT 5;

-- Velocidade média por linha
SELECT linha, ROUND(AVG(velocidade_media_kmh), 2) as vel_media
FROM `civitas-data-eng.civitas_gold.agg_metricas_horarias`
GROUP BY linha
ORDER BY vel_media DESC;
```

---

## 👤 Autor

**Felipe Santoro Alcantara**  
📧 santoro.felipe@gmail.com  
🔗 [GitHub](https://github.com/flpsantoro) | [LinkedIn](https://linkedin.com/in/felipesantoro)

---

**Desafio:** https://github.com/prefeitura-rio/civitas-desafio-data-eng/
