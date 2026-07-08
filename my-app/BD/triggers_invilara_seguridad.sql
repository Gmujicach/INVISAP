-- ============================================================================
--  PARTE 1 de 2  ->  BASE DE DATOS: invilara_seguridad
--  (Bitácora de auditoría alimentada por los triggers de invilara)
--
--  Ejecuta este script PRIMERO, seleccionando la base de datos
--  "invilara_seguridad" (o con permisos de creación de BD) en phpMyAdmin / MySQL.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS invilara_seguridad
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE invilara_seguridad;

CREATE TABLE IF NOT EXISTS bitacora (
  id_bitacora     INT          NOT NULL AUTO_INCREMENT,
  fecha_hora      DATETIME     DEFAULT CURRENT_TIMESTAMP,
  usuario_id      INT          NULL,
  tabla           VARCHAR(50)  NOT NULL,
  accion          VARCHAR(20)  NOT NULL,
  descripcion     TEXT,
  registro_id     VARCHAR(45),
  PRIMARY KEY (id_bitacora),
  KEY idx_bitacora_tabla (tabla),
  KEY idx_bitacora_fecha (fecha_hora)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Bitácora de seguridad alimentada por triggers (INVILARA)';

-- Fin Parte 1.
-- Ahora ejecuta la Parte 2 (triggers_invilara.sql) en la base de datos "invilara".
