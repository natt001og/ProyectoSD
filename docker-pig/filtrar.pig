-- Cargar archivo TSV
eventos_raw = LOAD 'eventos_limpios_pig.tsv' USING PigStorage('\t') 
    AS (type:chararray, location:map[], pubMillis:long, street:chararray, city:chararray, uuid:chararray, 
        tipo_incidente:chararray, descripcion:chararray, comuna:chararray, timestamp:chararray);

-- 1. Filtrar eventos incompletos
eventos_filtrados = FILTER eventos_raw BY 
    (type IS NOT NULL) AND
    (location#'x' IS NOT NULL) AND
    (location#'y' IS NOT NULL) AND
    (pubMillis IS NOT NULL) AND
    (street IS NOT NULL) AND
    (city IS NOT NULL) AND
    (uuid IS NOT NULL);

-- 2. Normalización básica de tipo_incidente, descripcion, comuna
eventos_normalizados = FOREACH eventos_filtrados GENERATE
    LOWER(TRIM(type)) AS tipo_incidente,
    TRIM(street) AS descripcion,
    TRIM(city) AS comuna,
    pubMillis,
    location,
    uuid,
    timestamp;

-- 3. Eliminar duplicados por UUID (nos quedamos con el primero)
deduplicados_grupo = GROUP eventos_normalizados BY uuid;
eventos_sin_duplicados = FOREACH deduplicados_grupo {
    ordenados = ORDER eventos_normalizados BY pubMillis ASC;
    uno = LIMIT ordenados 1;
    GENERATE FLATTEN(uno);
};

-- 4. Agrupamiento temporal simple (slot de 5 minutos)
eventos_truncados = FOREACH eventos_sin_duplicados GENERATE
    tipo_incidente,
    descripcion,
    comuna,
    pubMillis,
    location,
    uuid,
    timestamp,
    (long)(pubMillis / 300000) AS slot_5min;

-- 5. Agrupamos por tipo, comuna y slot temporal
agrupados = GROUP eventos_truncados BY (tipo_incidente, comuna, slot_5min);

-- 6. Seleccionamos un evento representativo por grupo
representantes = FOREACH agrupados {
    ordenados = ORDER eventos_truncados BY pubMillis ASC;
    uno = LIMIT ordenados 1;
    GENERATE FLATTEN(uno);
};

-- Para depurar y ver datos en consola (opcional)
-- DUMP representantes;

-- 7. Exportar resultados en formato TSV plano
STORE representantes INTO 'eventos_unificados_pig' USING PigStorage('\t');
