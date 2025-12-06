/*
WITH base AS (
    SELECT *,
        CASE 
            WHEN (
            excluir_vicidial = 1 
            OR 
            excluir_soul = 1
				)
            THEN 1 ELSE 0 
        END AS exclusiones_general
    FROM bbdd_cos_bog_etb_auditorias_encuestas.tb_asignacion_app_etb_coalesce_ds
    WHERE periodo = 202512
)
, consolidados AS (
    SELECT *,
           MAX(exclusiones_general) OVER(PARTITION BY phone) AS exclusion_total
    FROM base
)
*/

-- -----------------------------------------------------------------------------------------
-- Predictivo Sin Gestion: Descomentar colocando un # al inicio de los simbolos "/*" ---- --
-- -----------------------------------------------------------------------------------------
/*
	AND tipo_phone IN ('telefono_contacto_movil')
	AND (
		vicidial_calls = 0 
        OR 
        vicidial_calls IS NULL
        )
    
    AND tipificacion_mejor_gestion_soul IS NULL
*/

-- -----------------------------------------------------------------------------------------
-- Predictivo No Contacto: Descomentar colocando un # al inicio de los simbolos "/*" ---- --
-- -----------------------------------------------------------------------------------------
/*
	AND tipo_phone IN ('telefono_contacto_movil')
    
	AND ( 
    vicidial_calls <= 15
    )

    AND (
    tipificacion_mejor_gestion_soul IN ('No contesta', 'Cliente Cuelga La Llamada')
    OR 
    tipificacion_mejor_gestion_soul IS NULL
    )
    
#	AND tipificacion_mejor_gestion IN ('Agent Not Available', 'Agent Altnum', 'No Contacto','ADAIR')    
#	AND tipificacion_mejor_gestion NOT IN ('Agent Not Available', 'Agent Altnum', 'No Contacto','ADAIR')
#*/
/*
    AND (
		fecha_ultima_gestion IS NULL OR DATE(fecha_ultima_gestion) < CURDATE() - INTERVAL 1 DAY
	)
	AND (
		fecha_ultima_gestion_soul IS NULL OR DATE(fecha_ultima_gestion_soul) < CURDATE() - INTERVAL 1 DAY
	)
*/

-- --------------------------------------------------------------------------------------------------------------
-- Descarmar para asignacion inicial y cargue de base nueva en vicidial sin depure
-- --------------------------------------------------------------------------------------------------------------
#/*
WITH base AS (
    SELECT
        fecha_transaccion,
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
      AND telefono_limpio NOT REGEXP '^([0-9])\\1{9}$'
      AND telefono_limpio NOT REGEXP '([0-9])\\1{6,}'
)
SELECT
    fecha_transaccion,
    nombre_cliente,
    telefono_limpio AS phone,
    plan,
    CONCAT(
        usuario_mietb,
        DATEDIFF(fecha_transaccion, '1899-12-30')
    ) AS identificador,
    YEAR(fecha_transaccion) AS anio,
    MONTHNAME(fecha_transaccion) AS mes,
    usuario_mietb
FROM validos
WHERE rn = 1
GROUP BY usuario_mietb;
#*/

/*
ORDER BY 
    CASE 
        WHEN tipo_phone = 'telefono_contacto_movil' AND (vicidial_calls <= 3 OR vicidial_calls IS NULL) THEN 1
        ELSE 2
    END ASC,
    vicidial_calls ASC
;
*/