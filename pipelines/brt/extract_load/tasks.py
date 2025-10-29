"""
Tasks para extrao e carga de dados do BRT
"""
from datetime import datetime, timedelta
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
    Faz requisio  API do BRT e retorna os dados de GPS dos veculos.
    
    Args:
        api_url: URL da API do BRT
        
    Returns:
        Lista de dicionrios com dados de GPS dos veculos
        
    Raises:
        requests.RequestException: Erro na requisio HTTP
    """
    logger.info(f"Iniciando captura de dados da API: {api_url}")
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        timestamp_captura = datetime.now().isoformat()
        
        if isinstance(data, dict) and 'veiculos' in data:
            veiculos = data['veiculos']
            for record in veiculos:
                record['timestamp_captura'] = timestamp_captura
            logger.info(f"Capturados {len(veiculos)} registros de veculos")
            return veiculos
        elif isinstance(data, list):
            for record in data:
                record['timestamp_captura'] = timestamp_captura
            logger.info(f"Capturados {len(data)} registros de veculos")
            return data
        else:
            logger.warning(f"Formato inesperado da API. Tipo: {type(data)}")
            return []
            
    except requests.RequestException as e:
        logger.error(f"Erro ao buscar dados da API: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {str(e)}")
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
    
    logger.info(f" Total de registros acumulados: {len(accumulated_data)}")
    
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
        data: Lista de dicionrios com dados dos veculos
        output_dir: Diretrio de sada
        filename_prefix: Prefixo do nome do arquivo
        
    Returns:
        Caminho completo do arquivo CSV gerado
    """
    if not data:
        logger.warning(" Nenhum dado para gerar CSV")
        return None
    
    # Criar diretrio se no existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Gerar nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Converter para DataFrame
    df = pd.DataFrame(data)
    
    # Converter campos de timestamp Unix (milissegundos) para ISO 8601
    timestamp_columns = ['dataHora']
    for col in timestamp_columns:
        if col in df.columns:
            # Converter de milissegundos Unix para datetime e depois para ISO 8601
            df[col] = pd.to_datetime(df[col], unit='ms', errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Garantir que timestamp_captura tambm est em formato ISO
    if 'timestamp_captura' in df.columns:
        # Se j  string ISO, manter; se no, converter
        df['timestamp_captura'] = pd.to_datetime(df['timestamp_captura'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Salvar CSV
    df.to_csv(filepath, index=False, encoding='utf-8')
    
    logger.info(f" CSV gerado: {filepath}")
    logger.info(f" Linhas: {len(df)} | Colunas: {len(df.columns)}")
    logger.info(f" Colunas: {', '.join(df.columns.tolist())}")
    
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
        logger.error(f" Arquivo no encontrado: {csv_filepath}")
        raise FileNotFoundError(f"Arquivo no encontrado: {csv_filepath}")
    
    # Gerar caminho de destino no GCS
    filename = os.path.basename(csv_filepath)
    destination_blob_name = f"{destination_prefix}/{filename}"
    
    logger.info(f" Iniciando upload para GCS: gs://{bucket_name}/{destination_blob_name}")
    
    try:
        gcs_uri = upload_to_gcs(
            bucket_name=bucket_name,
            source_file_path=csv_filepath,
            destination_blob_name=destination_blob_name,
            credentials_path=credentials_path
        )
        
        logger.info(f" Upload concludo: {gcs_uri}")
        return gcs_uri
        
    except Exception as e:
        logger.error(f" Erro no upload para GCS: {str(e)}")
        raise


@task(
    name="Cleanup Local Files",
    tags=["cleanup"]
)
def cleanup_local_file(filepath: str, keep_file: bool = False) -> None:
    """
    Remove arquivo local aps upload bem-sucedido.
    
    Args:
        filepath: Caminho do arquivo a ser removido
        keep_file: Se True, mantm o arquivo local
    """
    if keep_file:
        logger.info(f" Mantendo arquivo local: {filepath}")
        return
    
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f" Arquivo local removido: {filepath}")
        else:
            logger.warning(f" Arquivo no encontrado para remoo: {filepath}")
    except Exception as e:
        logger.warning(f" Erro ao remover arquivo: {str(e)}")


@task(
    name="Trigger DBT Run",
    tags=["transformation", "dbt"],
    max_retries=2,
    retry_delay=timedelta(seconds=30)
)
def trigger_dbt_run(
    dataset_id: str,
    materialize: bool = True
) -> Dict[str, str]:
    """
    Executa transformaes DBT aps upload de dados para GCS.
    
    Args:
        dataset_id: ID do dataset no BigQuery
        materialize: Se deve materializar os modelos (sempre True para produo)
        
    Returns:
        Dicionrio com status da execuo DBT
    """
    import subprocess
    import json
    
    if not materialize:
        logger.info(" DBT materializao desabilitada (materialize=False)")
        return {
            "status": "skipped",
            "message": "DBT run skipped (materialize=False)",
            "dataset_id": dataset_id
        }
    
    logger.info(f" Iniciando DBT transformations para dataset: {dataset_id}")
    
    try:
        # Diretório DBT
        dbt_dir = "/app/dbt"
        
        # Primeiro: dbt deps (instalar dependências)
        logger.info(" Instalando dependências DBT...")
        deps_result = subprocess.run(
            ["dbt", "deps", "--profiles-dir", dbt_dir, "--project-dir", dbt_dir],
            cwd=dbt_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if deps_result.returncode != 0:
            logger.warning(f" dbt deps warning (ignorando): {deps_result.stderr}")
        else:
            logger.info(" Dependências DBT instaladas")
        
        # Comando DBT run (todas as camadas: bronze  silver  gold)
        dbt_command = [
            "dbt", "run",
            "--profiles-dir", dbt_dir,
            "--project-dir", dbt_dir
        ]
        
        logger.info(f" Executando: {' '.join(dbt_command)}")
        
        # Executar DBT run
        result = subprocess.run(
            dbt_command,
            cwd=dbt_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        # Log output
        if result.stdout:
            logger.info(f" DBT stdout:\n{result.stdout}")
        
        if result.stderr:
            logger.warning(f" DBT stderr:\n{result.stderr}")
        
        # Verificar sucesso
        if result.returncode == 0:
            logger.info(" DBT transformations executadas com sucesso!")
            
            # Extrair mtricas do output
            models_executed = result.stdout.count(" OK created")
            models_failed = result.stdout.count(" ERROR")
            
            return {
                "status": "success",
                "message": f"DBT run completed: {models_executed} models OK, {models_failed} errors",
                "dataset_id": dataset_id,
                "models_executed": models_executed,
                "models_failed": models_failed,
                "stdout": result.stdout[-500:] if len(result.stdout) > 500 else result.stdout  # ltimas 500 chars
            }
        else:
            error_msg = f"DBT run failed with return code {result.returncode}"
            logger.error(f" {error_msg}")
            logger.error(f"stderr: {result.stderr}")
            
            raise Exception(f"{error_msg}\n{result.stderr}")
    
    except subprocess.TimeoutExpired:
        error_msg = "DBT run timeout (exceeded 5 minutes)"
        logger.error(f" {error_msg}")
        raise Exception(error_msg)
    
    except Exception as e:
        logger.error(f" Erro ao executar DBT: {str(e)}")
        raise


@task(
    name="Cleanup All Data",
    max_retries=1,
    retry_delay=pd.Timedelta(seconds=5),
    tags=["cleanup", "maintenance"]
)
def cleanup_all_data(bucket_name: str, local_data_dir: str = "./data") -> Dict:
    """
    Remove TODOS os CSVs locais e arquivos do GCS antes de executar o pipeline.
    
    Args:
        bucket_name: Nome do bucket GCS
        local_data_dir: Diretório local com CSVs
        
    Returns:
        Dict com estatísticas da limpeza
    """
    from google.cloud import storage
    import glob
    
    logger.info("🧹 LIMPEZA COMPLETA - Removendo todos os dados antigos...")
    
    stats = {
        "local_files_deleted": 0,
        "gcs_files_deleted": 0,
        "errors": []
    }
    
    # 1. Limpar CSVs locais
    try:
        csv_files = glob.glob(os.path.join(local_data_dir, "brt_gps_*.csv"))
        for csv_file in csv_files:
            try:
                os.remove(csv_file)
                logger.info(f"   🗑️  Local: {os.path.basename(csv_file)}")
                stats["local_files_deleted"] += 1
            except Exception as e:
                logger.warning(f"   ⚠️  Erro ao remover {csv_file}: {e}")
                stats["errors"].append(str(e))
        
        if stats["local_files_deleted"] > 0:
            logger.info(f"   ✅ {stats['local_files_deleted']} arquivo(s) local(is) removido(s)")
        else:
            logger.info("   ℹ️  Nenhum CSV local encontrado")
    except Exception as e:
        logger.warning(f"   ⚠️  Erro na limpeza local: {e}")
        stats["errors"].append(f"Local cleanup: {e}")
    
    # 2. Limpar TODOS os arquivos do GCS
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        
        # Listar TODOS os arquivos no bucket
        blobs = list(bucket.list_blobs(prefix='bronze/brt_gps/'))
        
        if len(blobs) == 0:
            logger.info("   ℹ️  Nenhum arquivo GCS encontrado")
        else:
            for blob in blobs:
                try:
                    blob.delete()
                    logger.info(f"   🗑️  GCS: {blob.name}")
                    stats["gcs_files_deleted"] += 1
                except Exception as e:
                    logger.warning(f"   ⚠️  Erro ao remover {blob.name}: {e}")
                    stats["errors"].append(str(e))
            
            logger.info(f"   ✅ {stats['gcs_files_deleted']} arquivo(s) GCS removido(s)")
    
    except Exception as e:
        logger.warning(f"   ⚠️  Erro na limpeza GCS: {e}")
        stats["errors"].append(f"GCS cleanup: {e}")
    
    logger.info(f"🧹 LIMPEZA COMPLETA: {stats['local_files_deleted']} local + {stats['gcs_files_deleted']} GCS")
    
    return stats


@task(
    name="Validate Pipeline Layer",
    max_retries=1,
    retry_delay=pd.Timedelta(seconds=5),
    tags=["validation", "testing"]
)
def validate_layer(
    project_id: str,
    layer_name: str,
    table_id: str,
    min_records: int = 1
) -> Dict:
    """
    Valida se uma camada do pipeline foi criada corretamente.
    
    Args:
        project_id: ID do projeto GCP
        layer_name: Nome da camada (Bronze/Silver/Gold)
        table_id: ID completo da tabela (dataset.table)
        min_records: Número mínimo de registros esperado
        
    Returns:
        Dict com resultado da validação
    """
    from google.cloud import bigquery
    
    logger.info(f"✅ Validando {layer_name}: {table_id}")
    
    try:
        client = bigquery.Client(project=project_id)
        
        # Query simples de contagem
        query = f"SELECT COUNT(*) as total FROM `{project_id}.{table_id}`"
        result = list(client.query(query).result())[0]
        
        total_records = result.total
        
        if total_records >= min_records:
            logger.info(f"   ✅ {layer_name}: {total_records} registros (mínimo: {min_records})")
            return {
                "layer": layer_name,
                "table": table_id,
                "status": "PASS",
                "records": total_records,
                "expected_min": min_records
            }
        else:
            logger.error(f"   ❌ {layer_name}: {total_records} registros (esperado: >= {min_records})")
            return {
                "layer": layer_name,
                "table": table_id,
                "status": "FAIL",
                "records": total_records,
                "expected_min": min_records
            }
    
    except Exception as e:
        logger.error(f"   ❌ {layer_name}: Erro - {str(e)}")
        return {
            "layer": layer_name,
            "table": table_id,
            "status": "ERROR",
            "error": str(e)
        }


@task(
    name="Clean Old CSVs from GCS",
    max_retries=2,
    retry_delay=pd.Timedelta(seconds=5),
    tags=["maintenance", "gcs"]
)
def clean_old_csvs(bucket_name: str, prefix: str = 'bronze/brt_gps/') -> Dict:
    """
    Remove CSVs antigos do GCS, mantendo apenas o mais recente.
    
    Args:
        bucket_name: Nome do bucket GCS
        prefix: Prefixo do caminho dos CSVs
        
    Returns:
        Dict com número de arquivos deletados e arquivo mantido
    """
    from google.cloud import storage
    
    logger.info(f"🗑️  Limpando CSVs antigos em gs://{bucket_name}/{prefix}")
    
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blobs = list(bucket.list_blobs(prefix=prefix))
        
        if len(blobs) == 0:
            logger.warning("   Nenhum arquivo encontrado")
            return {"deleted": 0, "kept": None}
        
        if len(blobs) == 1:
            logger.info(f"   ✓ Apenas 1 arquivo, nada a deletar: {blobs[0].name}")
            return {"deleted": 0, "kept": blobs[0].name}
        
        # Ordenar por data de criação (mais recente primeiro)
        blobs_sorted = sorted(blobs, key=lambda b: b.updated, reverse=True)
        
        # Deletar todos exceto o mais recente
        deleted_count = 0
        for blob in blobs_sorted[1:]:
            logger.info(f"   Deletando: {blob.name}")
            blob.delete()
            deleted_count += 1
        
        logger.info(f"   ✓ {deleted_count} arquivo(s) deletado(s)")
        logger.info(f"   ✓ Mantido: {blobs_sorted[0].name}")
        
        return {
            "deleted": deleted_count,
            "kept": blobs_sorted[0].name
        }
    
    except Exception as e:
        logger.error(f"   ❌ Erro ao limpar CSVs: {str(e)}")
        raise


@task(
    name="Create Bronze External Table",
    max_retries=2,
    retry_delay=pd.Timedelta(seconds=5),
    tags=["bigquery", "bronze"]
)
def create_bronze_external_table(
    project_id: str,
    dataset_id: str,
    table_id: str,
    gcs_uri: str
) -> Dict:
    """
    Cria tabela externa no BigQuery apontando para CSVs no GCS.
    
    Args:
        project_id: ID do projeto GCP
        dataset_id: Nome do dataset (ex: civitas_bronze)
        table_id: Nome da tabela (ex: brt_gps_external)
        gcs_uri: URI do GCS (ex: gs://bucket/path/*.csv)
        
    Returns:
        Dict com informações da tabela criada
    """
    from google.cloud import bigquery
    
    logger.info(f"📊 Criando External Table: {project_id}.{dataset_id}.{table_id}")
    
    try:
        client = bigquery.Client(project=project_id)
        
        # Criar dataset se não existir
        dataset_ref = f"{project_id}.{dataset_id}"
        try:
            client.get_dataset(dataset_ref)
            logger.info(f"   ✓ Dataset {dataset_id} já existe")
        except:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "us-east1"
            client.create_dataset(dataset)
            logger.info(f"   ✓ Dataset {dataset_id} criado")
        
        # Configurar external table
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        external_config = bigquery.ExternalConfig("CSV")
        external_config.source_uris = [gcs_uri]
        external_config.options.skip_leading_rows = 1
        external_config.options.allow_jagged_rows = True
        external_config.options.allow_quoted_newlines = True
        
        # Schema
        external_config.schema = [
            bigquery.SchemaField("codigo", "STRING"),
            bigquery.SchemaField("placa", "STRING"),
            bigquery.SchemaField("linha", "STRING"),
            bigquery.SchemaField("latitude", "FLOAT"),
            bigquery.SchemaField("longitude", "FLOAT"),
            bigquery.SchemaField("dataHora", "STRING"),
            bigquery.SchemaField("velocidade", "FLOAT"),
            bigquery.SchemaField("id_migracao_trajeto", "STRING"),
            bigquery.SchemaField("sentido", "STRING"),
            bigquery.SchemaField("trajeto", "STRING"),
            bigquery.SchemaField("hodometro", "FLOAT"),
            bigquery.SchemaField("direcao", "STRING"),
            bigquery.SchemaField("ignicao", "STRING"),
            bigquery.SchemaField("capacidadePeVeiculo", "INTEGER"),
            bigquery.SchemaField("capacidadeSentadoVeiculo", "INTEGER"),
            bigquery.SchemaField("timestamp_captura", "STRING"),
        ]
        
        # Criar tabela
        table = bigquery.Table(table_ref)
        table.external_data_configuration = external_config
        
        table = client.create_table(table, exists_ok=True)
        logger.info(f"   ✓ Tabela externa criada: {table_ref}")
        logger.info(f"   ✓ URI: {gcs_uri}")
        
        # Testar query
        query = f"SELECT COUNT(*) as n FROM `{table_ref}`"
        result = list(client.query(query).result())[0]
        logger.info(f"   ✓ Teste OK: {result.n} registros")
        
        return {
            "table": table_ref,
            "type": "EXTERNAL",
            "uri": gcs_uri,
            "records": result.n
        }
    
    except Exception as e:
        logger.error(f"   ❌ Erro ao criar external table: {str(e)}")
        raise


@task(
    name="Create Gold Tables",
    max_retries=2,
    retry_delay=pd.Timedelta(seconds=10),
    tags=["bigquery", "gold"]
)
def create_gold_tables(project_id: str) -> Dict:
    """
    Cria 4 tabelas Gold (2 dimensões + 1 fato + 1 agregação).
    
    Args:
        project_id: ID do projeto GCP
        
    Returns:
        Dict com informações das tabelas criadas
    """
    from google.cloud import bigquery
    
    logger.info("🥇 Criando tabelas Gold...")
    
    try:
        client = bigquery.Client(project=project_id)
        
        # Garantir dataset
        dataset_ref = f"{project_id}.civitas_gold"
        try:
            client.get_dataset(dataset_ref)
        except:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "us-east1"
            client.create_dataset(dataset)
            logger.info(f"   ✓ Dataset civitas_gold criado")
        
        results = {}
        
        # 1. dim_brt_linhas
        logger.info("   📊 Criando dim_brt_linhas...")
        sql1 = f"""
        CREATE OR REPLACE TABLE `{project_id}.civitas_gold.dim_brt_linhas` AS
        SELECT
            TO_HEX(MD5(linha_brt)) as id_linha,
            linha_brt as codigo_linha,
            COUNT(DISTINCT codigo_veiculo) as total_veiculos,
            COUNT(*) as total_viagens,
            AVG(velocidade_kmh) as velocidade_media,
            MIN(data_hora_gps) as primeira_viagem,
            MAX(data_hora_gps) as ultima_viagem
        FROM `{project_id}.civitas_silver.stg_brt_gps`
        WHERE linha_brt IS NOT NULL AND linha_brt != '' AND is_valid_coordinates = TRUE
        GROUP BY linha_brt
        """
        client.query(sql1).result()
        count = list(client.query(f"SELECT COUNT(*) as n FROM `{project_id}.civitas_gold.dim_brt_linhas`").result())[0].n
        logger.info(f"      ✓ dim_brt_linhas: {count} registros")
        results['dim_brt_linhas'] = count
        
        # 2. dim_brt_veiculos
        logger.info("   📊 Criando dim_brt_veiculos...")
        sql2 = f"""
        CREATE OR REPLACE TABLE `{project_id}.civitas_gold.dim_brt_veiculos` AS
        SELECT
            TO_HEX(MD5(codigo_veiculo)) as id_veiculo,
            codigo_veiculo,
            MAX(placa_veiculo) as placa_veiculo,
            COUNT(DISTINCT data_gps) as dias_ativos,
            COUNT(*) as total_registros,
            AVG(velocidade_kmh) as velocidade_media,
            CASE 
                WHEN COUNT(DISTINCT data_gps) >= 5 THEN 'ALTA_ATIVIDADE'
                WHEN COUNT(DISTINCT data_gps) >= 2 THEN 'MEDIA_ATIVIDADE'
                ELSE 'BAIXA_ATIVIDADE'
            END as classificacao_atividade
        FROM `{project_id}.civitas_silver.stg_brt_gps`
        WHERE codigo_veiculo IS NOT NULL AND is_valid_coordinates = TRUE
        GROUP BY codigo_veiculo
        """
        client.query(sql2).result()
        count = list(client.query(f"SELECT COUNT(*) as n FROM `{project_id}.civitas_gold.dim_brt_veiculos`").result())[0].n
        logger.info(f"      ✓ dim_brt_veiculos: {count} registros")
        results['dim_brt_veiculos'] = count
        
        # 3. fct_brt_viagens
        logger.info("   📊 Criando fct_brt_viagens...")
        sql3 = f"""
        CREATE OR REPLACE TABLE `{project_id}.civitas_gold.fct_brt_viagens` AS
        WITH viagens AS (
            SELECT
                codigo_veiculo,
                linha_brt,
                data_gps,
                EXTRACT(HOUR FROM data_hora_gps) as hora,
                COUNT(*) as total_registros,
                AVG(velocidade_kmh) as velocidade_media,
                MIN(data_hora_gps) as inicio_viagem,
                MAX(data_hora_gps) as fim_viagem
            FROM `{project_id}.civitas_silver.stg_brt_gps`
            WHERE is_valid_coordinates = TRUE AND is_valid_velocity = TRUE
            GROUP BY codigo_veiculo, linha_brt, data_gps, EXTRACT(HOUR FROM data_hora_gps)
        )
        SELECT
            TO_HEX(MD5(CONCAT(codigo_veiculo, linha_brt, CAST(data_gps AS STRING), CAST(hora AS STRING)))) as id_viagem,
            codigo_veiculo,
            linha_brt,
            data_gps as data_viagem,
            hora as hora_viagem,
            total_registros,
            velocidade_media,
            inicio_viagem,
            fim_viagem,
            TIMESTAMP_DIFF(fim_viagem, inicio_viagem, MINUTE) as duracao_minutos
        FROM viagens
        """
        client.query(sql3).result()
        count = list(client.query(f"SELECT COUNT(*) as n FROM `{project_id}.civitas_gold.fct_brt_viagens`").result())[0].n
        logger.info(f"      ✓ fct_brt_viagens: {count} registros")
        results['fct_brt_viagens'] = count
        
        # 4. agg_metricas_horarias
        logger.info("   📊 Criando agg_metricas_horarias...")
        sql4 = f"""
        CREATE OR REPLACE TABLE `{project_id}.civitas_gold.agg_metricas_horarias` AS
        SELECT
            data_gps,
            hora_gps,
            COUNT(DISTINCT codigo_veiculo) as veiculos_ativos,
            COUNT(DISTINCT linha_brt) as linhas_ativas,
            COUNT(*) as total_registros,
            AVG(velocidade_kmh) as velocidade_media,
            MIN(velocidade_kmh) as velocidade_minima,
            MAX(velocidade_kmh) as velocidade_maxima,
            STDDEV(velocidade_kmh) as velocidade_desvio_padrao,
            COUNTIF(velocidade_kmh = 0) as veiculos_parados
        FROM `{project_id}.civitas_silver.stg_brt_gps`
        WHERE is_valid_coordinates = TRUE
        GROUP BY data_gps, hora_gps
        """
        client.query(sql4).result()
        count = list(client.query(f"SELECT COUNT(*) as n FROM `{project_id}.civitas_gold.agg_metricas_horarias`").result())[0].n
        logger.info(f"      ✓ agg_metricas_horarias: {count} registros")
        results['agg_metricas_horarias'] = count
        
        logger.info("   ✅ Todas as 4 tabelas Gold criadas!")
        
        return {
            "status": "success",
            "tables": results,
            "total_tables": len(results)
        }
    
    except Exception as e:
        logger.error(f"   ❌ Erro ao criar tabelas Gold: {str(e)}")
        raise
