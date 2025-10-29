-- Gold Layer: Aggregate Table - Métricas por Hora
-- Análise de desempenho operacional por hora do dia
-- Materialização: TABLE (análises agregadas)

{{ config(
    materialized='table',
    schema='brt_gold',
    partition_by={
        "field": "data_analise",
        "data_type": "date",
        "granularity": "day"
    }
) }}

WITH gps_data AS (
    SELECT * FROM {{ ref('stg_brt_gps') }}
),

hourly_metrics AS (
    SELECT
        -- Dimensões
        data_gps AS data_analise,
        hora_gps AS hora_analise,
        dia_semana,
        CASE 
            WHEN dia_semana IN (1, 7) THEN 'FIM_DE_SEMANA'
            ELSE 'DIA_UTIL'
        END AS tipo_dia,
        
        -- Classificação de período
        CASE 
            WHEN hora_gps BETWEEN 6 AND 9 THEN 'PICO_MANHA'
            WHEN hora_gps BETWEEN 10 AND 16 THEN 'FORA_PICO'
            WHEN hora_gps BETWEEN 17 AND 20 THEN 'PICO_TARDE'
            WHEN hora_gps BETWEEN 21 AND 23 THEN 'NOITE'
            ELSE 'MADRUGADA'
        END AS periodo_dia,
        
        -- Contagens
        COUNT(*) AS total_registros_gps,
        COUNT(DISTINCT codigo_veiculo) AS total_veiculos_ativos,
        COUNT(DISTINCT linha_brt) AS total_linhas_ativas,
        
        -- Métricas de velocidade
        AVG(velocidade_kmh) AS velocidade_media,
        MIN(velocidade_kmh) AS velocidade_minima,
        MAX(velocidade_kmh) AS velocidade_maxima,
        STDDEV(velocidade_kmh) AS velocidade_desvio_padrao,
        
        -- Distribuição de velocidade
        COUNTIF(velocidade_kmh = 0) AS veiculos_parados,
        COUNTIF(velocidade_kmh BETWEEN 0.1 AND 20) AS veiculos_lento,
        COUNTIF(velocidade_kmh BETWEEN 20.1 AND 50) AS veiculos_moderado,
        COUNTIF(velocidade_kmh > 50) AS veiculos_rapido,
        
        -- Status
        COUNTIF(status_ignicao = 'LIGADO') AS veiculos_ligados,
        COUNTIF(status_ignicao = 'DESLIGADO') AS veiculos_desligados,
        
        -- Capacidade total disponível
        SUM(DISTINCT capacidade_total) AS capacidade_total_frota

    FROM gps_data
    GROUP BY 
        data_analise,
        hora_analise,
        dia_semana
)

SELECT 
    -- Surrogate key
    {{ dbt_utils.generate_surrogate_key(['data_analise', 'hora_analise']) }} AS id_metrica_hora,
    
    -- Dimensões
    data_analise,
    hora_analise,
    dia_semana,
    tipo_dia,
    periodo_dia,
    
    -- Contagens
    total_registros_gps,
    total_veiculos_ativos,
    total_linhas_ativas,
    
    -- Velocidade
    ROUND(velocidade_media, 2) AS velocidade_media_kmh,
    ROUND(velocidade_minima, 2) AS velocidade_minima_kmh,
    ROUND(velocidade_maxima, 2) AS velocidade_maxima_kmh,
    ROUND(velocidade_desvio_padrao, 2) AS velocidade_desvio_padrao,
    
    -- Distribuição de velocidade
    veiculos_parados,
    veiculos_lento,
    veiculos_moderado,
    veiculos_rapido,
    
    -- Percentuais de distribuição
    ROUND(SAFE_DIVIDE(veiculos_parados, total_veiculos_ativos) * 100, 2) AS pct_parados,
    ROUND(SAFE_DIVIDE(veiculos_lento, total_veiculos_ativos) * 100, 2) AS pct_lento,
    ROUND(SAFE_DIVIDE(veiculos_moderado, total_veiculos_ativos) * 100, 2) AS pct_moderado,
    ROUND(SAFE_DIVIDE(veiculos_rapido, total_veiculos_ativos) * 100, 2) AS pct_rapido,
    
    -- Status
    veiculos_ligados,
    veiculos_desligados,
    ROUND(SAFE_DIVIDE(veiculos_ligados, total_veiculos_ativos) * 100, 2) AS pct_ligados,
    
    -- Capacidade
    capacidade_total_frota,
    
    -- Metadados
    CURRENT_TIMESTAMP() AS dbt_updated_at

FROM hourly_metrics
