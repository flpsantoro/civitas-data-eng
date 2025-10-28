# Decisões Técnicas - Versões

## 🐍 Python

**Versão escolhida: Python 3.10**

### Por que NÃO usar Python 3.12?

O desafio técnico especifica explicitamente o uso do **Prefect 1.4.1**, que tem as seguintes restrições de versão:

- ✅ Suporta: Python 3.7, 3.8, 3.9, 3.10
- ❌ **NÃO suporta**: Python 3.11, 3.12, 3.13

**Fonte:** [Prefect 1.4.1 Release Notes](https://github.com/PrefectHQ/prefect/releases/tag/1.4.1)

### Justificativa

1. **Compatibilidade**: Prefect 1.4.1 usa bibliotecas que não foram atualizadas para Python 3.11+
2. **Estabilidade**: Python 3.10 é maduro e estável (lançado em 2021)
3. **Referência**: O repositório [pipelines_rj_civitas](https://github.com/prefeitura-rio/pipelines_rj_civitas/) usa Python 3.10
4. **Requisito do desafio**: O desafio exige Prefect 1.4.1

## 🐘 PostgreSQL

**Versão escolhida: PostgreSQL 16**

### Por que atualizar de 13 para 16?

- ✅ Não há restrição de versão do Postgres no desafio
- ✅ Prefect 1.4.1 é compatível com Postgres 9.6+
- ✅ Postgres 16 é a versão LTS mais recente (lançada em Set/2023)
- ✅ Melhorias de performance e segurança

### Benefícios do Postgres 16

- Melhor performance em queries complexas
- Melhorias no sistema de replicação
- Suporte a mais features SQL modernas
- Patches de segurança mais recentes

## 🔧 Outras Dependências

### DBT

**Versão: 1.5.0**

- Compatível com Python 3.10
- Suporta BigQuery
- Inclui suporte a `dbt_external_tables`

### Google Cloud SDK

**Versões:**
- `google-cloud-storage`: 2.10.0
- `google-cloud-bigquery`: 3.11.4

Versões estáveis e bem testadas com Python 3.10.

## 📋 Resumo das Decisões

| Componente | Versão | Motivo |
|------------|--------|--------|
| Python | **3.10** | Última versão compatível com Prefect 1.4.1 |
| Prefect | **1.4.1** | Requisito obrigatório do desafio |
| PostgreSQL | **16** | Versão mais recente compatível |
| DBT | **1.5.0** | Estável e compatível com Python 3.10 |

## ⚠️ Importante

Caso queira usar **Python 3.12** no futuro, seria necessário:

1. Migrar para **Prefect 2.x** (não atende ao desafio)
2. OU usar Prefect 1.4.1 em container separado (complexidade desnecessária)

**Conclusão**: Manter Python 3.10 é a decisão correta para este desafio.
