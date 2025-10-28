FROM python:3.10-slim

# Metadados
LABEL maintainer="Data Engineer Challenge"
LABEL description="Pipeline BRT - CIVITAS"
# Nota: Python 3.10 é a última versão compatível com Prefect 1.4.1

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código da aplicação
COPY pipelines/ ./pipelines/
COPY dbt/ ./dbt/
COPY .env.example .env

# Criar diretórios necessários
RUN mkdir -p data logs credentials

# Expor porta (se necessário)
EXPOSE 8080

# Comando padrão
CMD ["prefect", "agent", "start"]
