-- Gold Layer: Dimension Table - Veículos BRT
-- Informações sobre os veículos da frota BRT
-- Materialização: TABLE (pequena, atualização periódica)

{{ config(
    materialized='table',
    schema='brt_gold'
) }}

WITH gps_data AS (
    SELECT * FROM {{ ref('stg_brt_gps') }}
),

veiculo_stats AS (
    SELECT
        codigo_veiculo,
        placa_veiculo,
        
        -- Linhas operadas
        COUNT(DISTINCT linha_brt) AS total_linhas_operadas,
        ARRAY_AGG(DISTINCT linha_brt IGNORE NULLS ORDER BY linha_brt) AS linhas_operadas,
        
        -- Contagens
        COUNT(*) AS total_registros,
        COUNT(DISTINCT data_gps) AS dias_ativos,
        
        -- Métricas de velocidade
        AVG(velocidade_kmh) AS velocidade_media,
        MIN(velocidade_kmh) AS velocidade_minima,
        MAX(velocidade_kmh) AS velocidade_maxima,
        STDDEV(velocidade_kmh) AS velocidade_desvio_padrao,
        
        -- Métricas de distância
        MAX(hodometro_km) - MIN(hodometro_km) AS distancia_total_percorrida,
        
        -- Capacidades
        MAX(capacidade_total) AS capacidade_maxima,
        AVG(capacidade_total) AS capacidade_media,
        
        -- Cobertura temporal
        MIN(data_gps) AS primeira_data_registro,
        MAX(data_gps) AS ultima_data_registro,
        DATE_DIFF(MAX(data_gps), MIN(data_gps), DAY) AS dias_operacao_span,
        
        -- Status de ignição
        COUNTIF(status_ignicao = 'LIGADO') AS registros_ligado,
        COUNTIF(status_ignicao = 'DESLIGADO') AS registros_desligado,
        SAFE_DIVIDE(
            COUNTIF(status_ignicao = 'LIGADO'),
            COUNT(*)
        ) * 100 AS percentual_tempo_ligado

    FROM gps_data
    WHERE codigo_veiculo IS NOT NULL
    GROUP BY 
        codigo_veiculo,
        placa_veiculo
)

SELECT 
    -- Surrogate key
    {{ dbt_utils.generate_surrogate_key(['codigo_veiculo']) }} AS id_veiculo,
    
    codigo_veiculo,
    placa_veiculo,
    
    -- Operação
    total_linhas_operadas,
    linhas_operadas,
    total_registros,
    dias_ativos,
    
    -- Velocidade
    ROUND(velocidade_media, 2) AS velocidade_media_kmh,
    ROUND(velocidade_minima, 2) AS velocidade_minima_kmh,
    ROUND(velocidade_maxima, 2) AS velocidade_maxima_kmh,
    ROUND(velocidade_desvio_padrao, 2) AS velocidade_desvio_padrao_kmh,
    
    -- Distância
    ROUND(distancia_total_percorrida, 2) AS distancia_total_km,
    CASE 
        WHEN dias_ativos > 0 
        THEN ROUND(distancia_total_percorrida / dias_ativos, 2)
        ELSE 0
    END AS distancia_media_diaria_km,
    
    -- Capacidade
    capacidade_maxima,
    ROUND(capacidade_media, 0) AS capacidade_media,
    
    -- Temporal
    primeira_data_registro,
    ultima_data_registro,
    dias_operacao_span,
    
    -- Status
    registros_ligado,
    registros_desligado,
    ROUND(percentual_tempo_ligado, 2) AS percentual_tempo_ligado,
    
    -- Classificações
    CASE 
        WHEN dias_ativos >= 20 THEN 'ALTA_ATIVIDADE'
        WHEN dias_ativos BETWEEN 10 AND 19 THEN 'MEDIA_ATIVIDADE'
        ELSE 'BAIXA_ATIVIDADE'
    END AS classificacao_atividade,
    
    CASE 
        WHEN distancia_total_percorrida >= 500 THEN 'ALTO_USO'
        WHEN distancia_total_percorrida BETWEEN 100 AND 499 THEN 'MEDIO_USO'
        ELSE 'BAIXO_USO'
    END AS classificacao_uso,
    
    -- Metadados
    CURRENT_TIMESTAMP() AS dbt_updated_at

FROM veiculo_stats
ORDER BY distancia_total_percorrida DESC
