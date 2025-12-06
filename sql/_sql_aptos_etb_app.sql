WITH base AS (
    SELECT
        fecha_transaccion,
        nombre_cliente,
        REGEXP_REPLACE(telefono_contacto_movil, '[^0-9]', '') AS telefono_limpio,
        plan,
        usuario_mietb,
        fecha_asignacion
    FROM bbdd_cos_bog_etb_auditorias_encuestas.tb_asignacion_app_etb_ds
    WHERE DATE(fecha_asignacion) = CURDATE()
),

filtrada AS (
    SELECT *,
        CASE
            WHEN usuario_mietb IS NULL OR usuario_mietb = '' THEN 'Sin usuario'
            WHEN telefono_limpio = '' THEN 'Telefono vacio'
            WHEN LENGTH(telefono_limpio) <> 10 THEN 'Longitud invalida'
            WHEN telefono_limpio REGEXP '^([0-9])\\1{9}$' THEN 'Telefono invalido'
            WHEN telefono_limpio REGEXP '([0-9])\\1{6,}' THEN 'Telefono invalido'
            ELSE 'apto_pre_dedupe'
        END AS categoria
    FROM base
),

aptos_pre AS (
    SELECT *
    FROM filtrada
    WHERE categoria = 'apto_pre_dedupe'
),

dedupe_phone AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY telefono_limpio
            ORDER BY fecha_transaccion DESC
        ) AS rn_phone
    FROM aptos_pre
),

telefono_duplicados AS (
    SELECT * FROM dedupe_phone WHERE rn_phone > 1
),

keep_phone AS (
    SELECT * FROM dedupe_phone WHERE rn_phone = 1
),

dedupe_user AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY usuario_mietb
            ORDER BY fecha_transaccion DESC
        ) AS rn_user
    FROM keep_phone
),

usuario_duplicados AS (
    SELECT * FROM dedupe_user WHERE rn_user > 1
),

aptos_final AS (
    SELECT * FROM dedupe_user WHERE rn_user = 1
)

SELECT categoria AS categoria, COUNT(*) AS total
FROM filtrada
WHERE categoria <> 'apto_pre_dedupe'
GROUP BY categoria
UNION ALL
SELECT 'Telefono duplicado', COUNT(*) FROM telefono_duplicados
UNION ALL
SELECT 'Usuario duplicado', COUNT(*) FROM usuario_duplicados
UNION ALL
SELECT 'Aptos', COUNT(*) FROM aptos_final;