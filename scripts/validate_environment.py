#!/usr/bin/env python3
"""
Script de validação do ambiente antes de executar o pipeline

Verifica:
- Credenciais GCP
- Variáveis de ambiente (.env)
- Recursos GCP (bucket e datasets)
- Conexão com Prefect Server
"""
import os
import sys
from pathlib import Path
from google.cloud import storage, bigquery
from google.auth import default
from prefect import Client
from dotenv import load_dotenv


# Carregar .env
load_dotenv()


def check_env_vars():
    """Valida variáveis de ambiente."""
    print("\n🔍 Verificando variáveis de ambiente...")
    
    required_vars = [
        "GCP_PROJECT_ID",
        "GCS_BUCKET_NAME",
        "BQ_DATASET_RAW",
        "BQ_DATASET_STAGING",
        "BQ_DATASET_GOLD",
        "PREFECT_PROJECT_NAME"
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
            print(f"  ❌ {var}: NOT SET")
        else:
            print(f"  ✅ {var}: {value}")
    
    if missing:
        print(f"\n❌ Variáveis faltando: {', '.join(missing)}")
        return False
    
    return True


def check_gcp_credentials():
    """Valida credenciais GCP."""
    print("\n🔑 Verificando credenciais GCP...")
    
    creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if creds_file:
        if Path(creds_file).exists():
            print(f"  ✅ Service Account: {creds_file}")
        else:
            print(f"  ❌ Arquivo não encontrado: {creds_file}")
            return False
    else:
        print("  ℹ️  Usando gcloud auth (OAuth)")
    
    try:
        credentials, project = default()
        print(f"  ✅ Autenticado no projeto: {project}")
        return True
    except Exception as e:
        print(f"  ❌ Erro na autenticação: {str(e)}")
        return False


def check_gcs_bucket():
    """Valida bucket GCS."""
    print("\n🪣 Verificando bucket GCS...")
    
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        
        if bucket.exists():
            print(f"  ✅ Bucket existe: gs://{bucket_name}")
            return True
        else:
            print(f"  ❌ Bucket não existe: gs://{bucket_name}")
            print(f"  💡 Crie com: gsutil mb -l us-east1 gs://{bucket_name}")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro ao verificar bucket: {str(e)}")
        return False


def check_bq_datasets():
    """Valida datasets BigQuery."""
    print("\n📊 Verificando datasets BigQuery...")
    
    project_id = os.getenv("GCP_PROJECT_ID")
    datasets = [
        os.getenv("BQ_DATASET_RAW"),
        os.getenv("BQ_DATASET_STAGING"),
        os.getenv("BQ_DATASET_GOLD")
    ]
    
    try:
        client = bigquery.Client(project=project_id)
        all_exist = True
        
        for dataset_name in datasets:
            dataset_id = f"{project_id}.{dataset_name}"
            
            try:
                client.get_dataset(dataset_id)
                print(f"  ✅ Dataset existe: {dataset_id}")
            except Exception:
                print(f"  ❌ Dataset não existe: {dataset_id}")
                print(f"  💡 Crie com: bq mk --dataset --location=us-east1 {dataset_id}")
                all_exist = False
        
        return all_exist
        
    except Exception as e:
        print(f"  ❌ Erro ao verificar datasets: {str(e)}")
        return False


def check_prefect_server():
    """Valida conexão com Prefect Server."""
    print("\n🔮 Verificando Prefect Server...")
    
    try:
        client = Client()
        
        # Testar conexão
        response = client.graphql(
            query="""
                query {
                    hello
                }
            """
        )
        
        if response.get("data", {}).get("hello"):
            print("  ✅ Prefect Server acessível")
            
            # Verificar projeto
            project_name = os.getenv("PREFECT_PROJECT_NAME")
            projects = client.graphql(
                query="""
                    query {
                        project {
                            name
                        }
                    }
                """
            )
            
            project_names = [p["name"] for p in projects["data"]["project"]]
            
            if project_name in project_names:
                print(f"  ✅ Projeto existe: {project_name}")
            else:
                print(f"  ⚠️  Projeto não existe: {project_name}")
                print(f"  💡 Será criado automaticamente no register_flows.py")
            
            return True
        else:
            print("  ❌ Resposta inválida do servidor")
            return False
            
    except Exception as e:
        print(f"  ❌ Prefect Server inacessível: {str(e)}")
        print("  💡 Execute: docker-compose up -d")
        return False


def main():
    """Função principal."""
    print("=" * 70)
    print("🧪 VALIDAÇÃO DO AMBIENTE - CIVITAS DATA ENG")
    print("=" * 70)
    
    checks = [
        ("Variáveis de Ambiente", check_env_vars),
        ("Credenciais GCP", check_gcp_credentials),
        ("Bucket GCS", check_gcs_bucket),
        ("Datasets BigQuery", check_bq_datasets),
        ("Prefect Server", check_prefect_server),
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Erro ao executar {name}: {str(e)}")
            results[name] = False
    
    # Resumo
    print("\n" + "=" * 70)
    print("📋 RESUMO DA VALIDAÇÃO")
    print("=" * 70)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ AMBIENTE PRONTO PARA USO!")
        print("=" * 70)
        print("\n💡 Próximo passo:")
        print("   poetry run python register_flows.py")
        sys.exit(0)
    else:
        print("❌ CORRIJA OS PROBLEMAS ACIMA ANTES DE CONTINUAR")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Validação cancelada pelo usuário")
        sys.exit(0)

