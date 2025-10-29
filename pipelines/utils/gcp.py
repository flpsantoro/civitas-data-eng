"""
Utilitrios para interao com Google Cloud Platform
"""
from google.cloud import storage, bigquery
from typing import Optional
import os


def get_gcs_client() -> storage.Client:
    """
    Retorna um cliente do Google Cloud Storage
    """
    return storage.Client()


def get_bq_client() -> bigquery.Client:
    """
    Retorna um cliente do BigQuery
    """
    return bigquery.Client()


def upload_to_gcs(
    bucket_name: str,
    source_file_path: str,
    destination_blob_name: str,
    credentials_path: Optional[str] = None
) -> str:
    """
    Faz upload de arquivo para o Google Cloud Storage
    
    Args:
        bucket_name: Nome do bucket
        source_file_path: Caminho do arquivo local
        destination_blob_name: Nome do arquivo no GCS
        credentials_path: Caminho para o arquivo de credenciais (opcional)
        
    Returns:
        URI do arquivo no GCS
    """
    if credentials_path:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(source_file_path)
    
    return f"gs://{bucket_name}/{destination_blob_name}"
