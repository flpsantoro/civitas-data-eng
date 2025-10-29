"""
Constantes globais do projeto
"""
from enum import Enum


class Constants(Enum):
    """
    Constantes utilizadas nos pipelines
    """
    # GCP
    GCP_PROJECT_ID = "rj-civitas"
    GCS_BUCKET_NAME = "civitas-brt-data"
    BQ_DATASET_RAW = "brt_raw"
    BQ_DATASET_STAGING = "brt_staging"
    
    # API BRT
    BRT_API_URL = "https://dados.mobilidade.rio/gps/brt"
    
    # Configuraes de execuo
    CAPTURE_INTERVAL_MINUTES = 1
    CSV_GENERATION_MINUTES = 10
    
    # Prefect
    PREFECT_BACKEND = "server"
    PREFECT_PROJECT_NAME = "desafio-civitas"
