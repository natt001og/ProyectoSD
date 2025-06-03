-- Configuración para modo local
SET mapreduce.framework.name 'local';
SET pig.usenewlogicalplan 'false';

-- Cargar datos desde el archivo data.tsv
raw = LOAD 'data.tsv'
    USING PigStorage('\t') AS (
        country:chararray,
        nThumbsUp:float,
        city:chararray,
        reportRating:int,
        reportByMunicipalityUser:chararray,
        reliability:int,
        tipo:chararray,
        fromNodeId:chararray,
        uuid:chararray,
        speed:int,
        reportMood:int,
        subtype:chararray,
        street:chararray,
        additionalInfo:chararray,
        toNodeId:chararray,
        id:chararray,
        nComments:float,
        reportBy:chararray,
        inscale:chararray,
        comments:chararray,
        confidence:int,
        roadType:int,
        magvar:int,
        wazeData:chararray,
        location:chararray,
        pubMillis:long,
        provider:chararray,
        providerId:chararray,
        reportDescription:chararray,
        imageUrl:chararray,
        imageId:chararray,
        nImages:int
    );

-- Filtrar registros válidos (relajado para conservar más datos)
validos = FILTER raw BY 
    tipo IS NOT NULL AND 
    city IS NOT NULL AND 
    pubMillis IS NOT NULL;

-- Normalizar datos (ahora aceptamos reportDescription vacío)
normalizados = FOREACH validos GENERATE
    LOWER(TRIM(city)) AS comuna,
    LOWER(TRIM(tipo)) AS tipo_incidente,
    pubMillis AS timestamp,
    (reportDescription IS NOT NULL ? TRIM(reportDescription) : '') AS descripcion,
    (nThumbsUp IS NOT NULL ? nThumbsUp : 0.0) AS votos_positivos,
    (reliability IS NOT NULL ? reliability : 0) AS confiabilidad,
    uuid AS identificador_unico;

-- Eliminar duplicados solo si son 100% idénticos en los campos clave
limpios = DISTINCT normalizados;

-- Guardar resultados
STORE limpios INTO 'eventos_limpios.tsv'
    USING PigStorage('\t');
