-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 16-06-2026 a las 22:19:49
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
-- Estructura de tabla para la tabla `avance`
--

CREATE TABLE `avance` (
  `id_avance` varchar(45) NOT NULL,
  `porcentaje_avance` int NOT NULL,
  `descripcion` varchar(45) NOT NULL,
  `gerente` varchar(45) NOT NULL,
  `fecha_avance` date NOT NULL,
  `obra_id_obra` int NOT NULL,
  `obra_semaforo_id_semaforo` int NOT NULL,
  `obra_contratacion_id_contratacion` int NOT NULL,
  `obra_gestionar_proyectos_codigo_proyecto` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `comunidad`
--

CREATE TABLE `comunidad` (
  `id_comunidad` int NOT NULL,
  `nombre_comunidad` varchar(100) NOT NULL,
  `ambito` varchar(45) NOT NULL,
  `sector` varchar(45) NOT NULL,
  `persona_id_persona` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `comunidad`
--

INSERT INTO `comunidad` (`id_comunidad`, `nombre_comunidad`, `ambito`, `sector`, `persona_id_persona`) VALUES
(1, 'prueba02', 'prueba', 'pruuuu', 2),
(2, 'carorita', 'cuji', 'la playa', 4),
(3, 'hskHJS', 'ihjdsk', 'hjajda', 5),
(4, 'Nuevo Horizonte', 'San Francisco', 'Oeste', 6);

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
  `empresa_rif` varchar(12) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de contrataciones';

--
-- Volcado de datos para la tabla `contratacion`
--

INSERT INTO `contratacion` (`id_contratacion`, `descripcion`, `empresa_ganadora`, `numero_contrato`, `monto`, `fecha_inicio_procedimiento`, `fecha_adjudicacion`, `tipo_contrato`, `modalidad`, `objeto`, `observacion`, `fecha_registro`, `empresa_rif`) VALUES
(1, 'Hola', 'Polar', '12', '12 Dolares', '2026-06-17 00:00:00', '2026-06-24 00:00:00', 'Anual', 'Fisica', 'Afaltado', 'Calles irregulares', '2026-06-17 00:00:00', '12');

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
  `persona_id_persona` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empresa`
--

CREATE TABLE `empresa` (
  `rif` varchar(12) NOT NULL,
  `nombre_empresa` varchar(80) NOT NULL,
  `telefono` varchar(12) NOT NULL COMMENT 'Tabla de empresas.',
  `domicilio_fiscal` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `empresa`
--

INSERT INTO `empresa` (`rif`, `nombre_empresa`, `telefono`, `domicilio_fiscal`) VALUES
('12', 'Polar', '04122212121', 'Calle 13c');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `evidencia`
--

CREATE TABLE `evidencia` (
  `id_evidencia` int NOT NULL,
  `fotos` varchar(45) NOT NULL,
  `url_archivos` varchar(90) NOT NULL,
  `fecha_registro` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gravedad_obra`
--

CREATE TABLE `gravedad_obra` (
  `id_gravedad` int NOT NULL,
  `nivel_gravedad` varchar(20) NOT NULL,
  `criticidad` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gravedad_obra_has_prioridad`
--

CREATE TABLE `gravedad_obra_has_prioridad` (
  `gravedad_obra_id_gravedad` int NOT NULL,
  `prioridad_id_gestion_prioridad` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `informe_avance_obra`
--

CREATE TABLE `informe_avance_obra` (
  `id_informe` int NOT NULL,
  `fecha` datetime NOT NULL,
  `estado` varchar(25) NOT NULL,
  `poblacion_benefiada` varchar(45) NOT NULL,
  `tipo_informe` varchar(30) NOT NULL,
  `evidencia_antes` varchar(50) NOT NULL,
  `evidencia_durante` varchar(50) NOT NULL,
  `evidencia_despues` varchar(50) NOT NULL,
  `avance_id_avance` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de informes de avances de obras';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `inspeccion`
--

CREATE TABLE `inspeccion` (
  `id_inspeccion` int NOT NULL,
  `inspector` varchar(45) NOT NULL,
  `fecha_inspeccion` date NOT NULL,
  `tipo_inspeccion` varchar(45) NOT NULL,
  `observaciones` varchar(255) NOT NULL,
  `obra_id_obra` int NOT NULL,
  `obra_semaforo_id_semaforo` int NOT NULL,
  `obra_contratacion_id_contratacion` int NOT NULL,
  `obra_gestionar_proyectos_codigo_proyecto` varchar(15) NOT NULL,
  `obra_id_obra1` int NOT NULL,
  `obra_semaforo_id_semaforo1` int NOT NULL,
  `obra_contratacion_id_contratacion1` int NOT NULL,
  `obra_gestionar_proyectos_codigo_proyecto1` varchar(15) NOT NULL,
  `evidencia_id_evidencia` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `institucion`
--

CREATE TABLE `institucion` (
  `id_institucion` int NOT NULL,
  `nombre_representante` varchar(45) NOT NULL,
  `razon_social` varchar(120) NOT NULL,
  `persona_id_persona` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `institucion`
--

INSERT INTO `institucion` (`id_institucion`, `nombre_representante`, `razon_social`, `persona_id_persona`) VALUES
(1, 'gabriel', 'youtube', 3);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `maquinaria`
--

CREATE TABLE `maquinaria` (
  `id_maquinaria` int NOT NULL,
  `nombre_maquinaria` varchar(50) NOT NULL COMMENT 'Tabla de nombres de maquinarias',
  `tipo_maquinaria` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `obra`
--

CREATE TABLE `obra` (
  `id_obra` int NOT NULL,
  `titulo_obra` varchar(45) NOT NULL,
  `ubicacion_obra` varchar(80) NOT NULL,
  `periodo_ejecucion` int NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `mediciones_obra` varchar(45) NOT NULL,
  `valuaciones` varchar(100) NOT NULL,
  `modificaciones_contrato` varchar(100) NOT NULL,
  `certificaciones_obras_ejecutadas` int NOT NULL,
  `numero_contrato` varchar(20) NOT NULL,
  `porcentaje_avance_obra` int NOT NULL,
  `semaforo_id_semaforo` int NOT NULL,
  `contratacion_id_contratacion` int NOT NULL,
  `gestionar_proyectos_codigo_proyecto` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de las inspecciones';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `particular`
--

CREATE TABLE `particular` (
  `id_particular` int NOT NULL,
  `nombre` varchar(45) NOT NULL,
  `apellido` varchar(45) NOT NULL,
  `persona_id_persona` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `particular`
--

INSERT INTO `particular` (`id_particular`, `nombre`, `apellido`, `persona_id_persona`) VALUES
(1, 'Gabriel', 'Mujica', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `persona`
--

CREATE TABLE `persona` (
  `id_persona` int NOT NULL,
  `cedula_persona` int NOT NULL,
  `direccion` varchar(200) NOT NULL,
  `parroquia` varchar(45) NOT NULL,
  `municipio` varchar(45) NOT NULL,
  `telefono` tinytext NOT NULL,
  `correo` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `persona`
--

INSERT INTO `persona` (`id_persona`, `cedula_persona`, `direccion`, `parroquia`, `municipio`, `telefono`, `correo`) VALUES
(1, 29957469, 'CAlle 24 entre 32 y 33', 'Catedral', 'Iribarren', '04128280586', 'gabrielenriquemch@gmail.com'),
(2, 34567896, 'prueba', 'Agua Viva', 'Palavecino', '04245678568', 'fedegtq2@gmail.com'),
(3, 56785729, 'calle miami', 'Hilario Luna y Luna', 'Morán', '04245678934', 'youtube@gmail.coom'),
(4, 31258936, 'cuji', 'Freitez', 'Crespo', '04245087200', 'redfiury21@gmail.com'),
(5, 30088284, 'ihjdsk', 'Cabudare', 'Palavecino', '04120587814', 'jose@gmail.com'),
(6, 28433546, 'San Francisco', 'Guerrera Ana Soto (Juan de Villegas)', 'Iribarren', '04123582233', 'mafer25@gmail.com');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prioridad`
--

CREATE TABLE `prioridad` (
  `id_gestion_prioridad` int NOT NULL,
  `rango_prioridad` float NOT NULL,
  `fecha_asignacion` datetime NOT NULL,
  `responsable_ajuste` varchar(30) NOT NULL,
  `justificacion_cambio` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `prioridad`
--

INSERT INTO `prioridad` (`id_gestion_prioridad`, `rango_prioridad`, `fecha_asignacion`, `responsable_ajuste`, `justificacion_cambio`) VALUES
(1, 1, '2026-06-15 16:38:02', 'Sistema', 'Default');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proyecto`
--

CREATE TABLE `proyecto` (
  `codigo_proyecto` varchar(15) NOT NULL,
  `fecha_planificacion` datetime NOT NULL,
  `descripcion_tecnica` varchar(200) NOT NULL,
  `computos_metricos` varchar(255) NOT NULL,
  `estimacion_costo` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de gestion de proyectos';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proyecto_has_maquinaria`
--

CREATE TABLE `proyecto_has_maquinaria` (
  `proyecto_codigo_proyecto` varchar(15) NOT NULL,
  `maquinaria_id_maquinaria` int NOT NULL
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
  `informe_avance_obra_id_informe` int NOT NULL
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
  `informe_avance_obra_id_informe` int NOT NULL
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
  `informe_avance_obra_id_informe` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `semaforo`
--

CREATE TABLE `semaforo` (
  `id_semaforo` int NOT NULL,
  `estado` varchar(20) NOT NULL,
  `color` enum('VERDE','AMARILLO','ROJO') NOT NULL,
  `descripcion` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
  `prioridad_id_gestion_prioridad` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla general de las solicitudes';

--
-- Volcado de datos para la tabla `solicitudes`
--

INSERT INTO `solicitudes` (`id_solicitudes`, `fecha`, `tipo_solicitud`, `estatus_solicitud`, `problematica`, `persona_id_persona`, `prioridad_id_gestion_prioridad`) VALUES
(1, '2026-06-15 16:38:02', 'Particular', 'Pendiente', '[Servicios Básicos (Agua, Luz, Gas)] Haciendo rgistro de prueba mortadela', 1, 1),
(2, '2026-06-15 16:40:32', 'Comunidad', 'Completada', '[Salud y Asistencia Médica] hhhhhhhhhuuuuuuuuuuuuuuuuu  mantequilla', 2, 1),
(3, '2026-06-15 16:42:00', 'Institucion', 'En Proceso', '[Servicios Básicos (Agua, Luz, Gas)] gggggggggggggggggggggggggggggggggggggg jamon', 3, 1),
(5, '2026-06-15 16:46:00', 'Comunidad', 'Pendiente', '[Servicios Básicos (Agua, Luz, Gas)] hueco en la avenida donde salen aguas negras', 4, 1),
(6, '2026-06-15 19:07:05', 'Comunidad', 'Completada', '[Infraestructura y Vialidad] aaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 5, 1),
(7, '2026-06-16 17:58:23', 'Comunidad', 'En Proceso', '[Infraestructura y Vialidad] Acondicionamiento vial', 6, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuarios` int NOT NULL,
  `nombre` varchar(25) COLLATE utf8mb4_general_ci NOT NULL,
  `cedula_usuario` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `contrasena` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `correo` varchar(45) COLLATE utf8mb4_general_ci NOT NULL,
  `rol` varchar(20) COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Tabla de los usuarios.'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Tabla de usuarios';

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuarios`, `nombre`, `cedula_usuario`, `contrasena`, `correo`, `rol`) VALUES
(1, 'Jhoanly', '30395804', 'pbkdf2:sha256:600000$hI1ARI12kxLAauXD$cfb2353db5762ef956921c951c91fa3bc1deeea2b66511bee0fc27ef527ac1da', 'admin@gmail.com', 'Usuario'),
(2, 'Frangher', '30553759', 'pbkdf2:sha256:600000$BW8CshHpdlpCU2pX$850ca46134fe0094d6e26718d0e8e54b895486e8bf30baf3923e167166641122', 'frangher@gmail.com', 'Usuario'),
(3, 'potato', '9543017', 'pbkdf2:sha256:600000$1shk4qAbaznq5Ui1$cf4aebb33ade4358663ac5895b337fc6606cb520dad328711394a47a697529b1', 'potato@gmail.com', 'Usuario');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `avance`
--
ALTER TABLE `avance`
  ADD PRIMARY KEY (`id_avance`),
  ADD KEY `fk_avance_obra1_idx` (`obra_id_obra`,`obra_semaforo_id_semaforo`,`obra_contratacion_id_contratacion`,`obra_gestionar_proyectos_codigo_proyecto`);

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
  ADD KEY `fk_empleados_persona1_idx` (`persona_id_persona`);

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
  ADD KEY `fk_informe_avance_obra_avance1_idx` (`avance_id_avance`);

--
-- Indices de la tabla `inspeccion`
--
ALTER TABLE `inspeccion`
  ADD PRIMARY KEY (`id_inspeccion`,`evidencia_id_evidencia`),
  ADD UNIQUE KEY `cedula_UNIQUE` (`fecha_inspeccion`),
  ADD KEY `fk_inspeccion_obra1_idx` (`obra_id_obra1`,`obra_semaforo_id_semaforo1`,`obra_contratacion_id_contratacion1`,`obra_gestionar_proyectos_codigo_proyecto1`),
  ADD KEY `fk_inspeccion_evidencia1_idx` (`evidencia_id_evidencia`);

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
  ADD PRIMARY KEY (`id_obra`,`semaforo_id_semaforo`,`contratacion_id_contratacion`,`gestionar_proyectos_codigo_proyecto`),
  ADD UNIQUE KEY `id_obra_UNIQUE` (`id_obra`),
  ADD KEY `fk_obra_semaforo1_idx` (`semaforo_id_semaforo`),
  ADD KEY `fk_obra_contratacion1_idx` (`contratacion_id_contratacion`),
  ADD KEY `fk_obra_gestionar_proyectos1_idx` (`gestionar_proyectos_codigo_proyecto`);

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
  ADD UNIQUE KEY `codigo_proyecto_UNIQUE` (`codigo_proyecto`);

--
-- Indices de la tabla `proyecto_has_maquinaria`
--
ALTER TABLE `proyecto_has_maquinaria`
  ADD PRIMARY KEY (`proyecto_codigo_proyecto`,`maquinaria_id_maquinaria`),
  ADD KEY `fk_proyecto_has_maquinaria_maquinaria1_idx` (`maquinaria_id_maquinaria`),
  ADD KEY `fk_proyecto_has_maquinaria_proyecto1_idx` (`proyecto_codigo_proyecto`);

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
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuarios`),
  ADD UNIQUE KEY `cedula_usuario_UNIQUE` (`cedula_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `comunidad`
--
ALTER TABLE `comunidad`
  MODIFY `id_comunidad` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `contratacion`
--
ALTER TABLE `contratacion`
  MODIFY `id_contratacion` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

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
  MODIFY `id_institucion` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

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
  MODIFY `id_particular` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `persona`
--
ALTER TABLE `persona`
  MODIFY `id_persona` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `prioridad`
--
ALTER TABLE `prioridad`
  MODIFY `id_gestion_prioridad` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

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
  MODIFY `id_semaforo` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `solicitudes`
--
ALTER TABLE `solicitudes`
  MODIFY `id_solicitudes` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuarios` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `avance`
--
ALTER TABLE `avance`
  ADD CONSTRAINT `fk_avance_obra1` FOREIGN KEY (`obra_id_obra`,`obra_semaforo_id_semaforo`,`obra_contratacion_id_contratacion`,`obra_gestionar_proyectos_codigo_proyecto`) REFERENCES `obra` (`id_obra`, `semaforo_id_semaforo`, `contratacion_id_contratacion`, `gestionar_proyectos_codigo_proyecto`);

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
  ADD CONSTRAINT `fk_inspeccion_evidencia1` FOREIGN KEY (`evidencia_id_evidencia`) REFERENCES `evidencia` (`id_evidencia`),
  ADD CONSTRAINT `fk_inspeccion_obra1` FOREIGN KEY (`obra_id_obra1`,`obra_semaforo_id_semaforo1`,`obra_contratacion_id_contratacion1`,`obra_gestionar_proyectos_codigo_proyecto1`) REFERENCES `obra` (`id_obra`, `semaforo_id_semaforo`, `contratacion_id_contratacion`, `gestionar_proyectos_codigo_proyecto`);

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
  ADD CONSTRAINT `fk_obra_gestionar_proyectos1` FOREIGN KEY (`gestionar_proyectos_codigo_proyecto`) REFERENCES `proyecto` (`codigo_proyecto`),
  ADD CONSTRAINT `fk_obra_semaforo1` FOREIGN KEY (`semaforo_id_semaforo`) REFERENCES `semaforo` (`id_semaforo`);

--
-- Filtros para la tabla `particular`
--
ALTER TABLE `particular`
  ADD CONSTRAINT `fk_particular_persona1` FOREIGN KEY (`persona_id_persona`) REFERENCES `persona` (`id_persona`);

--
-- Filtros para la tabla `proyecto_has_maquinaria`
--
ALTER TABLE `proyecto_has_maquinaria`
  ADD CONSTRAINT `fk_proyecto_has_maquinaria_maquinaria1` FOREIGN KEY (`maquinaria_id_maquinaria`) REFERENCES `maquinaria` (`id_maquinaria`),
  ADD CONSTRAINT `fk_proyecto_has_maquinaria_proyecto1` FOREIGN KEY (`proyecto_codigo_proyecto`) REFERENCES `proyecto` (`codigo_proyecto`);

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
