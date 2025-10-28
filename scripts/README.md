# Scripts Utilitários

Scripts auxiliares para validação, teste e configuração do pipeline.

## Scripts Disponíveis

### `validate_environment.py`
**Validação completa do ambiente antes de executar o pipeline.**

Verifica:
- ✅ Variáveis de ambiente (.env)
- ✅ Credenciais GCP (service account ou OAuth)
- ✅ Bucket GCS existe
- ✅ Datasets BigQuery existem (brt_raw, brt_staging, brt_gold)
- ✅ Prefect Server está acessível

```bash
poetry run python scripts/validate_environment.py
```

**Use antes de registrar flows!**

---

### `test_brt_api.py`
**Testa conexão e estrutura da API do BRT.**

Verifica:
- Conectividade com a API
- Formato dos dados retornados
- Campos disponíveis
- Tempo de resposta

```bash
poetry run python scripts/test_brt_api.py
```

Útil para:
- Validar acesso à API
- Entender estrutura dos dados
- Debug de problemas de conectividade

---

### `register_flows.py`
**Registra flows do Prefect no servidor.**

Funcionalidades:
- Cria projeto "desafio-civitas" se não existir
- Registra flow "brt-extract-load" com labels "civitas" e "brt"
- Suporta schedules (comentados por padrão)

```bash
poetry run python scripts/register_flows.py
```

**Execute após:**
1. Subir Prefect Server (`docker compose up`)
2. Validar ambiente (`validate_environment.py`)

## Ordem de Execução Recomendada

```bash
# 1. Validar ambiente
poetry run python scripts/validate_environment.py

# 2. Testar API (opcional)
poetry run python scripts/test_brt_api.py

# 3. Subir Prefect
docker compose -f docker/docker-compose.yml up -d

# 4. Registrar flows
poetry run python scripts/register_flows.py
```
