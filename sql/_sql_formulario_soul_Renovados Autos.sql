SELECT
    placa,
    poliza,
    clave_intermediario,
    sucursal,
    regional,
    prima_ant,
    prima_renov,
    IF(descuento IS NULL, 0, descuento) AS descuento,
    IF(cedula_asegurado IS NULL, placa, cedula_asegurado) AS cedula_asegurado, -- Cambio porque no mandan cedula asegurado
    documento,
    nombre,
    trat_datos,
    IF(telefono = '-' OR telefono IS NULL, '0', telefono) AS telefono,
    IF(telefono2 = '-' OR telefono2 IS NULL, '0', telefono2) AS telefono2,
    IF(telefono3 = '-' OR telefono3 IS NULL, '0', telefono3) AS telefono3,
    email,
    nombre_intermediario,
    IF(cliente_activo IS NULL, 'NO HAY DATO', cliente_activo) AS cliente_activo,
    fecha_utima_renovacion,
    poliza_vigente
FROM bbdd_cos_bog_allianz.tb_asignacion_renovaciones_autos
WHERE periodo = '202511';
