-- =============================================================================
-- INVILARA - Script de ajustes y TRIGGERS (Fase I)
-- Base de datos: invilara  (y bitacora en invilara_seguridad)
-- Servidor: MariaDB 11.8  |  Generado: 2026-07-08
-- -----------------------------------------------------------------------------
-- INSTRUCCIONES:
--   1) Ejecutar en la BD "invilara" (USE invilara;).
--   2) Es idempotente: usa ADD COLUMN IF NOT EXISTS y DROP TRIGGER IF EXISTS,
--      por lo que NO daña los datos ni registros existentes.
--   3) Para la bitacora en triggers: la app debe fijar antes de operar:
--        SET @usuario_actual = 'admin';   -- nombre de usuario en sesion
--        SET @usuario_id     = 1;         -- id de usuarios
--      Si no se fija, el trigger registra 'Sistema' / 1 por defecto.
-- =============================================================================

USE invilara;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET FOREIGN_KEY_CHECKS = 0;

-- =============================================================================
-- 1) AJUSTES DE ESQUEMA
-- =============================================================================

-- 1.1) Normalizar tinyint(4) -> tinyint(1) (borrado logico coherente).
--      En el dump actual ya predomina tinyint(1); este bloque es defensivo.
--      (Ejecutar solo si existieran columnas tinyint(4) en sus tablas.)
-- ALTER TABLE alguna_tabla MODIFY alguna_columna TINYINT(1) NOT NULL DEFAULT 1;

-- 1.2) Agregar columna 'estado' (borrado logico 1=activo, 0=inactivo) a las
--      tablas fuertes que no la tienen. Es seguro y no afecta datos.
ALTER TABLE avance     ADD COLUMN IF NOT EXISTS estado TINYINT(1) NOT NULL DEFAULT 1;
ALTER TABLE comunidad  ADD COLUMN IF NOT EXISTS estado TINYINT(1) NOT NULL DEFAULT 1;
ALTER TABLE inspeccion ADD COLUMN IF NOT EXISTS estado TINYINT(1) NOT NULL DEFAULT 1;
ALTER TABLE institucion ADD COLUMN IF NOT EXISTS estado TINYINT(1) NOT NULL DEFAULT 1;
ALTER TABLE particular ADD COLUMN IF NOT EXISTS estado TINYINT(1) NOT NULL DEFAULT 1;
ALTER TABLE persona    ADD COLUMN IF NOT EXISTS estado TINYINT(1) NOT NULL DEFAULT 1;
ALTER TABLE prioridad  ADD COLUMN IF NOT EXISTS estado TINYINT(1) NOT NULL DEFAULT 1;
ALTER TABLE solicitudes ADD COLUMN IF NOT EXISTS estado TINYINT(1) NOT NULL DEFAULT 1;
ALTER TABLE obra       ADD COLUMN IF NOT EXISTS estado TINYINT(1) NOT NULL DEFAULT 1;

-- 1.3) semaforo: unificar el nombre de columna a 'estado' (varchar) segun esquema solicitado.
SET @col_est = (SELECT COLUMN_NAME FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA='invilara' AND TABLE_NAME='semaforo' AND COLUMN_NAME='estatus_semaforo');
SET @sql_est = IF(@col_est IS NOT NULL,
                  'ALTER TABLE semaforo CHANGE estatus_semaforo estado VARCHAR(20) NOT NULL',
                  'SELECT 1');
PREPARE stmt_est FROM @sql_est;
EXECUTE stmt_est;
DEALLOCATE PREPARE stmt_est;

-- 1.4) gravedad_obra.criticidad -> porcentaje decimal(3,2) entre 0 y 1.
--      Mapear textos existentes a porcentajes antes de cambiar el tipo.
UPDATE gravedad_obra
   SET criticidad = CASE
        WHEN criticidad LIKE '%Alt%' OR criticidad LIKE '%Crí%' OR criticidad LIKE '%Cri%' THEN '0.80'
        WHEN criticidad LIKE '%Med%' THEN '0.50'
        WHEN criticidad LIKE '%Baj%' OR criticidad LIKE '%Lev%' THEN '0.20'
        ELSE '0.00'
   END
 WHERE criticidad NOT REGEXP '^[0-9]+(\\.[0-9]+)?$';
ALTER TABLE gravedad_obra MODIFY criticidad DECIMAL(3,2) NOT NULL DEFAULT 0.00 COMMENT 'Porcentaje de criticidad 0.00 - 1.00';

