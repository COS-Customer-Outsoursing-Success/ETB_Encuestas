WITH base AS (
    SELECT *,
        CASE 
            WHEN (
            excluir_vicidial = 1 
            OR 
            excluir_soul = 1
				)
/*              OR placa IN (
					SELECT placa 
					FROM bbdd_cos_bog_grupo_axa.tb_asignacion_falabella_v2_no_aptos 
					WHERE periodo = 202511
              )
              OR phone IN ( 
					SELECT 
						phone_number_dialed 
                    FROM bbdd_cos_bog_grupo_axa.tb_markings_2300_daily
					WHERE campana = 'Falabella'
                    )
*/
            THEN 1 ELSE 0 
        END AS exclusiones_general
    FROM bbdd_cos_bog_allianz.tb_asignacion_crosseling_vida_deudor_coalesce
    WHERE periodo = 202511
)
, consolidados AS (
    SELECT *,
           MAX(exclusiones_general) OVER(PARTITION BY phone) AS exclusion_total
    FROM base
)
/*
SELECT 
*
FROM consolidados
WHERE exclusion_total = 0
*/

-- -----------------------------------------------------------------------------------------
-- Predictivo Sin Gestion: Descomentar colocando un # al inicio de los simbolos "/*" ---- --
-- -----------------------------------------------------------------------------------------
/*
	AND tipo_phone IN ('tel1_org') #,'tel2_org'
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
	AND tipo_phone IN ('tel1_org') #,'telefono2'
    
	AND ( 
    vicidial_calls <= 20
    )

#    AND (
#    tipificacion_mejor_gestion_soul IN ('No contesta')#, 'Cliente Cuelga La Llamada')
#    OR 
#    tipificacion_mejor_gestion_soul IS NULL
#    )
    
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
	documento,
	COALESCE(
		NULLIF(NULLIF(NULLIF(telefono, ''), '0'), '-'),
		NULLIF(NULLIF(NULLIF(telefono2, ''), '0'), '-'),
		NULLIF(NULLIF(NULLIF(telefono3, ''), '0'), '-')
	) AS phone,
	nombre,
	poliza,
	placa,
    email
FROM bbdd_cos_bog_allianz.tb_asignacion_crosseling_vida_deudor
WHERE fecha_asignacion >= CURDATE()
  AND (
        (telefono IS NOT NULL AND telefono NOT IN ('', '0', '-')) 
        OR (telefono2 IS NOT NULL AND telefono2 NOT IN ('', '0', '-')) 
        OR (telefono3 IS NOT NULL AND telefono3 NOT IN ('', '0', '-'))
      );
#*/

/*
ORDER BY 
    CASE 
        WHEN tipo_phone = 'telefono' AND (vicidial_calls <= 3 OR vicidial_calls IS NULL) THEN 1
        WHEN tipo_phone IN ('telefono2', 'telefono3') THEN 2
        WHEN tipo_phone = 'telefono' AND vicidial_calls > 3 THEN 3
        ELSE 4
    END ASC,
    vicidial_calls ASC
;
*/