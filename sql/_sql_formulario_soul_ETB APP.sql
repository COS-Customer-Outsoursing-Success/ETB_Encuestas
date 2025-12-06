WITH base AS (
    SELECT
        fecha_transaccion,
        tipo_transaccion,
        canal_1,
        segmento,
        numero_conexion,
        nombre_cliente,
        REGEXP_REPLACE(telefono_contacto_movil, '[^0-9]', '') AS telefono_limpio,
        plan,
        usuario_mietb,
        fecha_asignacion
    FROM bbdd_cos_bog_etb_auditorias_encuestas.tb_asignacion_app_etb_ds
),
validos AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY telefono_limpio
            ORDER BY fecha_transaccion DESC
        ) AS rn
    FROM base
    WHERE fecha_asignacion >= CURDATE()
      AND usuario_mietb IS NOT NULL
      AND usuario_mietb <> '-'
      AND telefono_limpio <> ''
      AND LENGTH(telefono_limpio) = 10
      AND telefono_limpio NOT REGEXP '([0-9])\\1{5,}'
)
SELECT
    CONCAT(
        usuario_mietb,
        DATEDIFF(fecha_transaccion, '1899-12-30')
    ) AS identificador,
    fecha_transaccion,
    tipo_transaccion,
    canal_1,
    segmento,
    numero_conexion,
    nombre_cliente,
    telefono_limpio AS telefono,
    plan,
    usuario_mietb,
    YEAR(fecha_transaccion) AS anio,
    MONTHNAME(fecha_transaccion) AS mes
FROM validos
WHERE rn = 1
GROUP BY usuario_mietb;
