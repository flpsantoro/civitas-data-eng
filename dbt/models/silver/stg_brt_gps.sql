-- Silver Layer: Staging BRT GPS
-- Limpeza e padronização dos dados brutos
-- Materialização: VIEW (transformações leves)

{{ config(
    materialized='view'
) }}

WITH source AS (
    SELECT * FROM {{ source('gcs_bronze', 'brt_gps_external') }}
),

cleaned AS (
    SELECT
        -- Identificadores
        TRIM(codigo) AS codigo_veiculo,
        UPPER(TRIM(placa)) AS placa_veiculo,
        TRIM(linha) AS linha_brt,
        
        -- Localização
        ROUND(CAST(latitude AS FLOAT64), 6) AS latitude,
        ROUND(CAST(longitude AS FLOAT64), 6) AS longitude,
        
        -- Timestamps
        PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', dataHora) AS data_hora_gps,
        PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', timestamp_captura) AS data_hora_captura,
        
        -- Métricas
        ROUND(CAST(velocidade AS FLOAT64), 2) AS velocidade_kmh,
        CAST(hodometro AS FLOAT64) AS hodometro_km,
        
        -- Categorias
        CASE 
            WHEN UPPER(TRIM(sentido)) = 'I' THEN 'IDA'
            WHEN UPPER(TRIM(sentido)) = 'V' THEN 'VOLTA'
            WHEN UPPER(TRIM(sentido)) = 'C' THEN 'CIRCULAR'
            ELSE 'DESCONHECIDO'
        END AS sentido_trajeto,
        
        CASE 
            WHEN UPPER(TRIM(ignicao)) = 'L' THEN 'LIGADO'
            WHEN UPPER(TRIM(ignicao)) = 'D' THEN 'DESLIGADO'
            ELSE 'DESCONHECIDO'
        END AS status_ignicao,
        
        TRIM(trajeto) AS descricao_trajeto,
        TRIM(direcao) AS direcao_veiculo,
        
        -- Capacidades
        CAST(capacidadePeVeiculo AS INT64) AS capacidade_pe,
        CAST(capacidadeSentadoVeiculo AS INT64) AS capacidade_sentado,
        (CAST(capacidadePeVeiculo AS INT64) + CAST(capacidadeSentadoVeiculo AS INT64)) AS capacidade_total,
        
        -- Metadados
        TRIM(id_migracao_trajeto) AS id_migracao_trajeto,
        
        -- Derived fields
        DATE(CAST(dataHora AS TIMESTAMP)) AS data_gps,
        EXTRACT(HOUR FROM CAST(dataHora AS TIMESTAMP)) AS hora_gps,
        EXTRACT(DAYOFWEEK FROM CAST(dataHora AS TIMESTAMP)) AS dia_semana,
        
        -- Data quality flags
        CASE 
            WHEN CAST(latitude AS FLOAT64) BETWEEN -90 AND 90 
             AND CAST(longitude AS FLOAT64) BETWEEN -180 AND 180
            THEN TRUE
            ELSE FALSE
        END AS is_valid_coordinates,
        
        CASE 
            WHEN CAST(velocidade AS FLOAT64) >= 0 
             AND CAST(velocidade AS FLOAT64) <= 150
            THEN TRUE
            ELSE FALSE
        END AS is_valid_velocity

    FROM source
    WHERE 
        -- Filtros básicos de qualidade
        codigo IS NOT NULL
        AND placa IS NOT NULL
        AND latitude IS NOT NULL
        AND longitude IS NOT NULL
        AND dataHora IS NOT NULL
)

SELECT 
    *,
    -- Hash ID para deduplicação (chave composta para garantir unicidade)
    {{ dbt_utils.generate_surrogate_key([
        'codigo_veiculo', 
        'data_hora_gps', 
        'latitude', 
        'longitude', 
        'velocidade_kmh',
        'data_hora_captura'
    ]) }} AS id_registro
    
FROM cleaned
WHERE 
    is_valid_coordinates = TRUE
    AND is_valid_velocity = TRUE
