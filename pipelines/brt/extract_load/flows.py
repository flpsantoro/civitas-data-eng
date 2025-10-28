"""
Flow de extração e carga de dados do BRT
"""
from datetime import datetime, timedelta
import os
from typing import Optional

from prefect import Flow, Parameter, task, unmapped
from prefect.storage import Local
from prefect.run_configs import DockerRun
from prefect.utilities.logging import get_logger

from pipelines.brt.extract_load.tasks import (
    fetch_brt_gps_data,
    accumulate_data,
    generate_csv,
    upload_csv_to_gcs,
    cleanup_local_file,
    trigger_dbt_run
)
from pipelines.constants import Constants


logger = get_logger()


# Configuração do Flow
with Flow(
    name="BRT: Extract and Load GPS Data",
    description="Pipeline de captura minuto a minuto de dados GPS do BRT, "
                "geração de CSV (10 minutos) e upload para GCS"
) as brt_extract_load_flow:
    
    # =========================================================================
    # PARÂMETROS DO FLOW
    # =========================================================================
    
    # API Configuration
    api_url = Parameter(
        "api_url",
        default=Constants.BRT_API_URL.value,
        required=False
    )
    
    # GCS Configuration
    bucket_name = Parameter(
        "bucket_name",
        default=os.getenv("GCS_BUCKET_NAME", Constants.GCS_BUCKET_NAME.value),
        required=False
    )
    
    gcs_destination_prefix = Parameter(
        "gcs_destination_prefix",
        default="bronze/brt_gps",
        required=False
    )
    
    # Local Storage
    output_dir = Parameter(
        "output_dir",
        default="./data",
        required=False
    )
    
    # GCP Credentials
    credentials_path = Parameter(
        "credentials_path",
        default=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        required=False
    )
    
    # Pipeline Configuration
    capture_interval_minutes = Parameter(
        "capture_interval_minutes",
        default=Constants.CAPTURE_INTERVAL_MINUTES.value,
        required=False
    )
    
    csv_generation_minutes = Parameter(
        "csv_generation_minutes",
        default=Constants.CSV_GENERATION_MINUTES.value,
        required=False
    )
    
    keep_local_file = Parameter(
        "keep_local_file",
        default=True,
        required=False
    )
    
    # DBT Configuration
    materialize_dbt = Parameter(
        "materialize_dbt",
        default=False,
        required=False
    )
    
    dataset_id = Parameter(
        "dataset_id",
        default=Constants.BQ_DATASET_RAW.value,
        required=False
    )
    
    # =========================================================================
    # FLOW LOGIC
    # =========================================================================
    
    # Task 1: Capturar dados da API
    gps_data = fetch_brt_gps_data(api_url=api_url)
    
    # Task 2: Acumular dados (para captura de 10 minutos)
    # Nota: Em produção, usaria um mecanismo de estado persistente
    # Para simplificação do desafio, vamos gerar CSV a cada execução
    accumulated = accumulate_data(
        current_data=gps_data,
        accumulated_data=None  # Implementar persistência em produção
    )
    
    # Task 3: Gerar arquivo CSV
    csv_path = generate_csv(
        data=accumulated,
        output_dir=output_dir,
        filename_prefix="brt_gps"
    )
    
    # Task 4: Upload para GCS
    gcs_uri = upload_csv_to_gcs(
        csv_filepath=csv_path,
        bucket_name=bucket_name,
        destination_prefix=gcs_destination_prefix,
        credentials_path=credentials_path,
        upstream_tasks=[csv_path]
    )
    
    # Task 5: Cleanup (opcional)
    cleanup = cleanup_local_file(
        filepath=csv_path,
        keep_file=keep_local_file,
        upstream_tasks=[gcs_uri]
    )
    
    # Task 6: Trigger DBT (condicional)
    dbt_result = trigger_dbt_run(
        dataset_id=dataset_id,
        materialize=materialize_dbt,
        upstream_tasks=[gcs_uri]
    )


# =========================================================================
# CONFIGURAÇÃO DE STORAGE E RUN
# =========================================================================

# Storage local (para desenvolvimento)
brt_extract_load_flow.storage = Local(
    path="./pipelines/",
    stored_as_script=True
)

# Run configuration para Docker
brt_extract_load_flow.run_config = DockerRun(
    image="civitas-brt-pipeline:latest",
    labels=["civitas", "brt", "extract-load"]
)


# =========================================================================
# METADATA
# =========================================================================

brt_extract_load_flow.metadata = {
    "project": "CIVITAS",
    "domain": "BRT",
    "pipeline": "extract_load",
    "version": "1.0.0",
    "description": "Pipeline de captura de dados GPS do BRT da API Data.Rio"
}


if __name__ == "__main__":
    # Teste local do flow
    logger.info("🚀 Executando flow BRT Extract and Load localmente...")
    
    # Executar com parâmetros padrão
    state = brt_extract_load_flow.run(
        parameters={
            "api_url": Constants.BRT_API_URL.value,
            "keep_local_file": True,
            "materialize_dbt": False
        }
    )
    
    logger.info(f"📊 Status final: {state}")
    
    if state.is_successful():
        logger.info("✅ Flow executado com sucesso!")
    else:
        logger.error("❌ Flow falhou!")
        logger.error(f"Erro: {state.message}")
