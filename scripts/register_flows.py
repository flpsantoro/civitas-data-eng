"""
Script para registrar flows no Prefect Server

Uso:
    python register_flows.py
"""
import os
import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from prefect import Client
from prefect.utilities.logging import get_logger

from pipelines.brt.extract_load.flows import brt_extract_load_flow
from pipelines.brt.extract_load.schedules import (
    brt_minute_schedule,
    brt_with_dbt_schedule,
    brt_dev_schedule
)


logger = get_logger()


def register_flow(
    flow,
    project_name: str = "desafio-civitas",
    schedule=None,
    labels: list = None
):
    """
    Registra um flow no Prefect Server.
    
    Args:
        flow: Flow do Prefect
        project_name: Nome do projeto no Prefect
        schedule: Schedule do flow (opcional)
        labels: Labels do flow (opcional)
    """
    try:
        # Adicionar schedule se fornecido
        if schedule:
            flow.schedule = schedule
        
        # Adicionar labels se fornecido
        if labels:
            flow.run_config.labels = labels
        
        # Registrar flow
        flow_id = flow.register(project_name=project_name)
        
        logger.info(f"✅ Flow '{flow.name}' registrado com sucesso!")
        logger.info(f"   Flow ID: {flow_id}")
        logger.info(f"   Projeto: {project_name}")
        if schedule:
            logger.info(f"   Schedule: Ativo")
        
        return flow_id
        
    except Exception as e:
        logger.error(f"❌ Erro ao registrar flow '{flow.name}': {str(e)}")
        raise


def create_project_if_not_exists(project_name: str):
    """
    Cria projeto no Prefect se não existir.
    
    Args:
        project_name: Nome do projeto
    """
    try:
        client = Client()
        
        # Verificar se projeto existe
        projects = client.graphql(
            query="""
                query {
                    project {
                        id
                        name
                    }
                }
            """
        )
        
        existing_projects = [p["name"] for p in projects["data"]["project"]]
        
        if project_name not in existing_projects:
            logger.info(f"📁 Criando projeto '{project_name}'...")
            
            result = client.create_project(project_name=project_name)
            logger.info(f"✅ Projeto '{project_name}' criado com sucesso!")
            return result
        else:
            logger.info(f"📁 Projeto '{project_name}' já existe")
            
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível criar projeto: {str(e)}")
        logger.info(f"💡 Crie manualmente: prefect create project {project_name}")


def main():
    """
    Função principal para registro de flows.
    """
    logger.info("=" * 70)
    logger.info("🚀 REGISTRO DE FLOWS NO PREFECT SERVER")
    logger.info("=" * 70)
    
    # Configurações
    project_name = os.getenv("PREFECT_PROJECT_NAME", "desafio-civitas")
    
    # Criar projeto se necessário
    create_project_if_not_exists(project_name)
    
    logger.info("")
    logger.info("📋 Flows disponíveis para registro:")
    logger.info("")
    
    # Registrar flows
    flows_to_register = [
        {
            "flow": brt_extract_load_flow,
            "schedule": None,  # Sem schedule por padrão
            "labels": ["civitas", "brt"],
            "description": "Flow principal (sem schedule)"
        },
        # Descomentar para ativar schedules
        # {
        #     "flow": brt_extract_load_flow,
        #     "schedule": brt_minute_schedule,
        #     "labels": ["civitas", "brt", "scheduled"],
        #     "description": "Flow com schedule minuto a minuto"
        # },
        # {
        #     "flow": brt_extract_load_flow,
        #     "schedule": brt_with_dbt_schedule,
        #     "labels": ["civitas", "brt", "scheduled", "dbt"],
        #     "description": "Flow com schedule 10 minutos + DBT"
        # },
    ]
    
    registered_count = 0
    failed_count = 0
    
    for idx, flow_config in enumerate(flows_to_register, 1):
        logger.info(f"\n{idx}. {flow_config['description']}")
        logger.info("-" * 70)
        
        try:
            register_flow(
                flow=flow_config["flow"],
                project_name=project_name,
                schedule=flow_config.get("schedule"),
                labels=flow_config.get("labels")
            )
            registered_count += 1
        except Exception as e:
            logger.error(f"❌ Falha no registro: {str(e)}")
            failed_count += 1
    
    # Sumário
    logger.info("")
    logger.info("=" * 70)
    logger.info("📊 SUMÁRIO DO REGISTRO")
    logger.info("=" * 70)
    logger.info(f"✅ Flows registrados: {registered_count}")
    logger.info(f"❌ Falhas: {failed_count}")
    logger.info("")
    logger.info(f"🌐 Acesse a UI: http://localhost:8080")
    logger.info(f"📁 Projeto: {project_name}")
    logger.info("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⚠️ Registro cancelado pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Erro fatal: {str(e)}")
        sys.exit(1)
