# Docker Configuration

Arquivos de containerização do projeto.

## Arquivos

### `docker-compose.yml`
Stack completa para desenvolvimento local:
- **postgres**: Banco de dados do Prefect Server
- **prefect-server**: UI e API do Prefect (portas 4200 e 8080)
- **prefect-agent**: Executa os flows com label "civitas"

### `Dockerfile`
Imagem Docker para executar os pipelines:
- Python 3.10
- Poetry para gerenciamento de dependências
- Multi-stage build para otimização

## Como usar

```bash
# Subir stack completa
docker compose -f docker/docker-compose.yml up -d

# Ver logs
docker compose -f docker/docker-compose.yml logs -f

# Parar tudo
docker compose -f docker/docker-compose.yml down

# Rebuild da imagem
docker compose -f docker/docker-compose.yml build --no-cache
```

## Portas

- `4200`: Prefect API
- `8080`: Prefect UI (acesse http://localhost:8080)
- `5432`: PostgreSQL

## Volumes

- `postgres-data`: Dados do PostgreSQL (persiste entre restarts)
- `prefect-data`: Dados do Prefect Server
