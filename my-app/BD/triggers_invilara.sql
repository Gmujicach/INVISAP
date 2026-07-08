-- ============================================================================
--  PARTE 2 de 2  ->  BASE DE DATOS: invilara
--  Triggers de Cambiar Estado, Auditoría y Verificar.
--
--  IMPORTANTE:
--  * Ejecuta PRIMERO triggers_invilara_seguridad.sql (crea la BD de bitácora).
--  * Este script NO elimina, NO trunca y NO modifica registros existentes.
--  * Es idempotente (DROP TRIGGER IF EXISTS) y puede reejecutarse.
--  * Los triggers de auditoría escriben en invilara_seguridad.bitacora.
--  * La app puede setear @invilara_usuario_id (sesión); si no, queda en 0.
-- ============================================================================

USE invilara;

-- ============================================================================
--  1) TRIGGERS PARA "CAMBIAR DE ESTADO"  (Semáforo de Obra / Solicitudes)
-- ============================================================================

-- 1.1 Al INSERTAR un avance, inicializa el semáforo de la obra asociada.
DROP TRIGGER IF EXISTS trg_avance_inserta_semaforo;
DELIMITER $$
CREATE TRIGGER trg_avance_inserta_semaforo
AFTER INSERT ON avance
FOR EACH ROW
BEGIN
  IF NEW.porcentaje_avance >= 100 THEN
    UPDATE semaforo s
      JOIN obra o ON o.semaforo_id_semaforo = s.id_semaforo
      SET s.color = 'VERDE', s.estado = 'Culminado'
      WHERE o.id_obra = NEW.obra_id_obra;
  ELSE
    UPDATE semaforo s
      JOIN obra o ON o.semaforo_id_semaforo = s.id_semaforo
      SET s.color = 'AMARILLO', s.estado = 'En Proceso'
      WHERE o.id_obra = NEW.obra_id_obra;
  END IF;
END$$
DELIMITER ;

-- 1.2 Al ACTUALIZAR el porcentaje de avance, cambia el semáforo de la obra:
--     * 100%                 -> VERDE   (Culminado)
--     * sin avance > 30 días -> ROJO    (Paralizado)
--     * otro caso            -> AMARILLO (En Proceso)
DROP TRIGGER IF EXISTS trg_avance_cambia_semaforo;
DELIMITER $$
CREATE TRIGGER trg_avance_cambia_semaforo
AFTER UPDATE ON avance
FOR EACH ROW
BEGIN
  DECLARE dias_sin_avance INT DEFAULT 0;
  IF NEW.porcentaje_avance <> OLD.porcentaje_avance THEN
    SET dias_sin_avance = DATEDIFF(CURDATE(), NEW.fecha_avance);
    IF NEW.porcentaje_avance >= 100 THEN
      UPDATE semaforo s
        JOIN obra o ON o.semaforo_id_semaforo = s.id_semaforo
        SET s.color = 'VERDE', s.estado = 'Culminado'
        WHERE o.id_obra = NEW.obra_id_obra;
    ELSEIF dias_sin_avance > 30 THEN
      UPDATE semaforo s
        JOIN obra o ON o.semaforo_id_semaforo = s.id_semaforo
        SET s.color = 'ROJO', s.estado = 'Paralizado'
        WHERE o.id_obra = NEW.obra_id_obra;
    ELSE
      UPDATE semaforo s
        JOIN obra o ON o.semaforo_id_semaforo = s.id_semaforo
        SET s.color = 'AMARILLO', s.estado = 'En Proceso'
        WHERE o.id_obra = NEW.obra_id_obra;
    END IF;
  END IF;
END$$
DELIMITER ;

-- 1.3 Al registrar la PRIMERA inspección de una obra, la solicitud asociada
--     pasa de "Pendiente" a "En Proceso".
DROP TRIGGER IF EXISTS trg_inspeccion_cambia_solicitud;
DELIMITER $$
CREATE TRIGGER trg_inspeccion_cambia_solicitud
AFTER INSERT ON inspeccion
FOR EACH ROW
BEGIN
  UPDATE solicitudes s
    JOIN proyecto_has_solicitudes phs
      ON phs.solicitudes_id_solicitudes = s.id_solicitudes
    JOIN obra o
      ON o.gestionar_proyectos_codigo_proyecto = phs.proyecto_codigo_proyecto
    SET s.estatus_solicitud = 'En Proceso'
    WHERE o.id_obra = NEW.obra_id_obra1
      AND s.estatus_solicitud = 'Pendiente';
