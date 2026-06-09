-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 09-06-2026 a las 21:10:37
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

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleados`
--

CREATE TABLE `empleados` (
  `id_empleados` int NOT NULL,
  `nombre_gerente` varchar(45) NOT NULL,
  `cedula_gerente` varchar(10) NOT NULL,
  `telefono_gerente` varchar(12) NOT NULL,
  `direccion_gerente` varchar(100) NOT NULL,
  `correo_gerente` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empresa`
--

CREATE TABLE `empresa` (
  `rif` varchar(12) NOT NULL,
  `nombre_empresa` varchar(80) NOT NULL,
  `telefono` varchar(12) NOT NULL COMMENT 'Tabla de empresas.',
  `domicilio_fiscal` varchar(100) NOT NULL,
  `gestionar_proyectos_id_proyectos` int NOT NULL,
  `gestionar_proyectos_maquinaria_id_maquinaria` int NOT NULL,
  `gestionar_obra_id_inspeccion` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gerencias`
--

CREATE TABLE `gerencias` (
  `id_gerencias` int NOT NULL,
  `nombre_gerencia` varchar(45) NOT NULL,
  `direccion_gerencia` varchar(45) NOT NULL,
  `informe_avance_obra_id_informe` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de las gerencias';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gerencias_has_empleados`
--

CREATE TABLE `gerencias_has_empleados` (
  `gerencias_id_gerencias` int NOT NULL,
  `empleados_id_empleados` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gerencias_has_gestionar_prioridad`
--

CREATE TABLE `gerencias_has_gestionar_prioridad` (
  `gerencias_id_gerencias` int NOT NULL,
  `gerencias_informe_avance_obra_id_informe` int NOT NULL,
  `gestionar_prioridad_id_gestion_prioridad` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gestionar_contrataciones`
--

CREATE TABLE `gestionar_contrataciones` (
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
  `gestionar_proyectos_id_proyectos` int NOT NULL,
  `gestionar_proyectos_maquinaria_id_maquinaria` int NOT NULL,
  `empresa_rif` varchar(12) NOT NULL,
  `empresa_gestionar_proyectos_id_proyectos` int NOT NULL,
  `empresa_gestionar_proyectos_maquinaria_id_maquinaria` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de contrataciones';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gestionar_gravedad`
--

CREATE TABLE `gestionar_gravedad` (
  `id_gravedad` int NOT NULL,
  `nivel_gravedad` varchar(20) NOT NULL,
  `criticidad` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gestionar_obra`
--

CREATE TABLE `gestionar_obra` (
  `id_inspeccion` int NOT NULL,
  `nombre_ing_insp` varchar(45) NOT NULL,
  `periodo_ejecucion` int NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `mediciones_obra` varchar(45) NOT NULL,
  `valuaciones` varchar(100) NOT NULL,
  `modificaciones_contrato` varchar(100) NOT NULL,
  `certificaciones_obras_ejecutadas` int NOT NULL,
  `numero_contrato` varchar(20) NOT NULL,
  `porcentaje_avance_obra` int NOT NULL,
  `inspectores_id_inspector` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de las inspecciones';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gestionar_prioridad`
--

CREATE TABLE `gestionar_prioridad` (
  `id_gestion_prioridad` int NOT NULL,
  `rango_prioridad` float NOT NULL,
  `fecha_asignacion` datetime NOT NULL,
  `responsable_ajuste` varchar(30) NOT NULL,
  `justificacion_cambio` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gestionar_proyectos`
--

CREATE TABLE `gestionar_proyectos` (
  `id_proyectos` int NOT NULL,
  `codigo_proyecto` varchar(15) NOT NULL,
  `fecha_planificacion` datetime NOT NULL,
  `descripcion_tecnica` varchar(200) NOT NULL,
  `computos_metricos` varchar(255) NOT NULL,
  `estimacion_costo_proyecto` varchar(45) NOT NULL,
  `inspecciones_previas` varchar(255) NOT NULL,
  `maquinaria_id_maquinaria` int NOT NULL,
  `gerencias_id_gerencias` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de gestion de proyectos';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gestionar_publicaciones`
--

CREATE TABLE `gestionar_publicaciones` (
  `id_publicaciones` int NOT NULL,
  `titulo_publicacion` varchar(150) NOT NULL,
  `nombre_responsable` varchar(45) NOT NULL,
  `tipo_publicacion` varchar(15) NOT NULL,
  `fecha_publicacion` datetime NOT NULL COMMENT 'Tabla de gestion de publicaciones'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gestionar_solicitudes`
--

CREATE TABLE `gestionar_solicitudes` (
  `id_solicitud` int NOT NULL,
  `fecha` datetime NOT NULL,
  `telefono_solicitante` varchar(12) NOT NULL,
  `direccion_solicitante` varchar(100) NOT NULL,
  `tipo_solicitud` varchar(45) NOT NULL,
  `estatus_solicitud` varchar(15) NOT NULL,
  `problematica` varchar(255) NOT NULL,
  `tipo_solicitante` varchar(45) NOT NULL,
  `solicitante_id_comunidad` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla general de las solicitudes';

--
-- Volcado de datos para la tabla `gestionar_solicitudes`
--

INSERT INTO `gestionar_solicitudes` (`id_solicitud`, `fecha`, `telefono_solicitante`, `direccion_solicitante`, `tipo_solicitud`, `estatus_solicitud`, `problematica`, `tipo_solicitante`, `solicitante_id_comunidad`) VALUES
(1, '2026-06-09 01:05:00', '04123456789', 'Iribarren', 'Comunidad', 'PENDIENTE', 'Bache entre Carrera 7A con Calle 6b', 'Comunidad', 1),
(2, '2026-06-09 12:50:00', '02513353950', 'Caja de Agua', 'Institucion', 'PENDIENTE', 'Pongan la luz nojoda mamaguevos', 'Institucion', 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `informe_avance_obra`
--

CREATE TABLE `informe_avance_obra` (
  `id_informe` int NOT NULL,
  `fecha` datetime NOT NULL,
  `tipo_obras` varchar(25) NOT NULL,
  `estado` varchar(25) NOT NULL,
  `recurso` int NOT NULL,
  `poblacion_benefiada` varchar(45) NOT NULL,
  `logros` varchar(45) NOT NULL,
  `tipo_informe` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de informes de avances de obras';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `informe_avance_obra_has_gestionar_publicaciones`
--

CREATE TABLE `informe_avance_obra_has_gestionar_publicaciones` (
  `informe_avance_obra_id_informe` int NOT NULL,
  `gestionar_publicaciones_id_publicaciones` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `inspectores`
--

CREATE TABLE `inspectores` (
  `id_inspector` int NOT NULL,
  `nombre_inspector` varchar(45) NOT NULL,
  `cedula` varchar(10) NOT NULL,
  `telefono_inspector` varchar(12) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `maquinaria`
--

CREATE TABLE `maquinaria` (
  `id_maquinaria` int NOT NULL,
  `nombre_maquinaria` varchar(50) NOT NULL COMMENT 'Tabla de nombres de maquinarias'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `priorizar_solicitudes`
--

CREATE TABLE `priorizar_solicitudes` (
  `id_priorizacion` int NOT NULL,
  `analisis_narrativo_ia` varchar(255) NOT NULL,
  `prioridad_calculada` float NOT NULL,
  `estatus` varchar(15) NOT NULL,
  `fecha_procesamiento` datetime NOT NULL,
  `gestionar_prioridad_id_gestion_prioridad` int NOT NULL,
  `gestionar_gravedad_id_gravedad` int NOT NULL,
  `gestionar_solicitudes_id_solicitud` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reporte`
--

CREATE TABLE `reporte` (
  `id_reporte` int NOT NULL,
  `titulo_obra` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `ubicacion_obra` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `tipo_obra` varchar(30) NOT NULL,
  `fecha` datetime NOT NULL,
  `municipio` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `parroquia` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `solicitudes_pendientes` int NOT NULL,
  `solicitudes_procesadas` int NOT NULL,
  `cantidad_total_solicitudes` int NOT NULL,
  `cantidad_comunidades_atendidas` int NOT NULL,
  `institucion` varchar(45) NOT NULL,
  `gerencia` varchar(45) NOT NULL,
  `evidencia_antes` varchar(50) NOT NULL,
  `evidencia_durante` varchar(50) NOT NULL,
  `evidencia_despues` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `solicitante`
--

CREATE TABLE `solicitante` (
  `id_solicitante` int NOT NULL,
  `nombre_solicitante` varchar(90) NOT NULL,
  `parroquia` varchar(45) NOT NULL,
  `municipio` varchar(45) NOT NULL,
  `ambito` varchar(45) NOT NULL,
  `rif` varchar(45) NOT NULL,
  `cedula` varchar(10) NOT NULL,
  `correo` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de las comunidades';

--
-- Volcado de datos para la tabla `solicitante`
--

INSERT INTO `solicitante` (`id_solicitante`, `nombre_solicitante`, `parroquia`, `municipio`, `ambito`, `rif`, `cedula`, `correo`) VALUES
(1, 'Santa Maria', 'Guerrera Ana Soto (Juan de Villegas)', 'Iribarren', 'San Francisco', 'J-978563412', '29789456', 'America@gmail.com'),
(2, 'CORPEELECT', '', '', 'Caja de Agua', '02513353950', '9334114', 'corpeelect@gmail.com');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuarios` int NOT NULL,
  `cedula_usuario` varchar(10) NOT NULL,
  `nombre` varchar(45) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `correo` varchar(45) NOT NULL,
  `rol` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuarios`, `cedula_usuario`, `nombre`, `contrasena`, `correo`, `rol`) VALUES
(1, '12345678', 'admin', 'pbkdf2:sha256:600000$pQt5FWIkRkcGt5JD$db9d05e87050c9a6dc20a8a96bea7a71a2abaec9e04bfe9d7576b79837effd77', 'admin@invisap.com', 'Administrador'),
(4, '87654321', 'informatica', 'pbkdf2:sha256:600000$NANX5pro94zIDr4n$d9d590433732cb8341c4c04b0e22218987f21598fd6273e8918211877c87c70b', 'informatic.invilara@gmail.com', 'Super Usuario'),
(5, '30553759', 'Frangher Pereira', 'pbkdf2:sha256:600000$eApYKBEE15Ye7FN6$62dc766207151446826b9bee49e6288348bad2a98c7527bc11da87fd2472c5ba', 'frangher@gmail.com', 'Asistente');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD PRIMARY KEY (`id_empleados`);

--
-- Indices de la tabla `empresa`
--
ALTER TABLE `empresa`
  ADD PRIMARY KEY (`rif`,`gestionar_proyectos_id_proyectos`,`gestionar_proyectos_maquinaria_id_maquinaria`,`gestionar_obra_id_inspeccion`),
  ADD UNIQUE KEY `rif_proy_maq_UNIQUE` (`rif`,`gestionar_proyectos_id_proyectos`,`gestionar_proyectos_maquinaria_id_maquinaria`),
  ADD UNIQUE KEY `rif_UNIQUE` (`rif`),
  ADD KEY `fk_empresa_gestionar_proyectos1_idx` (`gestionar_proyectos_id_proyectos`,`gestionar_proyectos_maquinaria_id_maquinaria`),
  ADD KEY `fk_empresa_gestionar_obra1_idx` (`gestionar_obra_id_inspeccion`);

--
-- Indices de la tabla `gerencias`
--
ALTER TABLE `gerencias`
  ADD PRIMARY KEY (`id_gerencias`,`informe_avance_obra_id_informe`),
  ADD UNIQUE KEY `id_gerencias_UNIQUE` (`id_gerencias`),
  ADD UNIQUE KEY `nombre_gerencia_UNIQUE` (`nombre_gerencia`),
  ADD KEY `fk_gerencias_informe_avance_obra1_idx` (`informe_avance_obra_id_informe`);

--
-- Indices de la tabla `gerencias_has_empleados`
--
ALTER TABLE `gerencias_has_empleados`
  ADD PRIMARY KEY (`gerencias_id_gerencias`,`empleados_id_empleados`),
  ADD KEY `fk_gerencias_has_empleados_empleados1_idx` (`empleados_id_empleados`),
  ADD KEY `fk_gerencias_has_empleados_gerencias1_idx` (`gerencias_id_gerencias`);

--
-- Indices de la tabla `gerencias_has_gestionar_prioridad`
--
ALTER TABLE `gerencias_has_gestionar_prioridad`
  ADD PRIMARY KEY (`gerencias_id_gerencias`,`gerencias_informe_avance_obra_id_informe`,`gestionar_prioridad_id_gestion_prioridad`),
  ADD KEY `fk_gerencias_has_gestionar_prioridad_gestionar_prioridad1_idx` (`gestionar_prioridad_id_gestion_prioridad`),
  ADD KEY `fk_gerencias_has_gestionar_prioridad_gerencias1_idx` (`gerencias_id_gerencias`,`gerencias_informe_avance_obra_id_informe`);

--
-- Indices de la tabla `gestionar_contrataciones`
--
ALTER TABLE `gestionar_contrataciones`
  ADD PRIMARY KEY (`id_contratacion`,`gestionar_proyectos_id_proyectos`,`gestionar_proyectos_maquinaria_id_maquinaria`,`empresa_rif`,`empresa_gestionar_proyectos_id_proyectos`,`empresa_gestionar_proyectos_maquinaria_id_maquinaria`),
  ADD UNIQUE KEY `numero_contrato_UNIQUE` (`numero_contrato`),
  ADD KEY `fk_gestionar_contrataciones_gestionar_proyectos1_idx` (`gestionar_proyectos_id_proyectos`,`gestionar_proyectos_maquinaria_id_maquinaria`),
  ADD KEY `fk_gestionar_contrataciones_empresa1_idx` (`empresa_rif`,`empresa_gestionar_proyectos_id_proyectos`,`empresa_gestionar_proyectos_maquinaria_id_maquinaria`);

--
-- Indices de la tabla `gestionar_gravedad`
--
ALTER TABLE `gestionar_gravedad`
  ADD PRIMARY KEY (`id_gravedad`);

--
-- Indices de la tabla `gestionar_obra`
--
ALTER TABLE `gestionar_obra`
  ADD PRIMARY KEY (`id_inspeccion`,`inspectores_id_inspector`),
  ADD UNIQUE KEY `id_inspeccion_UNIQUE` (`id_inspeccion`),
  ADD KEY `fk_gestionar_obra_inspectores1_idx` (`inspectores_id_inspector`);

--
-- Indices de la tabla `gestionar_prioridad`
--
ALTER TABLE `gestionar_prioridad`
  ADD PRIMARY KEY (`id_gestion_prioridad`);

--
-- Indices de la tabla `gestionar_proyectos`
--
ALTER TABLE `gestionar_proyectos`
  ADD PRIMARY KEY (`id_proyectos`,`maquinaria_id_maquinaria`,`gerencias_id_gerencias`),
  ADD UNIQUE KEY `id_proy_maq_UNIQUE` (`id_proyectos`,`maquinaria_id_maquinaria`),
  ADD UNIQUE KEY `codigo_proyecto_UNIQUE` (`codigo_proyecto`),
  ADD KEY `fk_gestionar_proyectos_maquinaria_idx` (`maquinaria_id_maquinaria`),
  ADD KEY `fk_gestionar_proyectos_gerencias1_idx` (`gerencias_id_gerencias`);

--
-- Indices de la tabla `gestionar_publicaciones`
--
ALTER TABLE `gestionar_publicaciones`
  ADD PRIMARY KEY (`id_publicaciones`);

--
-- Indices de la tabla `gestionar_solicitudes`
--
ALTER TABLE `gestionar_solicitudes`
  ADD PRIMARY KEY (`id_solicitud`,`solicitante_id_comunidad`),
  ADD UNIQUE KEY `id_solicitud_UNIQUE` (`id_solicitud`),
  ADD KEY `fk_gestionar_solicitudes_solicitante1_idx` (`solicitante_id_comunidad`);

--
-- Indices de la tabla `informe_avance_obra`
--
ALTER TABLE `informe_avance_obra`
  ADD PRIMARY KEY (`id_informe`);

--
-- Indices de la tabla `informe_avance_obra_has_gestionar_publicaciones`
--
ALTER TABLE `informe_avance_obra_has_gestionar_publicaciones`
  ADD PRIMARY KEY (`informe_avance_obra_id_informe`,`gestionar_publicaciones_id_publicaciones`),
  ADD KEY `fk_informe_avance_obra_has_gestionar_publicaciones_gestiona_idx` (`gestionar_publicaciones_id_publicaciones`),
  ADD KEY `fk_informe_avance_obra_has_gestionar_publicaciones_informe__idx` (`informe_avance_obra_id_informe`);

--
-- Indices de la tabla `inspectores`
--
ALTER TABLE `inspectores`
  ADD PRIMARY KEY (`id_inspector`),
  ADD UNIQUE KEY `cedula_UNIQUE` (`cedula`);

--
-- Indices de la tabla `maquinaria`
--
ALTER TABLE `maquinaria`
  ADD PRIMARY KEY (`id_maquinaria`);

--
-- Indices de la tabla `priorizar_solicitudes`
--
ALTER TABLE `priorizar_solicitudes`
  ADD PRIMARY KEY (`id_priorizacion`,`gestionar_prioridad_id_gestion_prioridad`,`gestionar_gravedad_id_gravedad`,`gestionar_solicitudes_id_solicitud`),
  ADD KEY `fk_priorizar_solicitudes_gestionar_prioridad1_idx` (`gestionar_prioridad_id_gestion_prioridad`),
  ADD KEY `fk_priorizar_solicitudes_gestionar_gravedad1_idx` (`gestionar_gravedad_id_gravedad`),
  ADD KEY `fk_priorizar_solicitudes_gestionar_solicitudes1_idx` (`gestionar_solicitudes_id_solicitud`);

--
-- Indices de la tabla `reporte`
--
ALTER TABLE `reporte`
  ADD PRIMARY KEY (`id_reporte`),
  ADD UNIQUE KEY `titulo_obra_UNIQUE` (`titulo_obra`);

--
-- Indices de la tabla `solicitante`
--
ALTER TABLE `solicitante`
  ADD PRIMARY KEY (`id_solicitante`),
  ADD UNIQUE KEY `nombre_UNIQUE` (`nombre_solicitante`),
  ADD UNIQUE KEY `rif_UNIQUE` (`rif`),
  ADD UNIQUE KEY `cedula_UNIQUE` (`cedula`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuarios`),
  ADD UNIQUE KEY `cedula_usuario_UNIQUE` (`cedula_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `empleados`
--
ALTER TABLE `empleados`
  MODIFY `id_empleados` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `gerencias`
--
ALTER TABLE `gerencias`
  MODIFY `id_gerencias` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `gestionar_contrataciones`
--
ALTER TABLE `gestionar_contrataciones`
  MODIFY `id_contratacion` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `gestionar_gravedad`
--
ALTER TABLE `gestionar_gravedad`
  MODIFY `id_gravedad` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `gestionar_obra`
--
ALTER TABLE `gestionar_obra`
  MODIFY `id_inspeccion` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `gestionar_prioridad`
--
ALTER TABLE `gestionar_prioridad`
  MODIFY `id_gestion_prioridad` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `gestionar_proyectos`
--
ALTER TABLE `gestionar_proyectos`
  MODIFY `id_proyectos` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `gestionar_publicaciones`
--
ALTER TABLE `gestionar_publicaciones`
  MODIFY `id_publicaciones` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `gestionar_solicitudes`
--
ALTER TABLE `gestionar_solicitudes`
  MODIFY `id_solicitud` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `informe_avance_obra`
--
ALTER TABLE `informe_avance_obra`
  MODIFY `id_informe` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `inspectores`
--
ALTER TABLE `inspectores`
  MODIFY `id_inspector` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `maquinaria`
--
ALTER TABLE `maquinaria`
  MODIFY `id_maquinaria` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `priorizar_solicitudes`
--
ALTER TABLE `priorizar_solicitudes`
  MODIFY `id_priorizacion` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reporte`
--
ALTER TABLE `reporte`
  MODIFY `id_reporte` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `solicitante`
--
ALTER TABLE `solicitante`
  MODIFY `id_solicitante` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuarios` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `empresa`
--
ALTER TABLE `empresa`
  ADD CONSTRAINT `fk_empresa_gestionar_obra1` FOREIGN KEY (`gestionar_obra_id_inspeccion`) REFERENCES `gestionar_obra` (`id_inspeccion`),
  ADD CONSTRAINT `fk_empresa_gestionar_proyectos1` FOREIGN KEY (`gestionar_proyectos_id_proyectos`,`gestionar_proyectos_maquinaria_id_maquinaria`) REFERENCES `gestionar_proyectos` (`id_proyectos`, `maquinaria_id_maquinaria`);

--
-- Filtros para la tabla `gerencias`
--
ALTER TABLE `gerencias`
  ADD CONSTRAINT `fk_gerencias_informe_avance_obra1` FOREIGN KEY (`informe_avance_obra_id_informe`) REFERENCES `informe_avance_obra` (`id_informe`);

--
-- Filtros para la tabla `gerencias_has_empleados`
--
ALTER TABLE `gerencias_has_empleados`
  ADD CONSTRAINT `fk_gerencias_has_empleados_empleados1` FOREIGN KEY (`empleados_id_empleados`) REFERENCES `empleados` (`id_empleados`),
  ADD CONSTRAINT `fk_gerencias_has_empleados_gerencias1` FOREIGN KEY (`gerencias_id_gerencias`) REFERENCES `gerencias` (`id_gerencias`);

--
-- Filtros para la tabla `gerencias_has_gestionar_prioridad`
--
ALTER TABLE `gerencias_has_gestionar_prioridad`
  ADD CONSTRAINT `fk_gerencias_has_gestionar_prioridad_gerencias1` FOREIGN KEY (`gerencias_id_gerencias`,`gerencias_informe_avance_obra_id_informe`) REFERENCES `gerencias` (`id_gerencias`, `informe_avance_obra_id_informe`),
  ADD CONSTRAINT `fk_gerencias_has_gestionar_prioridad_gestionar_prioridad1` FOREIGN KEY (`gestionar_prioridad_id_gestion_prioridad`) REFERENCES `gestionar_prioridad` (`id_gestion_prioridad`);

--
-- Filtros para la tabla `gestionar_contrataciones`
--
ALTER TABLE `gestionar_contrataciones`
  ADD CONSTRAINT `fk_gestionar_contrataciones_empresa1` FOREIGN KEY (`empresa_rif`,`empresa_gestionar_proyectos_id_proyectos`,`empresa_gestionar_proyectos_maquinaria_id_maquinaria`) REFERENCES `empresa` (`rif`, `gestionar_proyectos_id_proyectos`, `gestionar_proyectos_maquinaria_id_maquinaria`),
  ADD CONSTRAINT `fk_gestionar_contrataciones_gestionar_proyectos1` FOREIGN KEY (`gestionar_proyectos_id_proyectos`,`gestionar_proyectos_maquinaria_id_maquinaria`) REFERENCES `gestionar_proyectos` (`id_proyectos`, `maquinaria_id_maquinaria`);

--
-- Filtros para la tabla `gestionar_obra`
--
ALTER TABLE `gestionar_obra`
  ADD CONSTRAINT `fk_gestionar_obra_inspectores1` FOREIGN KEY (`inspectores_id_inspector`) REFERENCES `inspectores` (`id_inspector`);

--
-- Filtros para la tabla `gestionar_proyectos`
--
ALTER TABLE `gestionar_proyectos`
  ADD CONSTRAINT `fk_gestionar_proyectos_gerencias1` FOREIGN KEY (`gerencias_id_gerencias`) REFERENCES `gerencias` (`id_gerencias`),
  ADD CONSTRAINT `fk_gestionar_proyectos_maquinaria` FOREIGN KEY (`maquinaria_id_maquinaria`) REFERENCES `maquinaria` (`id_maquinaria`);

--
-- Filtros para la tabla `gestionar_solicitudes`
--
ALTER TABLE `gestionar_solicitudes`
  ADD CONSTRAINT `fk_gestionar_solicitudes_solicitante1` FOREIGN KEY (`solicitante_id_comunidad`) REFERENCES `solicitante` (`id_solicitante`);

--
-- Filtros para la tabla `informe_avance_obra_has_gestionar_publicaciones`
--
ALTER TABLE `informe_avance_obra_has_gestionar_publicaciones`
  ADD CONSTRAINT `fk_informe_avance_obra_has_gestionar_publicaciones_gestionar_1` FOREIGN KEY (`gestionar_publicaciones_id_publicaciones`) REFERENCES `gestionar_publicaciones` (`id_publicaciones`),
  ADD CONSTRAINT `fk_informe_avance_obra_has_gestionar_publicaciones_informe_av1` FOREIGN KEY (`informe_avance_obra_id_informe`) REFERENCES `informe_avance_obra` (`id_informe`);

--
-- Filtros para la tabla `priorizar_solicitudes`
--
ALTER TABLE `priorizar_solicitudes`
  ADD CONSTRAINT `fk_priorizar_solicitudes_gestionar_gravedad1` FOREIGN KEY (`gestionar_gravedad_id_gravedad`) REFERENCES `gestionar_gravedad` (`id_gravedad`),
  ADD CONSTRAINT `fk_priorizar_solicitudes_gestionar_prioridad1` FOREIGN KEY (`gestionar_prioridad_id_gestion_prioridad`) REFERENCES `gestionar_prioridad` (`id_gestion_prioridad`),
  ADD CONSTRAINT `fk_priorizar_solicitudes_gestionar_solicitudes1` FOREIGN KEY (`gestionar_solicitudes_id_solicitud`) REFERENCES `gestionar_solicitudes` (`id_solicitud`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
