{% macro test_valid_rio_coordinates(model, column_lat, column_lon) %}

-- Test: Validar se as coordenadas estão dentro do Rio de Janeiro
-- Rio de Janeiro bounds aproximados:
-- Latitude: -23.0 a -22.7
-- Longitude: -43.8 a -43.1

SELECT 
    {{ column_lat }} AS latitude,
    {{ column_lon }} AS longitude,
    COUNT(*) AS invalid_count
FROM {{ model }}
WHERE 
    {{ column_lat }} NOT BETWEEN -23.0 AND -22.7
    OR {{ column_lon }} NOT BETWEEN -43.8 AND -43.1
GROUP BY {{ column_lat }}, {{ column_lon }}
HAVING COUNT(*) > 0

{% endmacro %}
