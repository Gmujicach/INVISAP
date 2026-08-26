/* ============================================================
   Migración: Agregar columna cumple_requisitos a la tabla empresa
   Descripción: Marca si una empresa cumple con todos los
               requisitos legales. Solo las empresas marcadas
               aparecerán en el modal de selección de empresas
               al registrar una nueva contratación.
   Fecha: 2026-08-26
   ============================================================ */

-- Agregar la columna (idempotente: solo si no existe)
SET @columna_existe = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME   = 'empresa'
      AND COLUMN_NAME  = 'cumple_requisitos'
);

SET @sql = IF(
    @columna_existe = 0,
    'ALTER TABLE `empresa` ADD COLUMN `cumple_requisitos` TINYINT(1) NOT NULL DEFAULT 0',
    'SELECT "La columna cumple_requisitos ya existe" AS mensaje'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Las empresas existentes quedan con cumple_requisitos = 0 por defecto.
-- Para marcar una empresa como que cumple requisitos legales, ejecutar:
--   UPDATE empresa SET cumple_requisitos = 1 WHERE rif = 'J-XXXXXXXXX';