-- 1.5) maquinaria: disponibilidad para el trigger de proyecto_maquinaria.
ALTER TABLE maquinaria ADD COLUMN IF NOT EXISTS disponibilidad VARCHAR(15) NOT NULL DEFAULT 'Disponible';

-- =============================================================================
-- 2) TRIGGERS - CAMBIAR DE ESTADO (SEMAFORO DE OBRA)
-- =============================================================================
DELIMITER //

DROP TRIGGER IF EXISTS trg_avance_ai_semaforo //
CREATE TRIGGER trg_avance_ai_semaforo
AFTER INSERT ON avance
FOR EACH ROW
BEGIN
  DECLARE v_pct INT DEFAULT NEW.porcentaje_avance;
  DECLARE v_dias INT DEFAULT DATEDIFF(NOW(), NEW.fecha_avance);
  DECLARE v_color VARCHAR(10) DEFAULT 'AMARILLO';
  DECLARE v_estado VARCHAR(20) DEFAULT 'En Ejecucion';
  IF v_pct >= 100 THEN
     SET v_color='VERDE'; SET v_estado='Culminado';
  ELSEIF v_dias > 30 THEN
     SET v_color='ROJO'; SET v_estado='Paralizado';
  END IF;
  UPDATE obra o
    JOIN semaforo s ON s.id_semaforo = o.semaforo_id_semaforo
    SET o.porcentaje_avance_obra = v_pct, s.color = v_color, s.estado = v_estado
  WHERE o.id_obra = NEW.obra_id_obra;
END //

DROP TRIGGER IF EXISTS trg_avance_au_semaforo //
CREATE TRIGGER trg_avance_au_semaforo
AFTER UPDATE ON avance
FOR EACH ROW
BEGIN
  DECLARE v_pct INT DEFAULT NEW.porcentaje_avance;
  DECLARE v_dias INT DEFAULT DATEDIFF(NOW(), NEW.fecha_avance);
  DECLARE v_color VARCHAR(10) DEFAULT 'AMARILLO';
  DECLARE v_estado VARCHAR(20) DEFAULT 'En Ejecucion';
  IF v_pct >= 100 THEN
     SET v_color='VERDE'; SET v_estado='Culminado';
  ELSEIF v_dias > 30 THEN
     SET v_color='ROJO'; SET v_estado='Paralizado';
  END IF;
  UPDATE obra o
    JOIN semaforo s ON s.id_semaforo = o.semaforo_id_semaforo
    SET o.porcentaje_avance_obra = v_pct, s.color = v_color, s.estado = v_estado
  WHERE o.id_obra = NEW.obra_id_obra;
END //

-- =============================================================================
-- 3) TRIGGERS - SOLICITUDES: Pendiente -> En Proceso al 1ra inspeccion tecnica
-- =============================================================================
DROP TRIGGER IF EXISTS trg_inspeccion_ai_solicitud //
CREATE TRIGGER trg_inspeccion_ai_solicitud
AFTER INSERT ON inspeccion
FOR EACH ROW
BEGIN
  UPDATE solicitudes s
    JOIN proyecto_has_solicitudes phs ON phs.solicitudes_id_solicitudes = s.id_solicitudes
    JOIN obra o ON o.gestionar_proyectos_codigo_proyecto = phs.proyecto_codigo_proyecto
    SET s.estatus_solicitud = 'En Proceso'
  WHERE o.id_obra = NEW.obra_id_obra1
    AND s.estatus_solicitud = 'Pendiente'
    AND s.estado = 1;
END //

-- =============================================================================
-- 4) TRIGGERS - AUDITORIA (BITACORA en invilara_seguridad)
--    Tablas fuertes: Empleados, Obras, Proyectos
-- =============================================================================

-- Empleados
DROP TRIGGER IF EXISTS trg_empleados_ai_bitacora //
CREATE TRIGGER trg_empleados_ai_bitacora
AFTER INSERT ON empleados
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora
    (usuario, id_modulo, modulo, accion, fecha, hora_inicio_sesion, hora_cierre_sesion, usuarios_id_usuarios)
  VALUES (COALESCE(@usuario_actual,'Sistema'), 0, 'Empleados', 'CREAR',
          NOW(), NOW(), NOW(), COALESCE(@usuario_id,1));
END //

DROP TRIGGER IF EXISTS trg_empleados_au_bitacora //
CREATE TRIGGER trg_empleados_au_bitacora
AFTER UPDATE ON empleados
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora
    (usuario, id_modulo, modulo, accion, fecha, hora_inicio_sesion, hora_cierre_sesion, usuarios_id_usuarios)
  VALUES (COALESCE(@usuario_actual,'Sistema'), 0, 'Empleados',
          IF(OLD.estado=1 AND NEW.estado=0,'ELIMINAR','EDITAR'),
          NOW(), NOW(), NOW(), COALESCE(@usuario_id,1));
