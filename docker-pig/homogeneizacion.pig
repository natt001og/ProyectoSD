-- Configuración para modo local
SET mapreduce.framework.name 'local';
SET pig.usenewlogicalplan 'false';

-- Cargar datos desde el archivo data.tsv en el directorio actual
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

-- Filtrar registros inválidos
validos = FILTER raw BY 
    tipo IS NOT NULL AND 
    city IS NOT NULL AND 
    reportDescription IS NOT NULL AND
    pubMillis IS NOT NULL;

-- Normalizar datos
normalizados = FOREACH validos GENERATE
    LOWER(TRIM(city)) AS comuna,
    LOWER(TRIM(tipo)) AS tipo_incidente,
    pubMillis AS timestamp,
    TRIM(reportDescription) AS descripcion,
    nThumbsUp AS votos_positivos,
    reliability AS confiabilidad;

-- Eliminar duplicados
limpios = DISTINCT normalizados;

-- Guardar salida en el directorio actual
STORE limpios INTO 'eventos_limpios.tsv'
    USING PigStorage('\t');