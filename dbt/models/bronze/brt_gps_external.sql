-- Bronze Layer: View sobre tabela externa do GCS
-- A tabela externa é criada via dbt-external-tables package

{{ config(
    materialized='view',
    schema='civitas_bronze'
) }}

-- Lê da tabela externa configurada em sources.yml
SELECT
    codigo,
    placa,
    linha,
    CAST(latitude AS FLOAT64) as latitude,
    CAST(longitude AS FLOAT64) as longitude,
    SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', dataHora) as dataHora,
    CAST(velocidade AS FLOAT64) as velocidade,
    id_migracao_trajeto,
    sentido,
    trajeto,
    CAST(hodometro AS FLOAT64) as hodometro,
    direcao,
    ignicao,
    CAST(capacidadePeVeiculo AS INT64) as capacidade_pe,
    CAST(capacidadeSentadoVeiculo AS INT64) as capacidade_sentado,
    SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', timestamp_captura) as timestamp_captura
FROM {{ source('gcs_bronze', 'brt_gps_external') }}
WHERE dataHora IS NOT NULL
  AND dataHora != ''