END //

-- Obras
DROP TRIGGER IF EXISTS trg_obra_ai_bitacora //
CREATE TRIGGER trg_obra_ai_bitacora
AFTER INSERT ON obra
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora
    (usuario, id_modulo, modulo, accion, fecha, hora_inicio_sesion, hora_cierre_sesion, usuarios_id_usuarios)
  VALUES (COALESCE(@usuario_actual,'Sistema'), 0, 'Obras', 'CREAR',
          NOW(), NOW(), NOW(), COALESCE(@usuario_id,1));
END //

DROP TRIGGER IF EXISTS trg_obra_au_bitacora //
CREATE TRIGGER trg_obra_au_bitacora
AFTER UPDATE ON obra
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora
    (usuario, id_modulo, modulo, accion, fecha, hora_inicio_sesion, hora_cierre_sesion, usuarios_id_usuarios)
  VALUES (COALESCE(@usuario_actual,'Sistema'), 0, 'Obras',
          IF(OLD.estado=1 AND NEW.estado=0,'ELIMINAR','EDITAR'),
          NOW(), NOW(), NOW(), COALESCE(@usuario_id,1));
END //

-- Proyectos
DROP TRIGGER IF EXISTS trg_proyecto_ai_bitacora //
CREATE TRIGGER trg_proyecto_ai_bitacora
AFTER INSERT ON proyecto
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora
    (usuario, id_modulo, modulo, accion, fecha, hora_inicio_sesion, hora_cierre_sesion, usuarios_id_usuarios)
  VALUES (COALESCE(@usuario_actual,'Sistema'), 0, 'Proyectos', 'CREAR',
          NOW(), NOW(), NOW(), COALESCE(@usuario_id,1));
END //

DROP TRIGGER IF EXISTS trg_proyecto_au_bitacora //
CREATE TRIGGER trg_proyecto_au_bitacora
AFTER UPDATE ON proyecto
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora
    (usuario, id_modulo, modulo, accion, fecha, hora_inicio_sesion, hora_cierre_sesion, usuarios_id_usuarios)
  VALUES (COALESCE(@usuario_actual,'Sistema'), 0, 'Proyectos',
          IF(OLD.estado=1 AND NEW.estado=0,'ELIMINAR','EDITAR'),
          NOW(), NOW(), NOW(), COALESCE(@usuario_id,1));
END //

-- =============================================================================
-- 5) TRIGGER - PROYECTO / MAQUINARIA (disponibilidad = Ocupada al asignar)
-- =============================================================================
DROP TRIGGER IF EXISTS trg_phm_ai_maquina //
CREATE TRIGGER trg_phm_ai_maquina
AFTER INSERT ON proyecto_has_maquinaria
FOR EACH ROW
BEGIN
  UPDATE maquinaria SET disponibilidad = 'Ocupada'
  WHERE id_maquinaria = NEW.maquinaria_id_maquinaria AND estado = 1;
END //

-- =============================================================================
-- 6) TRIGGERS - VERIFICAR (INTEGRIDAD / SEGURIDAD)
-- =============================================================================

-- 6.1) Borrado fisico PROHIBIDO: los triggers BEFORE DELETE bloquean DELETE.
--      El borrado logico (UPDATE estado=0) ya lo hace la capa de la aplicacion.
DROP TRIGGER IF EXISTS trg_obra_bd_proteger //
CREATE TRIGGER trg_obra_bd_proteger
BEFORE DELETE ON obra
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado fisico prohibido en INVILARA. Use borrado logico (UPDATE estado=0).';
END //

DROP TRIGGER IF EXISTS trg_solicitudes_bd_proteger //
CREATE TRIGGER trg_solicitudes_bd_proteger
BEFORE DELETE ON solicitudes
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado fisico prohibido en INVILARA. Use borrado logico (UPDATE estado=0).';
END //

DROP TRIGGER IF EXISTS trg_prioridad_bd_proteger //
CREATE TRIGGER trg_prioridad_bd_proteger
BEFORE DELETE ON prioridad
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado fisico prohibido en INVILARA. Use borrado logico (UPDATE estado=0).';
END //

DROP TRIGGER IF EXISTS trg_avance_bd_proteger //
CREATE TRIGGER trg_avance_bd_proteger
BEFORE DELETE ON avance
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado fisico prohibido en INVILARA. Use borrado logico (UPDATE estado=0).';
END //

