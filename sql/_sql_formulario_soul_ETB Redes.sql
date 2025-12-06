SELECT 
    id,
    canal AS red_social_de_contacto,
    fecha AS completado,
    asesor,
    tipificacion AS categoria_de_contacto,
    causal_pqr AS informacion,
    sintoma_pqr AS fallas_tecnicas,
    numero_pqr AS mdm,
    numero_identificacion,
    nombre_cliente,
    telefono_contacto_1 AS telefono_fijo,
    telefono_contacto_2 AS celular,
    telefono_contacto_3 AS telefono_complementario,
    MONTH(fecha) AS mes,
    YEAR(fecha) AS anio
FROM bbdd_cos_bog_etb_auditorias_encuestas.tb_asignacion_redes_sociales_etb_ds t
WHERE fecha_asignacion >= CURDATE()
AND (
        (
            t.telefono_contacto_2 REGEXP '^(3[0-9]{9}|601[0-9]{7})$'
            AND (
                SELECT COUNT(*) 
                FROM bbdd_cos_bog_etb_auditorias_encuestas.tb_asignacion_redes_sociales_etb_ds 
                WHERE telefono_contacto_2 = t.telefono_contacto_2
                AND fecha_asignacion >= CURDATE()
            ) = 1
        )
    OR
        (
            (t.telefono_contacto_2 NOT REGEXP '^(3[0-9]{9}|601[0-9]{7})$')
            AND t.telefono_contacto_1 REGEXP '^(3[0-9]{9}|601[0-9]{7})$'
            AND (
                SELECT COUNT(*) 
                FROM bbdd_cos_bog_etb_auditorias_encuestas.tb_asignacion_redes_sociales_etb_ds 
                WHERE telefono_contacto_1 = t.telefono_contacto_1
                AND fecha_asignacion >= CURDATE()
            ) = 1
        )
    OR
        (
            (t.telefono_contacto_2 NOT REGEXP '^(3[0-9]{9}|601[0-9]{7})$')
            AND (t.telefono_contacto_1 NOT REGEXP '^(3[0-9]{9}|601[0-9]{7})$')
            AND t.telefono_contacto_3 REGEXP '^(3[0-9]{9}|601[0-9]{7})$'
            AND (
                SELECT COUNT(*) 
                FROM bbdd_cos_bog_etb_auditorias_encuestas.tb_asignacion_redes_sociales_etb_ds 
                WHERE telefono_contacto_3 = t.telefono_contacto_3
                AND fecha_asignacion >= CURDATE()
            ) = 1
        )
);
