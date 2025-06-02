-- Configuración para modo local
SET mapreduce.framework.name 'local';
SET pig.usenewlogicalplan 'false';

-- Cargar datos limpios
datos = LOAD 'eventos_limpios.tsv'
    USING PigStorage('\t') AS (
        comuna:chararray,
        tipo_incidente:chararray,
        timestamp:long,
        descripcion:chararray,
        votos_positivos:float,
        confiabilidad:int
    );

-- 1. Análisis por comuna y tipo (sin cambios)
agrupados = GROUP datos BY (comuna, tipo_incidente);

conteo_por_comuna_tipo = FOREACH agrupados GENERATE
    FLATTEN(group) AS (comuna, tipo_incidente),
    COUNT(datos) AS cantidad_eventos,
    AVG(datos.votos_positivos) AS avg_votos,
    AVG(datos.confiabilidad) AS avg_confiabilidad;

-- 2. Análisis temporal simplificado (sin piggybank)
con_fechas = FOREACH datos GENERATE
    comuna,
    tipo_incidente,
    (timestamp / (1000*60*60*24)) as dias_desde_epoch,  -- Días desde epoch
    votos_positivos,
    confiabilidad;

-- Agrupar por día y tipo
agrupado_por_fecha = GROUP con_fechas BY (dias_desde_epoch, tipo_incidente);

conteo_temporal = FOREACH agrupado_por_fecha GENERATE
    FLATTEN(group) AS (dia, tipo_incidente),
    COUNT(con_fechas) AS total_eventos,
    AVG(con_fechas.votos_positivos) AS avg_votos;

-- Guardar resultados
STORE conteo_por_comuna_tipo INTO 'conteo_por_comuna_tipo.tsv' USING PigStorage('\t');
STORE conteo_temporal INTO 'conteo_temporal.tsv' USING PigStorage('\t');