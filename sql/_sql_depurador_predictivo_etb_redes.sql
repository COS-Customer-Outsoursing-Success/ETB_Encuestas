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
    FROM bbdd_cos_bog_etb_auditorias_encuestas.tb_asignacion_redes_etb_coalesce_ds
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
SELECT 
    canal AS red_social_de_contacto,
    fecha AS completado,
    tipificacion AS categoria_de_contacto,
    numero_pqr AS mdm,
    numero_identificacion,
    nombre_cliente,
    telefono_contacto_2 AS phone,
    MONTH(fecha) AS mes,
    YEAR(fecha) AS anio
FROM bbdd_cos_bog_etb_auditorias_encuestas.tb_asignacion_redes_sociales_etb_ds t
WHERE fecha_asignacion >= CURDATE()
AND telefono_contacto_2 REGEXP '^(3[0-9]{9}|601[0-9]{7})$'
AND telefono_contacto_2 IN (
    SELECT telefono_contacto_2
    FROM bbdd_cos_bog_etb_auditorias_encuestas.tb_asignacion_redes_sociales_etb_ds
    WHERE fecha_asignacion >= CURDATE()
    GROUP BY telefono_contacto_2
    HAVING COUNT(*) = 1
);
#*/

/*
ORDER BY 
    CASE 
        WHEN tipo_phone = 'telefono_contacto_1' AND (vicidial_calls <= 3 OR vicidial_calls IS NULL) THEN 1
        WHEN tipo_phone IN ('telefono_contacto_2', 'telefono_contacto_3') THEN 2
        ELSE 3
    END ASC,
    vicidial_calls ASC
;
*/