END$$
DELIMITER ;

-- ============================================================================
--  2) TRIGGERS PARA "ACTUALIZAR"  (Auditoría -> invilara_seguridad.bitacora)
--     Tablas fuertes: empleados, obra, proyecto  (INSERT / UPDATE / DELETE)
-- ============================================================================

-- ---- empleados ----
DROP TRIGGER IF EXISTS trg_empleados_ai;
DELIMITER $$
CREATE TRIGGER trg_empleados_ai AFTER INSERT ON empleados
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora (usuario_id, tabla, accion, descripcion, registro_id)
  VALUES (COALESCE(@invilara_usuario_id,0), 'empleados', 'INSERT',
          CONCAT('Creó empleado: ', NEW.nombre_empleado), NEW.id_empleados);
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_empleados_au;
DELIMITER $$
CREATE TRIGGER trg_empleados_au AFTER UPDATE ON empleados
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora (usuario_id, tabla, accion, descripcion, registro_id)
  VALUES (COALESCE(@invilara_usuario_id,0), 'empleados', 'UPDATE',
          CONCAT('Actualizó empleado ID: ', NEW.id_empleados, ' (', NEW.nombre_empleado, ')'), NEW.id_empleados);
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_empleados_ad;
DELIMITER $$
CREATE TRIGGER trg_empleados_ad AFTER DELETE ON empleados
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora (usuario_id, tabla, accion, descripcion, registro_id)
  VALUES (COALESCE(@invilara_usuario_id,0), 'empleados', 'DELETE',
          CONCAT('Eliminó (lógicamente) empleado ID: ', OLD.id_empleados), OLD.id_empleados);
END$$
DELIMITER ;

-- ---- obra ----
DROP TRIGGER IF EXISTS trg_obra_ai;
DELIMITER $$
CREATE TRIGGER trg_obra_ai AFTER INSERT ON obra
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora (usuario_id, tabla, accion, descripcion, registro_id)
  VALUES (COALESCE(@invilara_usuario_id,0), 'obra', 'INSERT',
          CONCAT('Creó obra: ', NEW.titulo_obra), NEW.id_obra);
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_obra_au;
DELIMITER $$
CREATE TRIGGER trg_obra_au AFTER UPDATE ON obra
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora (usuario_id, tabla, accion, descripcion, registro_id)
  VALUES (COALESCE(@invilara_usuario_id,0), 'obra', 'UPDATE',
          CONCAT('Actualizó obra ID: ', NEW.id_obra, ' (avance ', NEW.porcentaje_avance_obra, '%)'), NEW.id_obra);
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_obra_ad;
DELIMITER $$
CREATE TRIGGER trg_obra_ad AFTER DELETE ON obra
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora (usuario_id, tabla, accion, descripcion, registro_id)
  VALUES (COALESCE(@invilara_usuario_id,0), 'obra', 'DELETE',
          CONCAT('Eliminó (lógicamente) obra ID: ', OLD.id_obra), OLD.id_obra);
END$$
DELIMITER ;

-- ---- proyecto ----
DROP TRIGGER IF EXISTS trg_proyecto_ai;
DELIMITER $$
CREATE TRIGGER trg_proyecto_ai AFTER INSERT ON proyecto
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora (usuario_id, tabla, accion, descripcion, registro_id)
  VALUES (COALESCE(@invilara_usuario_id,0), 'proyecto', 'INSERT',
          CONCAT('Creó proyecto: ', NEW.codigo_proyecto), NEW.codigo_proyecto);
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_proyecto_au;
DELIMITER $$
CREATE TRIGGER trg_proyecto_au AFTER UPDATE ON proyecto
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora (usuario_id, tabla, accion, descripcion, registro_id)
  VALUES (COALESCE(@invilara_usuario_id,0), 'proyecto', 'UPDATE',
          CONCAT('Actualizó proyecto: ', NEW.codigo_proyecto), NEW.codigo_proyecto);
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_proyecto_ad;
DELIMITER $$
CREATE TRIGGER trg_proyecto_ad AFTER DELETE ON proyecto
FOR EACH ROW
BEGIN
  INSERT INTO invilara_seguridad.bitacora (usuario_id, tabla, accion, descripcion, registro_id)
  VALUES (COALESCE(@invilara_usuario_id,0), 'proyecto', 'DELETE',
          CONCAT('Eliminó (lógicamente) proyecto: ', OLD.codigo_proyecto), OLD.codigo_proyecto);
