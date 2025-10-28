"""
Tasks para extração e carga de dados do BRT
"""
from datetime import datetime
from typing import Dict, List, Optional
import os
import json

import requests
import pandas as pd
from prefect import task
from prefect.utilities.logging import get_logger

from pipelines.utils.gcp import upload_to_gcs


logger = get_logger()


@task(
    name="Fetch BRT GPS Data",
    max_retries=3,
    retry_delay=pd.Timedelta(seconds=10),
    tags=["extraction", "api"]
)
def fetch_brt_gps_data(api_url: str) -> List[Dict]:
    """
    Faz requisição à API do BRT e retorna os dados de GPS dos veículos.
    
    Args:
        api_url: URL da API do BRT
        
    Returns:
        Lista de dicionários com dados de GPS dos veículos
        
    Raises:
        requests.RequestException: Erro na requisição HTTP
    """
    logger.info(f"Iniciando captura de dados da API: {api_url}")
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Adicionar timestamp da captura
        timestamp_captura = datetime.now().isoformat()
        
        # Verificar se retornou objeto com chave "veiculos"
        if isinstance(data, dict) and 'veiculos' in data:
            veiculos = data['veiculos']
            for record in veiculos:
                record['timestamp_captura'] = timestamp_captura
            logger.info(f"✅ Capturados {len(veiculos)} registros de veículos")
            return veiculos
        elif isinstance(data, list):
            for record in data:
                record['timestamp_captura'] = timestamp_captura
            logger.info(f"✅ Capturados {len(data)} registros de veículos")
            return data
        else:
            logger.warning(f"⚠️ Formato inesperado da API. Tipo: {type(data)}")
            return []
            
    except requests.RequestException as e:
        logger.error(f"❌ Erro ao buscar dados da API: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"❌ Erro ao decodificar JSON: {str(e)}")
        raise


@task(
    name="Accumulate Data",
    tags=["processing"]
)
def accumulate_data(
    current_data: List[Dict],
    accumulated_data: Optional[List[Dict]] = None
) -> List[Dict]:
    """
    Acumula dados capturados em uma lista.
    
    Args:
        current_data: Dados da captura atual
        accumulated_data: Dados acumulados anteriormente
        
    Returns:
        Lista com dados acumulados
    """
    if accumulated_data is None:
        accumulated_data = []
    
    accumulated_data.extend(current_data)
    
    logger.info(f"📊 Total de registros acumulados: {len(accumulated_data)}")
    
    return accumulated_data


@task(
    name="Generate CSV",
    tags=["processing", "storage"]
)
def generate_csv(
    data: List[Dict],
    output_dir: str = "./data",
    filename_prefix: str = "brt_gps"
) -> str:
    """
    Gera arquivo CSV a partir dos dados capturados.
    
    Args:
        data: Lista de dicionários com dados dos veículos
        output_dir: Diretório de saída
        filename_prefix: Prefixo do nome do arquivo
        
    Returns:
        Caminho completo do arquivo CSV gerado
    """
    if not data:
        logger.warning("⚠️ Nenhum dado para gerar CSV")
        return None
    
    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Gerar nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Converter para DataFrame e salvar
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, encoding='utf-8')
    
    logger.info(f"✅ CSV gerado: {filepath}")
    logger.info(f"📊 Linhas: {len(df)} | Colunas: {len(df.columns)}")
    logger.info(f"📋 Colunas: {', '.join(df.columns.tolist())}")
    
    return filepath


@task(
    name="Upload to GCS",
    max_retries=3,
    retry_delay=pd.Timedelta(seconds=15),
    tags=["storage", "gcp"]
)
def upload_csv_to_gcs(
    csv_filepath: str,
    bucket_name: str,
    destination_prefix: str = "bronze/brt_gps",
    credentials_path: Optional[str] = None
) -> str:
    """
    Faz upload do arquivo CSV para o Google Cloud Storage.
    
    Args:
        csv_filepath: Caminho do arquivo CSV local
        bucket_name: Nome do bucket GCS
        destination_prefix: Prefixo do caminho no GCS
        credentials_path: Caminho para credenciais GCP
        
    Returns:
        URI do arquivo no GCS (gs://bucket/path/file.csv)
    """
    if not csv_filepath or not os.path.exists(csv_filepath):
        logger.error(f"❌ Arquivo não encontrado: {csv_filepath}")
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_filepath}")
    
    # Gerar caminho de destino no GCS
    filename = os.path.basename(csv_filepath)
    destination_blob_name = f"{destination_prefix}/{filename}"
    
    logger.info(f"📤 Iniciando upload para GCS: gs://{bucket_name}/{destination_blob_name}")
    
    try:
        gcs_uri = upload_to_gcs(
            bucket_name=bucket_name,
            source_file_path=csv_filepath,
            destination_blob_name=destination_blob_name,
            credentials_path=credentials_path
        )
        
        logger.info(f"✅ Upload concluído: {gcs_uri}")
        return gcs_uri
        
    except Exception as e:
        logger.error(f"❌ Erro no upload para GCS: {str(e)}")
        raise


@task(
    name="Cleanup Local Files",
    tags=["cleanup"]
)
def cleanup_local_file(filepath: str, keep_file: bool = False) -> None:
    """
    Remove arquivo local após upload bem-sucedido.
    
    Args:
        filepath: Caminho do arquivo a ser removido
        keep_file: Se True, mantém o arquivo local
    """
    if keep_file:
        logger.info(f"🗂️ Mantendo arquivo local: {filepath}")
        return
    
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"🗑️ Arquivo local removido: {filepath}")
        else:
            logger.warning(f"⚠️ Arquivo não encontrado para remoção: {filepath}")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao remover arquivo: {str(e)}")


@task(
    name="Trigger DBT Run",
    tags=["transformation", "dbt"]
)
def trigger_dbt_run(
    dataset_id: str,
    materialize: bool = True
) -> Dict[str, str]:
    """
    Placeholder para trigger de execução do DBT.
    Será implementado quando os modelos DBT estiverem prontos.
    
    Args:
        dataset_id: ID do dataset no BigQuery
        materialize: Se deve materializar os modelos
        
    Returns:
        Dicionário com status da execução
    """
    logger.info(f"🔄 DBT Run será implementado na próxima etapa")
    logger.info(f"Dataset: {dataset_id}, Materialize: {materialize}")
    
    return {
        "status": "pending",
        "message": "DBT integration to be implemented",
        "dataset_id": dataset_id
    }
