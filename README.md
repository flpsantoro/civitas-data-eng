# Desafio Técnico - Data Engineer CIVITAS

Pipeline de ELT para captura, armazenamento e transformação de dados da API de GPS do BRT.

## 📋 Sobre o Projeto

Este projeto implementa uma solução de dados que:

- **Extrai** dados da API de GPS do BRT minuto a minuto
- **Carrega** arquivos CSV (10 minutos de dados) no Google Cloud Storage
- **Transforma** dados seguindo a arquitetura Medallion (Bronze → Silver → Gold) usando DBT
- **Orquestra** todo o processo com Prefect v1.4.1

## 🏗️ Arquitetura

### Stack Tecnológica

- **Python 3.10**: Linguagem principal
- **Prefect 1.4.1**: Orquestração de workflows
- **DBT**: Transformação de dados no BigQuery
- **Google BigQuery**: Data warehouse
- **Google Cloud Storage**: Armazenamento de objetos
- **Docker**: Containerização

### Estrutura do Repositório

```
civitas-data-eng/
├── pipelines/              # Código dos pipelines Prefect
│   ├── brt/               # Pipeline de captura do BRT
│   │   ├── extract_load/  # Flow de extração e carga
│   │   └── ...
│   ├── constants.py       # Constantes globais
│   └── utils/             # Utilitários compartilhados
├── dbt/                   # Projeto DBT (queries)
│   ├── models/            # Modelos de transformação
│   ├── macros/            # Macros reutilizáveis
│   └── dbt_project.yml    # Configuração DBT
├── config/                # Arquivos de configuração
├── data/                  # Dados locais (CSV gerados)
├── .env.example           # Template de variáveis de ambiente
├── docker-compose.yml     # Configuração Prefect Server
├── Dockerfile             # Container para execução dos flows
└── requirements.txt       # Dependências Python
```

## 🚀 Setup do Ambiente

### Pré-requisitos

- Python 3.10
- Docker e Docker Compose
- Google Cloud SDK (gcloud CLI)
- Conta no Google Cloud Platform

### 1. Clonar o Repositório

```bash
git clone <seu-repositorio>
cd civitas-data-eng
```

### 2. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

### 3. Instalar Dependências

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configurar Google Cloud

```bash
# Autenticar
gcloud auth login

# Definir projeto
gcloud config set project SEU_PROJECT_ID

# Criar bucket (se necessário)
gsutil mb gs://SEU_BUCKET_NAME
```

## 🏃 Como Executar

### Iniciar Prefect Server

Em um terminal:

```bash
# Subir Prefect Server e Agent com Docker
docker-compose up -d

# Acessar UI
# http://localhost:8080
```

### Registrar e Executar Flow

Em outro terminal:

```bash
# Ativar ambiente virtual
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Criar projeto (primeira vez)
prefect create project desafio-civitas

# Registrar flow
prefect register --project desafio-civitas -m pipelines.brt.extract_load.flows

# Executar flow via UI ou CLI
prefect run flow --name "BRT: Extract and Load"
```

### Executar Transformações DBT

```bash
cd dbt

# Executar todos os modelos
dbt run

# Executar testes
dbt test

# Gerar documentação
dbt docs generate
dbt docs serve
```

## 📊 Arquitetura Medallion

- **Bronze (Raw)**: Dados brutos da API salvos no GCS e carregados como tabela externa no BigQuery
- **Silver (Staging)**: Dados limpos e padronizados
- **Gold (Marts)**: Dados agregados e prontos para análise

## 🧪 Testes

```bash
# Testes de qualidade de dados no DBT
cd dbt
dbt test

# Testes específicos
dbt test --select brt_staging
```

## 📝 Conventional Commits

Este projeto segue o padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/):

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `chore:` Tarefas de manutenção
- `refactor:` Refatoração de código
- `test:` Adição/modificação de testes

## 📚 Referências

- [Documentação Prefect v1](https://docs-v1.prefect.io/)
- [Documentação DBT](https://docs.getdbt.com/)
- [API do BRT](https://www.data.rio/documents/PCRJ::transporte-rodovi%C3%A1rio-api-de-gps-do-brt/about)
- [Pipelines rj-civitas](https://github.com/prefeitura-rio/pipelines_rj_civitas/)