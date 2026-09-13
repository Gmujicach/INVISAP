-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 13-09-2026 a las 02:02:29
-- Versión del servidor: 9.4.0
-- Versión de PHP: 8.3.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `invilara`
--
CREATE DATABASE IF NOT EXISTS `invilara` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `invilara`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `avance`
--

CREATE TABLE `avance` (
  `id_avance` varchar(45) NOT NULL,
  `porcentaje_avance` int NOT NULL,
  `descripcion` text NOT NULL,
  `gerente` int NOT NULL,
  `fecha_avance` date NOT NULL,
  `obra_id_obra` int NOT NULL,
  `obra_estado` int NOT NULL,
  `obra_contratacion_id_contratacion` int NOT NULL,
  `obra_gestionar_proyectos_codigo_proyecto` varchar(15) NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `catalogo_cargos`
--

CREATE TABLE `catalogo_cargos` (
  `id_cargo` int NOT NULL,
  `nombre_cargo` varchar(45) NOT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catálogo de cargos institucionales';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `comunidad`
--

CREATE TABLE `comunidad` (
  `id_comunidad` int NOT NULL,
  `nombre_comunidad` varchar(100) NOT NULL,
  `ambito` varchar(45) NOT NULL,
  `sector` varchar(45) NOT NULL,
  `persona_id_persona` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `contratacion`
--

CREATE TABLE `contratacion` (
  `id_contratacion` int NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  `empresa_ganadora` varchar(30) NOT NULL,
  `numero_contrato` varchar(12) NOT NULL,
  `monto` varchar(20) NOT NULL,
  `fecha_inicio_procedimiento` datetime NOT NULL,
  `fecha_adjudicacion` datetime NOT NULL,
  `tipo_contrato` varchar(30) NOT NULL,
  `modalidad` varchar(30) NOT NULL,
  `objeto` varchar(30) NOT NULL,
  `observacion` varchar(100) NOT NULL,
  `fecha_registro` datetime NOT NULL,
  `empresa_rif` varchar(12) NOT NULL,
  `estado` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de contrataciones';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleados`
--

CREATE TABLE `empleados` (
  `id_empleados` int NOT NULL,
  `nombre_empleado` varchar(45) NOT NULL,
  `cargo` varchar(45) NOT NULL,
  `fecha_ingreso` date NOT NULL,
  `gerencia_asignada` varchar(45) NOT NULL,
  `persona_id_persona` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1' COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Disparadores `empleados`
--
DELIMITER $$
CREATE TRIGGER `trg_borrado_logico_empleados` BEFORE DELETE ON `empleados` FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000' 
    SET MESSAGE_TEXT = 'La eliminación física está prohibida. El sistema realizará un borrado lógico.';
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empresa`
--

CREATE TABLE `empresa` (
  `rif` varchar(12) NOT NULL,
  `nombre_empresa` varchar(80) NOT NULL,
  `telefono` varchar(12) NOT NULL COMMENT 'Tabla de empresas.',
  `domicilio_fiscal` varchar(100) NOT NULL,
  `estado` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `evidencia`
--

CREATE TABLE `evidencia` (
  `id_evidencia` int NOT NULL,
  `fotos` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `url_archivos` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `fecha_registro` datetime NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1' COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)',
  `etapa` enum('antes','durante','despues') NOT NULL DEFAULT 'antes' COMMENT 'Etapa de la evidencia fotográfica'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Disparadores `evidencia`
--
DELIMITER $$
CREATE TRIGGER `trg_limite_evidencias` BEFORE INSERT ON `evidencia` FOR EACH ROW BEGIN
    DECLARE total INT;
    SELECT COUNT(*) INTO total FROM evidencia WHERE estado = 1;
    IF total >= 50 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Límite de evidencias alcanzado (máximo 50).';
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gravedad_obra`
--

CREATE TABLE `gravedad_obra` (
  `id_gravedad` int NOT NULL,
  `nivel_gravedad` varchar(20) NOT NULL,
  `criticidad` varchar(10) NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1' COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gravedad_obra_has_prioridad`
--

CREATE TABLE `gravedad_obra_has_prioridad` (
  `gravedad_obra_id_gravedad` int NOT NULL,
  `prioridad_id_gestion_prioridad` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `informe_avance_obra`
--

CREATE TABLE `informe_avance_obra` (
  `id_informe` int NOT NULL,
  `fecha` datetime NOT NULL,
  `estado` varchar(25) NOT NULL,
  `poblacion_beneficiada` varchar(45) NOT NULL DEFAULT 'No especificado',
  `tipo_informe` varchar(30) NOT NULL,
  `evidencia_antes` varchar(255) NOT NULL DEFAULT '',
  `evidencia_durante` varchar(255) NOT NULL DEFAULT '',
  `evidencia_despues` varchar(255) NOT NULL DEFAULT '',
  `avance_id_avance` varchar(45) NOT NULL,
  `estado_registro` tinyint NOT NULL DEFAULT '1' COMMENT '1=Activo, 0=Inactivo (borrado lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de informes de avances de obras';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `inspeccion`
--

CREATE TABLE `inspeccion` (
  `id_inspeccion` int NOT NULL,
  `inspector` int NOT NULL,
  `fecha_inspeccion` date NOT NULL,
  `tipo_inspeccion` varchar(45) NOT NULL,
  `observaciones` varchar(255) NOT NULL,
  `obra_id_obra` int NOT NULL,
  `obra_estado` int NOT NULL,
  `obra_contratacion_id_contratacion` int NOT NULL,
  `obra_gestionar_proyectos_codigo_proyecto` varchar(15) NOT NULL,
  `obra_id_obra1` int NOT NULL,
  `obra_estado1` int NOT NULL,
  `obra_contratacion_id_contratacion1` int NOT NULL,
  `obra_gestionar_proyectos_codigo_proyecto1` varchar(15) NOT NULL,
  `evidencia_id_evidencia` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Disparadores `inspeccion`
--
DELIMITER $$
CREATE TRIGGER `trg_cambiar_estatus_solicitud` AFTER INSERT ON `inspeccion` FOR EACH ROW BEGIN
    -- 1. Sincronizar el estatus de la Solicitud a 'En Proceso'
    UPDATE `invilara`.`solicitudes`
    SET estatus_solicitud = 'En Proceso'
    WHERE id_solicitudes IN (
        SELECT solicitudes_id_solicitudes
        FROM `invilara`.`proyecto_has_solicitudes`
        WHERE proyecto_codigo_proyecto = NEW.obra_gestionar_proyectos_codigo_proyecto
    ) AND estatus_solicitud = 'Pendiente';

    -- 2. Sincronizar el estatus del Proyecto asociado a 'En Proceso'
    -- (Nota: Ajusta 'estatus_proyecto' al nombre exacto de tu columna en la tabla proyecto)
    UPDATE `invilara`.`proyecto`
    SET estatus_proyecto = 'En Proceso' 
    WHERE codigo_proyecto = NEW.obra_gestionar_proyectos_codigo_proyecto
      AND estatus_proyecto = 'Pendiente';

    -- 3. Sincronizar el estatus de la Obra asociada a 'En Proceso'
    -- (Nota: Ajusta 'estatus_obra' al nombre exacto de tu columna en la tabla obra)
    UPDATE `invilara`.`obra`
    SET estatus_obra = 'En Proceso' 
    WHERE gestionar_proyectos_codigo_proyecto = NEW.obra_gestionar_proyectos_codigo_proyecto
      AND estatus_obra = 'Pendiente';

END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `institucion`
--

CREATE TABLE `institucion` (
  `id_institucion` int NOT NULL,
  `nombre_representante` varchar(45) NOT NULL,
  `razon_social` varchar(120) NOT NULL,
  `persona_id_persona` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `maquinaria`
--

CREATE TABLE `maquinaria` (
  `id_maquinaria` int NOT NULL,
  `nombre_maquinaria` varchar(50) NOT NULL COMMENT 'Tabla de nombres de maquinarias',
  `tipo_maquinaria` varchar(45) NOT NULL,
  `estado` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `obra`
--

CREATE TABLE `obra` (
  `id_obra` int NOT NULL,
  `titulo_obra` varchar(45) NOT NULL,
  `ubicacion_obra` varchar(80) NOT NULL,
  `periodo_ejecucion` varchar(10) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `mediciones_obra` varchar(45) NOT NULL,
  `valuaciones` varchar(100) NOT NULL,
  `modificaciones_contrato` varchar(100) NOT NULL,
  `certificaciones_obras_ejecutadas` int NOT NULL,
  `numero_contrato` varchar(20) NOT NULL,
  `porcentaje_avance_obra` int NOT NULL,
  `estado` int NOT NULL,
  `contratacion_id_contratacion` int NOT NULL,
  `gestionar_proyectos_codigo_proyecto` varchar(15) NOT NULL,
  `activo` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de las inspecciones';

--
-- Disparadores `obra`
--
DELIMITER $$
CREATE TRIGGER `actualizar_semaforo_obra` BEFORE UPDATE ON `obra` FOR EACH ROW BEGIN
    IF NEW.porcentaje_avance_obra >= 100 THEN
        SET NEW.estado = 1; 
    ELSEIF NEW.porcentaje_avance_obra > 0 AND NEW.porcentaje_avance_obra < 100 THEN
        SET NEW.estado = 2; 
    ELSE
        SET NEW.estado = 3; 
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `particular`
--

CREATE TABLE `particular` (
  `id_particular` int NOT NULL,
  `nombre` varchar(45) NOT NULL,
  `apellido` varchar(45) NOT NULL,
  `persona_id_persona` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `persona`
--

CREATE TABLE `persona` (
  `id_persona` int NOT NULL,
  `cedula_persona` bigint NOT NULL,
  `direccion` varchar(200) NOT NULL,
  `parroquia` varchar(45) NOT NULL,
  `municipio` varchar(45) NOT NULL,
  `telefono` tinytext NOT NULL,
  `correo` varchar(45) NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prioridad`
--

CREATE TABLE `prioridad` (
  `id_gestion_prioridad` int NOT NULL,
  `rango_prioridad` float NOT NULL,
  `fecha_asignacion` datetime NOT NULL,
  `responsable_ajuste` varchar(30) NOT NULL,
  `justificacion_cambio` varchar(150) NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proyecto`
--

CREATE TABLE `proyecto` (
  `codigo_proyecto` varchar(15) NOT NULL,
  `fecha_planificacion` datetime NOT NULL,
  `descripcion_tecnica` varchar(200) NOT NULL,
  `computos_metricos` text NOT NULL,
  `estimacion_costo` varchar(45) NOT NULL,
  `proyecto_has_empleado` int DEFAULT NULL,
  `estado` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de gestion de proyectos';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proyecto_has_maquinaria`
--

CREATE TABLE `proyecto_has_maquinaria` (
  `proyecto_codigo_proyecto` varchar(15) NOT NULL,
  `maquinaria_id_maquinaria` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proyecto_has_solicitudes`
--

CREATE TABLE `proyecto_has_solicitudes` (
  `proyecto_codigo_proyecto` varchar(15) NOT NULL,
  `solicitudes_id_solicitudes` int NOT NULL,
  `solicitudes_persona_id_persona` int NOT NULL,
  `solicitudes_prioridad_id_gestion_prioridad` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `publicacion`
--

CREATE TABLE `publicacion` (
  `id_publicacion` int NOT NULL,
  `titulo_publicacion` varchar(150) NOT NULL,
  `nombre_responsable` varchar(45) NOT NULL,
  `tipo_publicacion` varchar(15) NOT NULL,
  `fecha_publicacion` datetime NOT NULL COMMENT 'Tabla de gestion de publicaciones',
  `informe_avance_obra_id_informe` int NOT NULL,
  `cuerpo_publicacion` text,
  `estado` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recurso_obra`
--

CREATE TABLE `recurso_obra` (
  `id_recurso` int NOT NULL,
  `descripcion_material` varchar(45) NOT NULL,
  `cantidad_material` decimal(5,2) NOT NULL,
  `unidad_material` varchar(20) NOT NULL,
  `informe_avance_obra_id_informe` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reporte`
--

CREATE TABLE `reporte` (
  `id_reporte` int NOT NULL,
  `fecha` datetime NOT NULL,
  `ubicacion` varchar(255) NOT NULL,
  `solicitudes_pendientes` int NOT NULL,
  `solicitudes_procesadas` int NOT NULL,
  `cantidad_total_solicitudes` int NOT NULL,
  `cantidad_comunidades_atendidas` int NOT NULL,
  `informe_avance_obra_id_informe` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `semaforo`
--

CREATE TABLE `semaforo` (
  `id_semaforo` int NOT NULL,
  `estado` varchar(20) NOT NULL,
  `color` enum('VERDE','AMARILLO','ROJO') NOT NULL,
  `descripcion` varchar(50) NOT NULL,
  `estado_registro` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `semaforo`
--

INSERT INTO `semaforo` (`id_semaforo`, `estado`, `color`, `descripcion`, `estado_registro`) VALUES
(1, '', 'VERDE', 'Obra finalizada (100% de avance)', 0),
(2, '', 'AMARILLO', 'Obra en ejecución o en proceso (Avance mayor a 0% ', 0),
(3, '', 'ROJO', 'Obra pendiente o sin iniciar (0% de avance)', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `solicitudes`
--

CREATE TABLE `solicitudes` (
  `id_solicitudes` int NOT NULL,
  `fecha` datetime NOT NULL,
  `tipo_solicitud` varchar(45) NOT NULL,
  `estatus_solicitud` varchar(15) NOT NULL,
  `problematica` varchar(255) NOT NULL,
  `persona_id_persona` int NOT NULL,
  `prioridad_id_gestion_prioridad` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla general de las solicitudes';

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_evidencia_informe`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `vista_evidencia_informe` (
`id_evidencia` int
,`fotos` varchar(255)
,`url_archivos` varchar(255)
,`fecha_registro` datetime
,`etapa` enum('antes','durante','despues')
,`estado` tinyint
,`id_informe` int
,`fecha_informe` datetime
,`tipo_informe` varchar(30)
,`estado_informe` varchar(25)
);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `avance`
--
ALTER TABLE `avance`
  ADD PRIMARY KEY (`id_avance`),
  ADD KEY `fk_avance_obra1_idx` (`obra_id_obra`,`obra_estado`,`obra_contratacion_id_contratacion`,`obra_gestionar_proyectos_codigo_proyecto`),
  ADD KEY `fk_avance_empleado1_idx` (`gerente`);

--
-- Indices de la tabla `catalogo_cargos`
--
ALTER TABLE `catalogo_cargos`
  ADD PRIMARY KEY (`id_cargo`),
  ADD UNIQUE KEY `nombre_cargo_UNIQUE` (`nombre_cargo`);

--
-- Indices de la tabla `comunidad`
--
ALTER TABLE `comunidad`
  ADD PRIMARY KEY (`id_comunidad`,`persona_id_persona`),
  ADD KEY `fk_comunidad_persona1_idx` (`persona_id_persona`);

--
-- Indices de la tabla `contratacion`
--
ALTER TABLE `contratacion`
  ADD PRIMARY KEY (`id_contratacion`),
  ADD UNIQUE KEY `numero_contrato_UNIQUE` (`numero_contrato`),
  ADD KEY `fk_contratacion_empresa1_idx` (`empresa_rif`);

--
-- Indices de la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD PRIMARY KEY (`id_empleados`),
  ADD KEY `fk_empleados_persona1_idx` (`persona_id_persona`),
  ADD KEY `idx_empleados_estado` (`estado`),
  ADD KEY `idx_empleados_cargo` (`cargo`);

--
-- Indices de la tabla `empresa`
--
ALTER TABLE `empresa`
  ADD PRIMARY KEY (`rif`),
  ADD UNIQUE KEY `rif_UNIQUE` (`rif`);

--
-- Indices de la tabla `evidencia`
--
ALTER TABLE `evidencia`
  ADD PRIMARY KEY (`id_evidencia`);

--
-- Indices de la tabla `gravedad_obra`
--
ALTER TABLE `gravedad_obra`
  ADD PRIMARY KEY (`id_gravedad`);

--
-- Indices de la tabla `gravedad_obra_has_prioridad`
--
ALTER TABLE `gravedad_obra_has_prioridad`
  ADD PRIMARY KEY (`gravedad_obra_id_gravedad`,`prioridad_id_gestion_prioridad`),
  ADD KEY `fk_gravedad_obra_has_prioridad_prioridad1_idx` (`prioridad_id_gestion_prioridad`),
  ADD KEY `fk_gravedad_obra_has_prioridad_gravedad_obra1_idx` (`gravedad_obra_id_gravedad`);

--
-- Indices de la tabla `informe_avance_obra`
--
ALTER TABLE `informe_avance_obra`
  ADD PRIMARY KEY (`id_informe`),
  ADD KEY `fk_informe_avance_obra_avance1_idx` (`avance_id_avance`),
  ADD KEY `idx_informe_estado_registro` (`estado_registro`);

--
-- Indices de la tabla `inspeccion`
--
ALTER TABLE `inspeccion`
  ADD PRIMARY KEY (`id_inspeccion`,`evidencia_id_evidencia`),
  ADD KEY `fk_inspeccion_obra1_idx` (`obra_id_obra1`,`obra_estado1`,`obra_contratacion_id_contratacion1`,`obra_gestionar_proyectos_codigo_proyecto1`),
  ADD KEY `fk_inspeccion_evidencia1_idx` (`evidencia_id_evidencia`),
  ADD KEY `fk_inspeccion_empleado1_idx` (`inspector`);

--
-- Indices de la tabla `institucion`
--
ALTER TABLE `institucion`
  ADD PRIMARY KEY (`id_institucion`,`persona_id_persona`),
  ADD KEY `fk_institucion_persona1_idx` (`persona_id_persona`);

--
-- Indices de la tabla `maquinaria`
--
ALTER TABLE `maquinaria`
  ADD PRIMARY KEY (`id_maquinaria`);

--
-- Indices de la tabla `obra`
--
ALTER TABLE `obra`
  ADD UNIQUE KEY `id_obra_UNIQUE` (`id_obra`),
  ADD KEY `fk_obra_contratacion1_idx` (`contratacion_id_contratacion`),
  ADD KEY `fk_obra_gestionar_proyectos1_idx` (`gestionar_proyectos_codigo_proyecto`),
  ADD KEY `idx_obra_estado` (`estado`);

--
-- Indices de la tabla `particular`
--
ALTER TABLE `particular`
  ADD PRIMARY KEY (`id_particular`,`persona_id_persona`),
  ADD KEY `fk_particular_persona1_idx` (`persona_id_persona`);

--
-- Indices de la tabla `persona`
--
ALTER TABLE `persona`
  ADD PRIMARY KEY (`id_persona`),
  ADD UNIQUE KEY `cedula_persona_UNIQUE` (`cedula_persona`);

--
-- Indices de la tabla `prioridad`
--
ALTER TABLE `prioridad`
  ADD PRIMARY KEY (`id_gestion_prioridad`);

--
-- Indices de la tabla `proyecto`
--
ALTER TABLE `proyecto`
  ADD PRIMARY KEY (`codigo_proyecto`),
  ADD UNIQUE KEY `codigo_proyecto_UNIQUE` (`codigo_proyecto`),
  ADD KEY `fk_proyecto_empleado1_idx` (`proyecto_has_empleado`);

--
-- Indices de la tabla `proyecto_has_maquinaria`
--
ALTER TABLE `proyecto_has_maquinaria`
  ADD PRIMARY KEY (`proyecto_codigo_proyecto`,`maquinaria_id_maquinaria`),
  ADD KEY `fk_proyecto_has_maquinaria_maquinaria1_idx` (`maquinaria_id_maquinaria`),
  ADD KEY `fk_proyecto_has_maquinaria_proyecto1_idx` (`proyecto_codigo_proyecto`);

--
-- Indices de la tabla `proyecto_has_solicitudes`
--
ALTER TABLE `proyecto_has_solicitudes`
  ADD PRIMARY KEY (`proyecto_codigo_proyecto`,`solicitudes_id_solicitudes`,`solicitudes_persona_id_persona`,`solicitudes_prioridad_id_gestion_prioridad`),
  ADD KEY `fk_proyecto_has_solicitudes_solicitudes1_idx` (`solicitudes_id_solicitudes`,`solicitudes_persona_id_persona`,`solicitudes_prioridad_id_gestion_prioridad`),
  ADD KEY `fk_proyecto_has_solicitudes_proyecto1_idx` (`proyecto_codigo_proyecto`);

--
-- Indices de la tabla `publicacion`
--
ALTER TABLE `publicacion`
  ADD PRIMARY KEY (`id_publicacion`),
  ADD KEY `fk_publicacion_informe_avance_obra1_idx` (`informe_avance_obra_id_informe`);

--
-- Indices de la tabla `recurso_obra`
--
ALTER TABLE `recurso_obra`
  ADD PRIMARY KEY (`id_recurso`),
  ADD KEY `fk_recurso_obra_informe_avance_obra1_idx` (`informe_avance_obra_id_informe`);

--
-- Indices de la tabla `reporte`
--
ALTER TABLE `reporte`
  ADD PRIMARY KEY (`id_reporte`),
  ADD KEY `fk_reporte_informe_avance_obra1_idx` (`informe_avance_obra_id_informe`);

--
-- Indices de la tabla `semaforo`
--
ALTER TABLE `semaforo`
  ADD PRIMARY KEY (`id_semaforo`);

--
-- Indices de la tabla `solicitudes`
--
ALTER TABLE `solicitudes`
  ADD PRIMARY KEY (`id_solicitudes`,`persona_id_persona`,`prioridad_id_gestion_prioridad`),
  ADD KEY `fk_solicitudes_persona1_idx` (`persona_id_persona`),
  ADD KEY `fk_solicitudes_prioridad1_idx` (`prioridad_id_gestion_prioridad`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `catalogo_cargos`
--
ALTER TABLE `catalogo_cargos`
  MODIFY `id_cargo` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `comunidad`
--
ALTER TABLE `comunidad`
  MODIFY `id_comunidad` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `contratacion`
--
ALTER TABLE `contratacion`
  MODIFY `id_contratacion` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `empleados`
--
ALTER TABLE `empleados`
  MODIFY `id_empleados` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `evidencia`
--
ALTER TABLE `evidencia`
  MODIFY `id_evidencia` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `gravedad_obra`
--
ALTER TABLE `gravedad_obra`
  MODIFY `id_gravedad` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `informe_avance_obra`
--
ALTER TABLE `informe_avance_obra`
  MODIFY `id_informe` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `inspeccion`
--
ALTER TABLE `inspeccion`
  MODIFY `id_inspeccion` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `institucion`
--
ALTER TABLE `institucion`
  MODIFY `id_institucion` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `maquinaria`
--
ALTER TABLE `maquinaria`
  MODIFY `id_maquinaria` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `obra`
--
ALTER TABLE `obra`
  MODIFY `id_obra` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `particular`
--
ALTER TABLE `particular`
  MODIFY `id_particular` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `persona`
--
ALTER TABLE `persona`
  MODIFY `id_persona` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `prioridad`
--
ALTER TABLE `prioridad`
  MODIFY `id_gestion_prioridad` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `publicacion`
--
ALTER TABLE `publicacion`
  MODIFY `id_publicacion` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reporte`
--
ALTER TABLE `reporte`
  MODIFY `id_reporte` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `semaforo`
--
ALTER TABLE `semaforo`
  MODIFY `id_semaforo` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `solicitudes`
--
ALTER TABLE `solicitudes`
  MODIFY `id_solicitudes` int NOT NULL AUTO_INCREMENT;

-- --------------------------------------------------------

--
-- Estructura para la vista `vista_evidencia_informe`
--
DROP TABLE IF EXISTS `vista_evidencia_informe`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_evidencia_informe`  AS SELECT `e`.`id_evidencia` AS `id_evidencia`, `e`.`fotos` AS `fotos`, `e`.`url_archivos` AS `url_archivos`, `e`.`fecha_registro` AS `fecha_registro`, `e`.`etapa` AS `etapa`, `e`.`estado` AS `estado`, `i`.`id_informe` AS `id_informe`, `i`.`fecha` AS `fecha_informe`, `i`.`tipo_informe` AS `tipo_informe`, `i`.`estado` AS `estado_informe` FROM (`evidencia` `e` left join `informe_avance_obra` `i` on((((`e`.`etapa` = 'antes') and (`i`.`evidencia_antes` like concat('%',`e`.`id_evidencia`,'%'))) or ((`e`.`etapa` = 'durante') and (`i`.`evidencia_durante` like concat('%',`e`.`id_evidencia`,'%'))) or ((`e`.`etapa` = 'despues') and (`i`.`evidencia_despues` like concat('%',`e`.`id_evidencia`,'%')))))) WHERE (`e`.`estado` = 1) ;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `avance`
--
ALTER TABLE `avance`
  ADD CONSTRAINT `fk_avance_empleado1` FOREIGN KEY (`gerente`) REFERENCES `empleados` (`id_empleados`);

--
-- Filtros para la tabla `comunidad`
--
ALTER TABLE `comunidad`
  ADD CONSTRAINT `fk_comunidad_persona1` FOREIGN KEY (`persona_id_persona`) REFERENCES `persona` (`id_persona`);

--
-- Filtros para la tabla `contratacion`
--
ALTER TABLE `contratacion`
  ADD CONSTRAINT `fk_contratacion_empresa1` FOREIGN KEY (`empresa_rif`) REFERENCES `empresa` (`rif`);

--
-- Filtros para la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD CONSTRAINT `fk_empleados_persona1` FOREIGN KEY (`persona_id_persona`) REFERENCES `persona` (`id_persona`);

--
-- Filtros para la tabla `gravedad_obra_has_prioridad`
--
ALTER TABLE `gravedad_obra_has_prioridad`
  ADD CONSTRAINT `fk_gravedad_obra_has_prioridad_gravedad_obra1` FOREIGN KEY (`gravedad_obra_id_gravedad`) REFERENCES `gravedad_obra` (`id_gravedad`),
  ADD CONSTRAINT `fk_gravedad_obra_has_prioridad_prioridad1` FOREIGN KEY (`prioridad_id_gestion_prioridad`) REFERENCES `prioridad` (`id_gestion_prioridad`);

--
-- Filtros para la tabla `informe_avance_obra`
--
ALTER TABLE `informe_avance_obra`
  ADD CONSTRAINT `fk_informe_avance_obra_avance1` FOREIGN KEY (`avance_id_avance`) REFERENCES `avance` (`id_avance`);

--
-- Filtros para la tabla `inspeccion`
--
ALTER TABLE `inspeccion`
  ADD CONSTRAINT `fk_inspeccion_empleado1` FOREIGN KEY (`inspector`) REFERENCES `empleados` (`id_empleados`),
  ADD CONSTRAINT `fk_inspeccion_evidencia1` FOREIGN KEY (`evidencia_id_evidencia`) REFERENCES `evidencia` (`id_evidencia`);

--
-- Filtros para la tabla `institucion`
--
ALTER TABLE `institucion`
  ADD CONSTRAINT `fk_institucion_persona1` FOREIGN KEY (`persona_id_persona`) REFERENCES `persona` (`id_persona`);

--
-- Filtros para la tabla `obra`
--
ALTER TABLE `obra`
  ADD CONSTRAINT `fk_obra_contratacion1` FOREIGN KEY (`contratacion_id_contratacion`) REFERENCES `contratacion` (`id_contratacion`),
  ADD CONSTRAINT `fk_obra_estado` FOREIGN KEY (`estado`) REFERENCES `semaforo` (`id_semaforo`),
  ADD CONSTRAINT `fk_obra_gestionar_proyectos1` FOREIGN KEY (`gestionar_proyectos_codigo_proyecto`) REFERENCES `proyecto` (`codigo_proyecto`);

--
-- Filtros para la tabla `particular`
--
ALTER TABLE `particular`
  ADD CONSTRAINT `fk_particular_persona1` FOREIGN KEY (`persona_id_persona`) REFERENCES `persona` (`id_persona`);

--
-- Filtros para la tabla `proyecto`
--
ALTER TABLE `proyecto`
  ADD CONSTRAINT `fk_proyecto_empleado1` FOREIGN KEY (`proyecto_has_empleado`) REFERENCES `empleados` (`id_empleados`);

--
-- Filtros para la tabla `proyecto_has_maquinaria`
--
ALTER TABLE `proyecto_has_maquinaria`
  ADD CONSTRAINT `fk_proyecto_has_maquinaria_maquinaria1` FOREIGN KEY (`maquinaria_id_maquinaria`) REFERENCES `maquinaria` (`id_maquinaria`),
  ADD CONSTRAINT `fk_proyecto_has_maquinaria_proyecto1` FOREIGN KEY (`proyecto_codigo_proyecto`) REFERENCES `proyecto` (`codigo_proyecto`);

--
-- Filtros para la tabla `proyecto_has_solicitudes`
--
ALTER TABLE `proyecto_has_solicitudes`
  ADD CONSTRAINT `fk_proyecto_has_solicitudes_proyecto1` FOREIGN KEY (`proyecto_codigo_proyecto`) REFERENCES `proyecto` (`codigo_proyecto`),
  ADD CONSTRAINT `fk_proyecto_has_solicitudes_solicitudes1` FOREIGN KEY (`solicitudes_id_solicitudes`,`solicitudes_persona_id_persona`,`solicitudes_prioridad_id_gestion_prioridad`) REFERENCES `solicitudes` (`id_solicitudes`, `persona_id_persona`, `prioridad_id_gestion_prioridad`);

--
-- Filtros para la tabla `publicacion`
--
ALTER TABLE `publicacion`
  ADD CONSTRAINT `fk_publicacion_informe_avance_obra1` FOREIGN KEY (`informe_avance_obra_id_informe`) REFERENCES `informe_avance_obra` (`id_informe`);

--
-- Filtros para la tabla `recurso_obra`
--
ALTER TABLE `recurso_obra`
  ADD CONSTRAINT `fk_recurso_obra_informe_avance_obra1` FOREIGN KEY (`informe_avance_obra_id_informe`) REFERENCES `informe_avance_obra` (`id_informe`);

--
-- Filtros para la tabla `reporte`
--
ALTER TABLE `reporte`
  ADD CONSTRAINT `fk_reporte_informe_avance_obra1` FOREIGN KEY (`informe_avance_obra_id_informe`) REFERENCES `informe_avance_obra` (`id_informe`);

--
-- Filtros para la tabla `solicitudes`
--
ALTER TABLE `solicitudes`
  ADD CONSTRAINT `fk_solicitudes_persona1` FOREIGN KEY (`persona_id_persona`) REFERENCES `persona` (`id_persona`),
  ADD CONSTRAINT `fk_solicitudes_prioridad1` FOREIGN KEY (`prioridad_id_gestion_prioridad`) REFERENCES `prioridad` (`id_gestion_prioridad`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
