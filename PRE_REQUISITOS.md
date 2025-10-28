# Pré-requisitos - Instalação

Antes de criar recursos no GCP, você precisa instalar ferramentas essenciais.

## ✅ Já Instalados

- ✅ **Poetry** (2.2.1) - Gerenciador de dependências Python
- ✅ **Python** (3.12) - Compatível com o projeto
- ✅ **Dependências** - Instaladas via `poetry install`

## 🔧 Instalação Necessária

### 1. Google Cloud SDK

**Download:**
https://cloud.google.com/sdk/docs/install

**Instalação Windows:**
1. Baixe o instalador: https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe
2. Execute o instalador
3. Marque "Run 'gcloud init'" no final
4. Reinicie o terminal após instalação

**Verificar:**
```bash
gcloud --version
```

### 2. Docker Desktop (para Prefect local)

**Download:**
https://www.docker.com/products/docker-desktop

**Instalação Windows:**
1. Baixe Docker Desktop
2. Execute o instalador
3. Reinicie o computador se solicitado
4. Abra Docker Desktop e aguarde inicializar

**Verificar:**
```bash
docker --version
docker compose version
```

## 🎯 Próximos Passos Após Instalação

Depois de instalar o Google Cloud SDK:

```bash
# 1. Autenticar com sua conta Google
gcloud auth login

# 2. Autenticar application default (para aplicações)
gcloud auth application-default login

# 3. Configurar projeto
gcloud config set project civitas-data-eng

# 4. Criar recursos GCP
# Ver: PROXIMOS_PASSOS.md > "1. Criar Recursos no GCP"
```

## 📦 Resumo de Comandos

```bash
# Verificar tudo está OK
poetry --version          # Deve mostrar 2.2.1
python --version          # Deve mostrar 3.12.x
gcloud --version          # Deve mostrar SDK instalado
docker --version          # Deve mostrar Docker instalado

# Testar ambiente
poetry run python scripts/test_brt_api.py
```
