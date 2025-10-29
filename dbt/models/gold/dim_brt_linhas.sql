-- Gold Layer: Dimension Table - Linhas BRT
-- Informações sobre as linhas de BRT
-- Materialização: TABLE (pequena, atualização rara)

{{ config(
    materialized='table',
    schema='brt_gold'
) }}

WITH gps_data AS (
    SELECT * FROM {{ ref('stg_brt_gps') }}
),

linha_stats AS (
    SELECT
        linha_brt,
        
        -- Contagens
        COUNT(DISTINCT codigo_veiculo) AS total_veiculos,
        COUNT(DISTINCT placa_veiculo) AS total_placas_unicas,
        COUNT(DISTINCT descricao_trajeto) AS total_trajetos_distintos,
        COUNT(*) AS total_registros,
        
        -- Métricas de velocidade
        AVG(velocidade_kmh) AS velocidade_media_linha,
        MAX(velocidade_kmh) AS velocidade_maxima_registrada,
        
        -- Capacidades
        AVG(capacidade_total) AS capacidade_media_veiculos,
        MIN(capacidade_total) AS capacidade_minima_veiculos,
        MAX(capacidade_total) AS capacidade_maxima_veiculos,
        
        -- Cobertura temporal
        MIN(data_gps) AS primeira_data_registro,
        MAX(data_gps) AS ultima_data_registro,
        DATE_DIFF(MAX(data_gps), MIN(data_gps), DAY) AS dias_operacao,
        
        -- Trajetos mais comuns
        ARRAY_AGG(
            DISTINCT descricao_trajeto 
            IGNORE NULLS 
            ORDER BY descricao_trajeto 
            LIMIT 10
        ) AS trajetos_operados

    FROM gps_data
    WHERE linha_brt IS NOT NULL
    GROUP BY linha_brt
)

SELECT 
    -- Surrogate key
    {{ dbt_utils.generate_surrogate_key(['linha_brt']) }} AS id_linha,
    
    linha_brt AS codigo_linha,
    
    -- Métricas operacionais
    total_veiculos,
    total_placas_unicas,
    total_trajetos_distintos,
    total_registros,
    
    -- Métricas de velocidade
    ROUND(velocidade_media_linha, 2) AS velocidade_media_kmh,
    ROUND(velocidade_maxima_registrada, 2) AS velocidade_maxima_kmh,
    
    -- Capacidades
    ROUND(capacidade_media_veiculos, 0) AS capacidade_media,
    capacidade_minima_veiculos AS capacidade_minima,
    capacidade_maxima_veiculos AS capacidade_maxima,
    
    -- Cobertura temporal
    primeira_data_registro,
    ultima_data_registro,
    dias_operacao,
    
    -- Classificação da linha
    CASE 
        WHEN total_veiculos >= 50 THEN 'ALTA_DEMANDA'
        WHEN total_veiculos BETWEEN 20 AND 49 THEN 'MEDIA_DEMANDA'
        ELSE 'BAIXA_DEMANDA'
    END AS classificacao_demanda,
    
    -- Trajetos
    trajetos_operados,
    
    -- Metadados
    CURRENT_TIMESTAMP() AS dbt_updated_at

FROM linha_stats
ORDER BY total_veiculos DESC
