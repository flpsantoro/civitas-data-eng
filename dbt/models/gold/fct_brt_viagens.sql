-- Gold Layer: Fact Table - Viagens BRT
-- Agregação de dados GPS em viagens (trips)
-- Materialização: TABLE (análises pesadas)

{{ config(
    materialized='table',
    schema='brt_gold',
    partition_by={
        "field": "data_viagem",
        "data_type": "date",
        "granularity": "day"
    },
    cluster_by=["linha_brt", "codigo_veiculo"]
) }}

WITH gps_data AS (
    SELECT * FROM {{ ref('stg_brt_gps') }}
),

-- Agregação por veículo, linha, data e hora
trips AS (
    SELECT
        -- Identificadores
        codigo_veiculo,
        placa_veiculo,
        linha_brt,
        sentido_trajeto,
        descricao_trajeto,
        
        -- Dimensões temporais
        data_gps AS data_viagem,
        hora_gps AS hora_viagem,
        dia_semana,
        CASE 
            WHEN dia_semana IN (1, 7) THEN 'FIM_DE_SEMANA'
            ELSE 'DIA_UTIL'
        END AS tipo_dia,
        
        -- Métricas agregadas
        COUNT(*) AS total_registros_gps,
        MIN(data_hora_gps) AS primeiro_registro,
        MAX(data_hora_gps) AS ultimo_registro,
        TIMESTAMP_DIFF(MAX(data_hora_gps), MIN(data_hora_gps), MINUTE) AS duracao_minutos,
        
        -- Métricas de localização
        MIN(latitude) AS latitude_min,
        MAX(latitude) AS latitude_max,
        AVG(latitude) AS latitude_media,
        MIN(longitude) AS longitude_min,
        MAX(longitude) AS longitude_max,
        AVG(longitude) AS longitude_media,
        
        -- Métricas de velocidade
        AVG(velocidade_kmh) AS velocidade_media,
        MIN(velocidade_kmh) AS velocidade_minima,
        MAX(velocidade_kmh) AS velocidade_maxima,
        STDDEV(velocidade_kmh) AS velocidade_desvio_padrao,
        
        -- Métricas de hodômetro
        MIN(hodometro_km) AS hodometro_inicial,
        MAX(hodometro_km) AS hodometro_final,
        (MAX(hodometro_km) - MIN(hodometro_km)) AS distancia_percorrida_km,
        
        -- Capacidade
        AVG(capacidade_total) AS capacidade_media,
        
        -- Contadores de status
        COUNTIF(status_ignicao = 'LIGADO') AS registros_ignicao_ligada,
        COUNTIF(status_ignicao = 'DESLIGADO') AS registros_ignicao_desligada,
        
        -- Percentuais
        SAFE_DIVIDE(
            COUNTIF(status_ignicao = 'LIGADO'),
            COUNT(*)
        ) * 100 AS percentual_tempo_ligado,
        
        -- Qualidade dos dados
        MIN(data_hora_captura) AS primeira_captura,
        MAX(data_hora_captura) AS ultima_captura

    FROM gps_data
    GROUP BY 
        codigo_veiculo,
        placa_veiculo,
        linha_brt,
        sentido_trajeto,
        descricao_trajeto,
        data_gps,
        hora_gps,
        dia_semana
)

SELECT 
    -- Surrogate key
    {{ dbt_utils.generate_surrogate_key([
        'codigo_veiculo', 
        'linha_brt', 
        'data_viagem', 
        'hora_viagem',
        'sentido_trajeto'
    ]) }} AS id_viagem,
    
    *,
    
    -- Métricas derivadas
    CASE 
        WHEN duracao_minutos > 0 
        THEN SAFE_DIVIDE(distancia_percorrida_km, duracao_minutos) * 60
        ELSE 0
    END AS velocidade_media_calculada,
    
    -- Classificação de viagem
    CASE 
        WHEN duracao_minutos < 5 THEN 'MUITO_CURTA'
        WHEN duracao_minutos BETWEEN 5 AND 15 THEN 'CURTA'
        WHEN duracao_minutos BETWEEN 16 AND 30 THEN 'MEDIA'
        WHEN duracao_minutos BETWEEN 31 AND 60 THEN 'LONGA'
        ELSE 'MUITO_LONGA'
    END AS classificacao_duracao,
    
    -- Metadados
    CURRENT_TIMESTAMP() AS dbt_updated_at

FROM trips
WHERE 
    -- Filtros de qualidade
    total_registros_gps >= 2  -- Pelo menos 2 pontos GPS
    AND duracao_minutos >= 1   -- Pelo menos 1 minuto de duração
