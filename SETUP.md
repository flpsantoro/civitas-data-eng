# Setup Inicial - Desafio CIVITAS

## ✅ Estrutura Criada

### Arquivos de Configuração
- ✅ `requirements.txt` - Dependências Python (Prefect 1.4.1, DBT, GCP)
- ✅ `.gitignore` - Regras para ignorar arquivos sensíveis e temporários
- ✅ `.env.example` - Template de variáveis de ambiente
- ✅ `docker-compose.yml` - Configuração Prefect Server + Agent
- ✅ `Dockerfile` - Container para execução dos flows

### Estrutura de Pastas

```
civitas-data-eng/
├── pipelines/                    # ✅ Código dos pipelines Prefect
│   ├── __init__.py
│   ├── constants.py             # Constantes globais
│   ├── brt/                     # Pipeline BRT
│   │   ├── __init__.py
│   │   └── extract_load/        # Flow de extração e carga
│   │       └── __init__.py
│   └── utils/                   # Utilitários compartilhados
│       ├── __init__.py
│       └── gcp.py              # Helpers para Google Cloud
│
├── dbt/                         # ✅ Projeto DBT
│   ├── dbt_project.yml         # Configuração DBT
│   ├── packages.yml            # dbt_external_tables
│   ├── models/                 # Modelos SQL (Bronze/Silver/Gold)
│   ├── macros/                 # Macros reutilizáveis
│   └── seeds/                  # Dados estáticos
│
├── config/                      # ✅ Configurações
├── data/                        # ✅ Dados locais (CSV)
└── README.md                    # ✅ Documentação completa
```

## 📦 Commits Criados (Conventional Commits)

1. **chore: adicionar dependências do projeto com Prefect 1.4.1** (ceeff40)
   - Prefect 1.4.1, Google Cloud SDK, DBT 1.5.0

2. **chore: atualizar .gitignore com regras do projeto** (3ad40fd)
   - Regras para Prefect, DBT, credenciais GCP

3. **feat: criar estrutura base dos pipelines Prefect** (f8d67ee)
   - constants.py, utils/gcp.py, pipelines/brt/

4. **feat: configurar estrutura inicial do DBT** (f6026fb)
   - dbt_project.yml com arquitetura Medallion
   - packages.yml com dbt_external_tables

5. **feat: adicionar configuração Docker para Prefect Server e Agent** (b271466)
   - docker-compose.yml (Postgres + Prefect Server + Agent)
   - Dockerfile para flows

6. **chore: adicionar template de variáveis de ambiente e estrutura de pastas** (e4a3bde)
   - .env.example com todas as variáveis

7. **docs: atualizar README com documentação completa do projeto** (118972e)
   - Instruções de setup e execução

## 🎯 Próximos Passos

### 1. Implementar Pipeline de Captura (BRT)
- [ ] Criar `tasks.py` com tasks de extração da API
- [ ] Criar `flows.py` com o flow principal
- [ ] Criar `schedules.py` para execução minuto a minuto
- [ ] Implementar lógica de captura e geração de CSV (10 min)

### 2. Implementar Upload para GCS
- [ ] Task para upload de CSV para Google Cloud Storage
- [ ] Configurar autenticação GCP

### 3. Configurar DBT
- [ ] Criar tabela externa (Bronze) com dbt_external_tables
- [ ] Criar modelos de transformação (Silver/Gold)
- [ ] Adicionar schema.yml com documentação detalhada
- [ ] Configurar testes de qualidade de dados
- [ ] Implementar particionamento

### 4. Integrar DBT com Prefect
- [ ] Adicionar task para executar DBT após carga
- [ ] Configurar materialização automática

### 5. Testes e Validação
- [ ] Testar captura da API do BRT
- [ ] Validar geração de CSV
- [ ] Testar upload para GCS
- [ ] Validar criação de tabelas no BigQuery
- [ ] Executar testes de qualidade DBT

## 🚀 Como Começar

```bash
# 1. Configurar ambiente
cp .env.example .env
# Editar .env com suas credenciais

# 2. Instalar dependências
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Subir Prefect Server
docker-compose up -d

# 4. Acessar UI
# http://localhost:8080

# 5. Instalar pacotes DBT
cd dbt
dbt deps
```

## 📝 Padrão Conventional Commits

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `chore:` Tarefas de manutenção
- `refactor:` Refatoração
- `test:` Testes

## 📚 Referências

- [Prefect v1 Docs](https://docs-v1.prefect.io/)
- [DBT Docs](https://docs.getdbt.com/)
- [API BRT](https://www.data.rio/documents/PCRJ::transporte-rodovi%C3%A1rio-api-de-gps-do-brt/about)
- [Repositório Referência](https://github.com/prefeitura-rio/pipelines_rj_civitas/)
