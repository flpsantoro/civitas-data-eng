"""
Script de setup inicial do projeto
"""
import os
import json
from pathlib import Path


def create_service_account_key():
    """Cria arquivo de credenciais de exemplo"""
    credentials_dir = Path("credentials")
    credentials_dir.mkdir(exist_ok=True)
    
    print("\n📝 Configurando credenciais GCP...")
    print("\nOpções:")
    print("1. Usar credenciais do gcloud (recomendado)")
    print("2. Usar arquivo de service account JSON")
    
    choice = input("\nEscolha (1 ou 2): ").strip()
    
    if choice == "1":
        print("\n✅ Usando credenciais do gcloud")
        print("Execute: gcloud auth application-default login")
        return None
    else:
        print("\n📄 Baixe o arquivo JSON de service account do GCP Console:")
        print("   1. Acesse: https://console.cloud.google.com/iam-admin/serviceaccounts")
        print("   2. Crie ou selecione uma service account")
        print("   3. Crie uma chave JSON")
        print("   4. Salve o arquivo na pasta credentials/")
        
        filename = input("\nNome do arquivo baixado (ex: meu-projeto-123456.json): ").strip()
        
        if filename:
            return f"./credentials/{filename}"
        return None


def setup_env_file():
    """Configura arquivo .env"""
    print("\n" + "=" * 70)
    print("🚀 SETUP DO PROJETO CIVITAS")
    print("=" * 70)
    
    # GCP Project
    print("\n📋 Configurações do Google Cloud Platform")
    print("-" * 70)
    
    project_id = input("Project ID do GCP: ").strip()
    bucket_name = input("Nome do bucket GCS (será criado se não existir): ").strip()
    
    # Credenciais
    credentials_path = create_service_account_key()
    
    # Criar .env
    env_content = f"""# Google Cloud Platform
GOOGLE_APPLICATION_CREDENTIALS={credentials_path or 'usar gcloud auth'}
GCP_PROJECT_ID={project_id}
GCS_BUCKET_NAME={bucket_name}

# BigQuery
BQ_DATASET_RAW=brt_raw
BQ_DATASET_STAGING=brt_staging
BQ_DATASET_GOLD=brt_gold

# Prefect
PREFECT_PROJECT_NAME=desafio-civitas

# DBT
DBT_PROFILES_DIR=./dbt
DBT_TARGET=dev
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("\n✅ Arquivo .env criado!")
    
    # Criar dbt/profiles.yml
    setup_dbt_profile(project_id)
    
    # Instruções finais
    print("\n" + "=" * 70)
    print("✅ SETUP CONCLUÍDO!")
    print("=" * 70)
    print("\n📋 Próximos passos:")
    print("\n1. Autenticar no GCP:")
    if not credentials_path:
        print("   gcloud auth application-default login")
    print(f"   gcloud config set project {project_id}")
    print(f"\n2. Criar bucket:")
    print(f"   gsutil mb gs://{bucket_name}")
    print("\n3. Instalar dependências:")
    print("   poetry install")
    print("\n4. Subir Prefect:")
    print("   docker-compose up -d")
    print("\n5. Testar API:")
    print("   poetry run python test_brt_api.py")
    print("\n6. Registrar flow:")
    print("   poetry run python register_flows.py")
    print("=" * 70)


def setup_dbt_profile(project_id):
    """Cria profiles.yml do DBT"""
    dbt_dir = Path("dbt")
    dbt_dir.mkdir(exist_ok=True)
    
    profiles_content = f"""civitas_brt:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: {project_id}
      dataset: brt_raw
      threads: 4
      timeout_seconds: 300
      location: US
      priority: interactive
      
    prod:
      type: bigquery
      method: oauth
      project: {project_id}
      dataset: brt_gold
      threads: 8
      timeout_seconds: 300
      location: US
      priority: interactive
"""
    
    with open("dbt/profiles.yml", "w") as f:
        f.write(profiles_content)
    
    print("✅ DBT profiles.yml criado!")


if __name__ == "__main__":
    try:
        setup_env_file()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelado")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
