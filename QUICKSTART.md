# 🚀 Guia de Execução Rápida - Pipeline BRT

## ⚡ Quick Start

### 1. Setup Inicial (Uma Única Vez)

```bash
# 1. Clonar e entrar no repositório
git clone <seu-repo>
cd civitas-data-eng

# 2. Configurar ambiente
cp .env.example .env
# Editar .env com suas credenciais GCP

# 3. Criar ambiente virtual e instalar dependências
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 4. Autenticar no GCP
gcloud auth login
gcloud config set project SEU_PROJECT_ID

# 5. Criar bucket GCS
gsutil mb gs://civitas-brt-data
```

### 2. Subir Prefect Server

```bash
# Terminal 1: Subir infraestrutura
docker-compose up -d

# Verificar se subiu corretamente
docker-compose ps

# Acessar UI: http://localhost:8080
```

### 3. Testar Pipeline

```bash
# Terminal 2: Ativar ambiente
.\venv\Scripts\activate

# Testar API do BRT
python test_brt_api.py

# Criar projeto no Prefect
prefect create project desafio-civitas

# Registrar flow
python register_flows.py
```

### 4. Executar Flow

#### Opção A: Via UI (Recomendado)

1. Abrir http://localhost:8080
2. Ir em "Flows"
3. Selecionar "BRT: Extract and Load GPS Data"
4. Clicar em "Quick Run"
5. Acompanhar execução em "Flow Runs"

#### Opção B: Via CLI

```bash
prefect run flow \
  --name "BRT: Extract and Load GPS Data" \
  --project desafio-civitas
```

#### Opção C: Teste Local (Sem Prefect Server)

```bash
cd pipelines/brt/extract_load
python flows.py
```

## 📊 Verificar Resultados

### Arquivos Locais

```bash
# Ver CSVs gerados
ls -la data/

# Ver conteúdo do CSV
head data/brt_gps_*.csv
```

### Google Cloud Storage

```bash
# Listar arquivos no GCS
gsutil ls gs://civitas-brt-data/bronze/brt_gps/

# Ver conteúdo de um arquivo
gsutil cat gs://civitas-brt-data/bronze/brt_gps/brt_gps_*.csv | head
```

### Logs do Prefect

```bash
# Ver logs do servidor
docker-compose logs -f prefect-server

# Ver logs do agent
docker-compose logs -f prefect-agent
```

## 🔧 Comandos Úteis

### Docker

```bash
# Parar serviços
docker-compose down

# Reiniciar serviços
docker-compose restart

# Ver logs em tempo real
docker-compose logs -f

# Limpar tudo (⚠️ remove dados)
docker-compose down -v
```

### Prefect

```bash
# Listar projetos
prefect get projects

# Listar flows
prefect get flows --project desafio-civitas

# Listar execuções
prefect get flow-runs --project desafio-civitas

# Deletar flow
prefect delete flow --name "BRT: Extract and Load GPS Data"
```

### DBT (Próxima Etapa)

```bash
cd dbt

# Instalar pacotes
dbt deps

# Executar modelos
dbt run

# Executar testes
dbt test

# Gerar documentação
dbt docs generate
dbt docs serve
```

## 🐛 Troubleshooting

### Erro: "Port 8080 already in use"

```bash
# Parar Prefect
docker-compose down

# Verificar o que está usando a porta
netstat -ano | findstr :8080  # Windows
lsof -i :8080  # Linux/Mac

# Matar processo ou mudar porta no docker-compose.yml
```

### Erro: "Connection refused" ao registrar flow

```bash
# Verificar se Prefect Server está rodando
docker-compose ps

# Verificar logs
docker-compose logs prefect-server

# Configurar backend do Prefect
prefect backend server
```

### Erro: "401 Unauthorized" no GCS

```bash
# Re-autenticar
gcloud auth login
gcloud auth application-default login

# Verificar projeto
gcloud config get-value project

# Verificar credenciais
echo $GOOGLE_APPLICATION_CREDENTIALS  # Linux/Mac
echo %GOOGLE_APPLICATION_CREDENTIALS%  # Windows
```

### Erro: "Module not found"

```bash
# Reinstalar dependências
pip install -r requirements.txt

# Verificar ambiente virtual está ativo
which python  # Linux/Mac
where python  # Windows
```

## 📚 Próximos Passos

1. ✅ Pipeline funcionando
2. ⏭️ Implementar modelos DBT (Bronze → Silver → Gold)
3. ⏭️ Configurar tabela externa no BigQuery
4. ⏭️ Criar views transformadas
5. ⏭️ Adicionar testes de qualidade
6. ⏭️ Configurar particionamento

## 🔗 Links Úteis

- UI do Prefect: http://localhost:8080
- Documentação Prefect v1: https://docs-v1.prefect.io/
- Console GCP: https://console.cloud.google.com/
- API BRT: https://dados.mobilidade.rio/gps/brt