DROP TRIGGER IF EXISTS trg_empleados_bd_proteger //
CREATE TRIGGER trg_empleados_bd_proteger
BEFORE DELETE ON empleados
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado fisico prohibido en INVILARA. Use borrado logico (UPDATE estado=0).';
END //

DROP TRIGGER IF EXISTS trg_inspeccion_bd_proteger //
CREATE TRIGGER trg_inspeccion_bd_proteger
BEFORE DELETE ON inspeccion
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado fisico prohibido en INVILARA. Use borrado logico (UPDATE estado=0).';
END //

DROP TRIGGER IF EXISTS trg_gravedad_bd_proteger //
CREATE TRIGGER trg_gravedad_bd_proteger
BEFORE DELETE ON gravedad_obra
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado fisico prohibido en INVILARA. Use borrado logico (UPDATE estado=0).';
END //

DROP TRIGGER IF EXISTS trg_proyecto_bd_proteger //
CREATE TRIGGER trg_proyecto_bd_proteger
BEFORE DELETE ON proyecto
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado fisico prohibido en INVILARA. Use borrado logico (UPDATE estado=0).';
END //

-- 6.2) Consistencia en Tablas Catalogo: cargo del empleado debe existir y estar activo.
DROP TRIGGER IF EXISTS trg_empleados_bi_validar_cargo //
CREATE TRIGGER trg_empleados_bi_validar_cargo
BEFORE INSERT ON empleados
FOR EACH ROW
BEGIN
  IF NOT EXISTS (SELECT 1 FROM catalogo_cargos WHERE nombre_cargo = NEW.cargo AND estado = 1) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'El cargo no existe en el catalogo de cargos activos.';
  END IF;
END //

DROP TRIGGER IF EXISTS trg_empleados_bu_validar_cargo //
CREATE TRIGGER trg_empleados_bu_validar_cargo
BEFORE UPDATE ON empleados
FOR EACH ROW
BEGIN
  IF NOT EXISTS (SELECT 1 FROM catalogo_cargos WHERE nombre_cargo = NEW.cargo AND estado = 1) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'El cargo no existe en el catalogo de cargos activos.';
  END IF;
END //

-- 6.3) Control de Evidencias: maximo 5 imagenes por etapa (antes/durante/despues).
DROP TRIGGER IF EXISTS trg_informe_bi_evidencias //
CREATE TRIGGER trg_informe_bi_evidencias
BEFORE INSERT ON informe_avance_obra
FOR EACH ROW
BEGIN
  IF (CHAR_LENGTH(NEW.evidencia_antes)   - CHAR_LENGTH(REPLACE(NEW.evidencia_antes,',',''))   + IF(NEW.evidencia_antes='',0,1))   > 5
     OR (CHAR_LENGTH(NEW.evidencia_durante) - CHAR_LENGTH(REPLACE(NEW.evidencia_durante,',','')) + IF(NEW.evidencia_durante='',0,1)) > 5
     OR (CHAR_LENGTH(NEW.evidencia_despues) - CHAR_LENGTH(REPLACE(NEW.evidencia_despues,',','')) + IF(NEW.evidencia_despues='',0,1)) > 5
  THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Maximo 5 evidencias por etapa (antes/durante/despues).';
  END IF;
END //

DROP TRIGGER IF EXISTS trg_informe_bu_evidencias //
CREATE TRIGGER trg_informe_bu_evidencias
BEFORE UPDATE ON informe_avance_obra
FOR EACH ROW
BEGIN
  IF (CHAR_LENGTH(NEW.evidencia_antes)   - CHAR_LENGTH(REPLACE(NEW.evidencia_antes,',',''))   + IF(NEW.evidencia_antes='',0,1))   > 5
     OR (CHAR_LENGTH(NEW.evidencia_durante) - CHAR_LENGTH(REPLACE(NEW.evidencia_durante,',','')) + IF(NEW.evidencia_durante='',0,1)) > 5
     OR (CHAR_LENGTH(NEW.evidencia_despues) - CHAR_LENGTH(REPLACE(NEW.evidencia_despues,',','')) + IF(NEW.evidencia_despues='',0,1)) > 5
  THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Maximo 5 evidencias por etapa (antes/durante/despues).';
  END IF;
END //

DELIMITER ;

SET FOREIGN_KEY_CHECKS = 1;
-- =============================================================================
-- FIN DEL SCRIPT
-- =============================================================================
