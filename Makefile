.PHONY: help build up down restart logs shell test validate setup-gcp register clean

# Variáveis
COMPOSE=docker compose -f docker/docker-compose.yml
CLI_SERVICE=cli

help: ## Mostra esta ajuda
	@echo "Comandos disponíveis:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build das imagens Docker
	$(COMPOSE) build

up: ## Sobe todos os serviços (Prefect Server + Agent + PostgreSQL)
	$(COMPOSE) up -d postgres prefect-server prefect-agent
	@echo ""
	@echo "✅ Serviços iniciados!"
	@echo "   Prefect UI: http://localhost:8080"
	@echo "   Prefect API: http://localhost:4200"
	@echo ""
	@echo "📋 Próximos passos:"
	@echo "   make setup-gcp    # Criar recursos no GCP"
	@echo "   make validate     # Validar ambiente"
	@echo "   make register     # Registrar flows"

down: ## Para todos os serviços
	$(COMPOSE) down

restart: ## Reinicia todos os serviços
	$(COMPOSE) restart

logs: ## Mostra logs de todos os serviços
	$(COMPOSE) logs -f

shell: ## Abre shell no container CLI com todas as ferramentas
	$(COMPOSE) run --rm $(CLI_SERVICE) /bin/bash

# Scripts utilitários
test: ## Testa API do BRT
	$(COMPOSE) run --rm $(CLI_SERVICE) scripts/test_brt_api.py

validate: ## Valida ambiente completo (credenciais, GCP, etc)
	$(COMPOSE) run --rm $(CLI_SERVICE) scripts/validate_environment.py

register: ## Registra flows no Prefect Server
	$(COMPOSE) run --rm $(CLI_SERVICE) scripts/register_flows.py

# GCP
setup-gcp: ## Cria recursos no GCP (bucket + datasets)
	@echo "🔧 Criando recursos no GCP..."
	@echo ""
	$(COMPOSE) run --rm $(CLI_SERVICE) /bin/bash -c " \
		set -e; \
		echo '📦 Verificando projeto...'; \
		gcloud config get-value project || echo 'Projeto não configurado'; \
		echo ''; \
		echo '🪣 Criando bucket GCS...'; \
		gsutil mb -l us-east1 gs://civitas-brt-data || echo 'Bucket já existe'; \
		echo ''; \
		echo '📊 Criando datasets BigQuery...'; \
		bq mk --dataset --location=us-east1 civitas-data-eng:brt_raw || echo 'Dataset brt_raw já existe'; \
		bq mk --dataset --location=us-east1 civitas-data-eng:brt_staging || echo 'Dataset brt_staging já existe'; \
		bq mk --dataset --location=us-east1 civitas-data-eng:brt_gold || echo 'Dataset brt_gold já existe'; \
		echo ''; \
		echo '✅ Recursos GCP criados/verificados!'; \
	"

gcloud: ## Executa comando gcloud (uso: make gcloud ARGS="auth list")
	$(COMPOSE) run --rm $(CLI_SERVICE) gcloud $(ARGS)

gsutil: ## Executa comando gsutil (uso: make gsutil ARGS="ls")
	$(COMPOSE) run --rm $(CLI_SERVICE) gsutil $(ARGS)

bq: ## Executa comando bq (uso: make bq ARGS="ls")
	$(COMPOSE) run --rm $(CLI_SERVICE) bq $(ARGS)

dbt: ## Executa comando dbt (uso: make dbt ARGS="debug")
	$(COMPOSE) run --rm $(CLI_SERVICE) dbt --project-dir queries $(ARGS)

# Limpeza
clean: ## Remove containers, volumes e imagens
	$(COMPOSE) down -v --remove-orphans
	docker rmi civitas-data-eng-cli civitas-data-eng-prefect-agent 2>/dev/null || true

# Setup completo
setup: build up setup-gcp validate register ## Setup completo do ambiente
	@echo ""
	@echo "🎉 Setup completo!"
	@echo "   Acesse: http://localhost:8080"
