"""
Utilitários para manipulação de datas e timestamps
"""
from datetime import datetime, timezone
from typing import Optional
import pytz


def get_current_timestamp(
    tz_name: str = "America/Sao_Paulo",
    format_str: Optional[str] = None
) -> str:
    """
    Retorna timestamp atual em um timezone específico.
    
    Args:
        tz_name: Nome do timezone (ex: 'America/Sao_Paulo', 'UTC')
        format_str: Formato customizado (opcional)
        
    Returns:
        Timestamp formatado como string
    """
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    
    if format_str:
        return now.strftime(format_str)
    
    return now.isoformat()


def parse_timestamp(
    timestamp_str: str,
    input_format: Optional[str] = None
) -> datetime:
    """
    Converte string de timestamp para objeto datetime.
    
    Args:
        timestamp_str: String com timestamp
        input_format: Formato de entrada (opcional, tenta ISO se não fornecido)
        
    Returns:
        Objeto datetime
    """
    if input_format:
        return datetime.strptime(timestamp_str, input_format)
    
    # Tentar formato ISO
    try:
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        # Tentar outros formatos comuns
        common_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y%m%d_%H%M%S",
            "%d/%m/%Y %H:%M:%S"
        ]
        
        for fmt in common_formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Não foi possível parsear timestamp: {timestamp_str}")


def generate_partition_path(
    base_path: str,
    timestamp: Optional[datetime] = None,
    partition_by: str = "date"
) -> str:
    """
    Gera caminho particionado para armazenamento de dados.
    
    Args:
        base_path: Caminho base
        timestamp: Timestamp para particionamento (usa now() se None)
        partition_by: Tipo de partição ('date', 'hour', 'month')
        
    Returns:
        Caminho particionado (ex: base_path/year=2025/month=10/day=28)
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    if partition_by == "date":
        return f"{base_path}/year={timestamp.year}/month={timestamp.month:02d}/day={timestamp.day:02d}"
    elif partition_by == "hour":
        return f"{base_path}/year={timestamp.year}/month={timestamp.month:02d}/day={timestamp.day:02d}/hour={timestamp.hour:02d}"
    elif partition_by == "month":
        return f"{base_path}/year={timestamp.year}/month={timestamp.month:02d}"
    else:
        return base_path


def get_time_window(
    minutes: int = 10,
    reference_time: Optional[datetime] = None
) -> tuple:
    """
    Retorna janela de tempo (início, fim).
    
    Args:
        minutes: Tamanho da janela em minutos
        reference_time: Tempo de referência (usa now() se None)
        
    Returns:
        Tupla (start_time, end_time)
    """
    if reference_time is None:
        reference_time = datetime.now()
    
    from datetime import timedelta
    start_time = reference_time - timedelta(minutes=minutes)
    end_time = reference_time
    
    return start_time, end_time