END$$
DELIMITER ;

-- ============================================================================
--  3) TRIGGERS PARA "VERIFICAR"  (Integridad y Seguridad)
-- ============================================================================

-- 3.1 CONVERSIÓN A BORRADO LÓGICO (borrado físico PROHIBIDO por el Prof. Escalona).
--     Cualquier DELETE sobre tablas fuertes es INTERCEPTADO y abortado.
DROP TRIGGER IF EXISTS trg_empleados_bd;
DELIMITER $$
CREATE TRIGGER trg_empleados_bd BEFORE DELETE ON empleados
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado físico prohibido en empleados: use borrado lógico (estado=0).';
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_obra_bd;
DELIMITER $$
CREATE TRIGGER trg_obra_bd BEFORE DELETE ON obra
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado físico prohibido en obra: use borrado lógico (estado=0).';
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_proyecto_bd;
DELIMITER $$
CREATE TRIGGER trg_proyecto_bd BEFORE DELETE ON proyecto
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado físico prohibido en proyecto: use borrado lógico (estado=0).';
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_solicitudes_bd;
DELIMITER $$
CREATE TRIGGER trg_solicitudes_bd BEFORE DELETE ON solicitudes
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado físico prohibido en solicitudes: use borrado lógico (estado=0).';
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_prioridad_bd;
DELIMITER $$
CREATE TRIGGER trg_prioridad_bd BEFORE DELETE ON prioridad
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado físico prohibido en prioridad: use borrado lógico (estado=0).';
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_gravedad_bd;
DELIMITER $$
CREATE TRIGGER trg_gravedad_bd BEFORE DELETE ON gravedad_obra
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Borrado físico prohibido en gravedad_obra: use borrado lógico (estado=0).';
END$$
DELIMITER ;

-- 3.2 CONSISTENCIA EN TABLAS CATÁLOGO.
--     Al asociar una gravedad a una prioridad, se verifica que exista y esté ACTIVA.
DROP TRIGGER IF EXISTS trg_gravedad_has_prioridad_bi;
DELIMITER $$
CREATE TRIGGER trg_gravedad_has_prioridad_bi BEFORE INSERT ON gravedad_obra_has_prioridad
FOR EACH ROW
BEGIN
  IF NOT EXISTS (
        SELECT 1 FROM gravedad_obra
        WHERE id_gravedad = NEW.gravedad_obra_id_gravedad AND estado = 1
  ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'La gravedad de obra seleccionada no existe o está inactiva.';
  END IF;
END$$
DELIMITER ;

-- 3.3 DISPONIBILIDAD DE MAQUINARIA.
--     Al asignar una maquinaria a un proyecto, se marca como OCUPADA (estado=0).
DROP TRIGGER IF EXISTS trg_proyecto_maquinaria_ocupa;
DELIMITER $$
CREATE TRIGGER trg_proyecto_maquinaria_ocupa AFTER INSERT ON proyecto_has_maquinaria
FOR EACH ROW
BEGIN
  UPDATE maquinaria
    SET estado = 0
    WHERE id_maquinaria = NEW.maquinaria_id_maquinaria;
END$$
DELIMITER ;

-- 3.4 CONTROL DE EVIDENCIAS (límite de imágenes por etapa/día).
DROP TRIGGER IF EXISTS trg_evidencia_limite;
DELIMITER $$
CREATE TRIGGER trg_evidencia_limite BEFORE INSERT ON evidencia
FOR EACH ROW
BEGIN
  IF (SELECT COUNT(*) FROM evidencia
        WHERE etapa = NEW.etapa
          AND DATE(fecha_registro) = DATE(NEW.fecha_registro)) >= 5 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Límite alcanzado: máximo 5 evidencias por etapa por día.';
  END IF;
END$$
DELIMITER ;

-- ============================================================================
--  FIN DE LOS TRIGGERS
--  Verificar:  SHOW TRIGGERS FROM invilara;
-- ============================================================================
