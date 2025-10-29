"""
Utilitrios para logging e formatao de mensagens
"""
from datetime import datetime
from typing import Any, Dict
import json


def format_log_message(message: str, emoji: str = "", **kwargs) -> str:
    """
    Formata mensagem de log com timestamp e contexto adicional.
    
    Args:
        message: Mensagem principal
        emoji: Emoji para identificao visual
        **kwargs: Contexto adicional
        
    Returns:
        Mensagem formatada
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    base_message = f"{emoji} [{timestamp}] {message}"
    
    if kwargs:
        context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        return f"{base_message} ({context})"
    
    return base_message


def log_dataframe_info(df, logger, title: str = "DataFrame Info") -> None:
    """
    Loga informaes detalhadas sobre um DataFrame.
    
    Args:
        df: pandas DataFrame
        logger: Logger do Prefect
        title: Ttulo do log
    """
    logger.info(f" {title}")
    logger.info(f"   Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    logger.info(f"   Columns: {', '.join(df.columns.tolist())}")
    logger.info(f"   Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Tipos de dados
    dtypes_summary = df.dtypes.value_counts().to_dict()
    logger.info(f"   Data types: {dtypes_summary}")
    
    # Valores nulos
    null_counts = df.isnull().sum()
    if null_counts.any():
        logger.warning(f"   Null values found:")
        for col, count in null_counts[null_counts > 0].items():
            logger.warning(f"       {col}: {count}")


def create_execution_summary(
    start_time: datetime,
    end_time: datetime,
    records_processed: int,
    output_file: str = None,
    gcs_uri: str = None
) -> Dict[str, Any]:
    """
    Cria sumrio da execuo do pipeline.
    
    Args:
        start_time: Incio da execuo
        end_time: Fim da execuo
        records_processed: Nmero de registros processados
        output_file: Caminho do arquivo gerado
        gcs_uri: URI do arquivo no GCS
        
    Returns:
        Dicionrio com sumrio da execuo
    """
    duration = (end_time - start_time).total_seconds()
    
    summary = {
        "execution": {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "duration_formatted": f"{duration:.2f}s"
        },
        "data": {
            "records_processed": records_processed,
            "records_per_second": records_processed / duration if duration > 0 else 0
        },
        "output": {
            "local_file": output_file,
            "gcs_uri": gcs_uri
        }
    }
    
    return summary


def pretty_print_json(data: Dict, logger) -> None:
    """
    Imprime JSON formatado no log.
    
    Args:
        data: Dicionrio para imprimir
        logger: Logger do Prefect
    """
    try:
        formatted = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        logger.info(f"\n{formatted}")
    except Exception as e:
        logger.warning(f"No foi possvel formatar JSON: {e}")
        logger.info(str(data))
