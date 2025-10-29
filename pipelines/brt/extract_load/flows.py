"""
Flow de extrao e carga de dados do BRT
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
    trigger_dbt_run,
    cleanup_all_data,
    validate_layer,
    clean_old_csvs,
    create_bronze_external_table,
    create_gold_tables
)
from pipelines.constants import Constants


logger = get_logger()


# Configurao do Flow
with Flow(
    name="BRT: Extract and Load GPS Data"
) as brt_extract_load_flow:
    
    # =========================================================================
    # PARMETROS DO FLOW
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
    keep_local_file = Parameter(
        "keep_local_file",
        default=True,
        required=False
    )
    
    dataset_id = Parameter(
        "dataset_id",
        default=Constants.BQ_DATASET_RAW.value,
        required=False
    )
    
    # =========================================================================
    # FLOW LOGIC - PIPELINE AUTOMATIZADO COM LIMPEZA E VALIDAÇÕES
    # =========================================================================
    
    # Task 0: LIMPEZA COMPLETA - Remove todos CSVs locais e do GCS
    cleanup_all = cleanup_all_data(
        bucket_name=bucket_name,
        local_data_dir=output_dir
    )
    
    # Task 1: Capturar dados da API
    gps_data = fetch_brt_gps_data(
        api_url=api_url,
        upstream_tasks=[cleanup_all]
    )
    
    # Task 2: Acumular dados
    accumulated = accumulate_data(
        current_data=gps_data,
        accumulated_data=None
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
    
    # Task 5: Criar Bronze External Table
    bronze_table = create_bronze_external_table(
        project_id="civitas-data-eng",
        dataset_id="civitas_bronze",
        table_id="brt_gps_external",
        gcs_uri="gs://civitas-brt-data/bronze/brt_gps/*.csv",
        upstream_tasks=[gcs_uri]
    )
    
    # Task 6: VALIDAÇÃO Bronze
    validate_bronze = validate_layer(
        project_id="civitas-data-eng",
        layer_name="Bronze",
        table_id="civitas_bronze.brt_gps_external",
        min_records=1,
        upstream_tasks=[bronze_table]
    )
    
    # Task 7: Trigger DBT para Silver
    dbt_result = trigger_dbt_run(
        dataset_id=dataset_id,
        materialize=True,
        upstream_tasks=[validate_bronze]
    )
    
    # Task 8: VALIDAÇÃO Silver
    validate_silver = validate_layer(
        project_id="civitas-data-eng",
        layer_name="Silver",
        table_id="civitas_silver.stg_brt_gps",
        min_records=1,
        upstream_tasks=[dbt_result]
    )
    
    # Task 9: Criar Gold Tables
    gold_tables = create_gold_tables(
        project_id="civitas-data-eng",
        upstream_tasks=[validate_silver]
    )
    
    # Task 10: VALIDAÇÕES Gold (4 tabelas)
    validate_gold_linhas = validate_layer(
        project_id="civitas-data-eng",
        layer_name="Gold - Linhas",
        table_id="civitas_gold.dim_brt_linhas",
        min_records=1,
        upstream_tasks=[gold_tables]
    )
    
    validate_gold_veiculos = validate_layer(
        project_id="civitas-data-eng",
        layer_name="Gold - Veículos",
        table_id="civitas_gold.dim_brt_veiculos",
        min_records=1,
        upstream_tasks=[gold_tables]
    )
    
    validate_gold_viagens = validate_layer(
        project_id="civitas-data-eng",
        layer_name="Gold - Viagens",
        table_id="civitas_gold.fct_brt_viagens",
        min_records=1,
        upstream_tasks=[gold_tables]
    )
    
    validate_gold_metricas = validate_layer(
        project_id="civitas-data-eng",
        layer_name="Gold - Métricas",
        table_id="civitas_gold.agg_metricas_horarias",
        min_records=1,
        upstream_tasks=[gold_tables]
    )
    
    # Task 11: Cleanup local (após validações)
    cleanup = cleanup_local_file(
        filepath=csv_path,
        keep_file=keep_local_file,
        upstream_tasks=[validate_gold_metricas]
    )


# =========================================================================
# CONFIGURAO DE STORAGE E RUN
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
    logger.info(" Executando flow BRT Extract and Load localmente...")
    
    # Executar com parmetros padro
    state = brt_extract_load_flow.run(
        parameters={
            "api_url": Constants.BRT_API_URL.value,
            "keep_local_file": True
        }
    )
    
    logger.info(f" Status final: {state}")
    
    if state.is_successful():
        logger.info(" Flow executado com sucesso!")
    else:
        logger.error(" Flow falhou!")
        logger.error(f"Erro: {state.message}")
