-- phpMyAdmin SQL Dump
-- version 5.2.2deb1+deb13u1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 08-07-2026 a las 07:44:11
-- Versión del servidor: 11.8.6-MariaDB-0+deb13u1 from Debian
-- Versión de PHP: 8.4.21

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
  `porcentaje_avance` int(11) NOT NULL,
  `descripcion` varchar(45) NOT NULL,
  `gerente` varchar(45) NOT NULL,
  `fecha_avance` date NOT NULL,
  `obra_id_obra` int(11) NOT NULL,
  `obra_semaforo_id_semaforo` int(11) NOT NULL,
  `obra_contratacion_id_contratacion` int(11) NOT NULL,
  `obra_gestionar_proyectos_codigo_proyecto` varchar(15) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `avance`
--

INSERT INTO `avance` (`id_avance`, `porcentaje_avance`, `descripcion`, `gerente`, `fecha_avance`, `obra_id_obra`, `obra_semaforo_id_semaforo`, `obra_contratacion_id_contratacion`, `obra_gestionar_proyectos_codigo_proyecto`, `estado`) VALUES
('3d65f647b8e9', 7, 'nuncasd sdsds', '5', '2026-07-07', 1, 1, 1, 'FRE-001', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `catalogo_cargos`
--

CREATE TABLE `catalogo_cargos` (
  `id_cargo` int(11) NOT NULL,
  `nombre_cargo` varchar(45) NOT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catálogo de cargos institucionales';

--
-- Volcado de datos para la tabla `catalogo_cargos`
--

INSERT INTO `catalogo_cargos` (`id_cargo`, `nombre_cargo`, `descripcion`, `estado`) VALUES
(1, 'Gerente', 'Gerente de área o departamento', 1),
(2, 'Inspector', 'Inspector de obras y proyectos', 1),
(3, 'Asistente', 'Asistente administrativo', 1),
(4, 'Proyectista', 'Responsable de diseño de proyectos', 1),
(5, 'Recepcionista', 'Atención al público', 1),
(6, 'Ingeniero', 'Ingeniero técnico', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `comunidad`
--

CREATE TABLE `comunidad` (
  `id_comunidad` int(11) NOT NULL,
  `nombre_comunidad` varchar(100) NOT NULL,
  `ambito` varchar(45) NOT NULL,
  `sector` varchar(45) NOT NULL,
  `persona_id_persona` int(11) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `comunidad`
--

INSERT INTO `comunidad` (`id_comunidad`, `nombre_comunidad`, `ambito`, `sector`, `persona_id_persona`, `estado`) VALUES
(1, 'prueba02', 'prueba', 'pruuuu', 2, 1),
(2, 'carorita', 'cuji', 'la playa', 4, 1),
(3, 'hskHJS', 'ihjdsk', 'hjajda', 5, 1),
(4, 'Nuevo Horizonte', 'San Francisco', 'Oeste', 6, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `contratacion`
--

CREATE TABLE `contratacion` (
  `id_contratacion` int(11) NOT NULL,
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
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de contrataciones';

--
-- Volcado de datos para la tabla `contratacion`
--

INSERT INTO `contratacion` (`id_contratacion`, `descripcion`, `empresa_ganadora`, `numero_contrato`, `monto`, `fecha_inicio_procedimiento`, `fecha_adjudicacion`, `tipo_contrato`, `modalidad`, `objeto`, `observacion`, `fecha_registro`, `empresa_rif`, `estado`) VALUES
(1, 'Hola', 'Polar', '12', '12 Dolares', '2026-06-17 00:00:00', '2026-06-24 00:00:00', 'Anual', 'Fisica', 'Afaltado', 'Calles irregulares', '2026-06-17 00:00:00', '12', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleados`
--

CREATE TABLE `empleados` (
  `id_empleados` int(11) NOT NULL,
  `nombre_empleado` varchar(45) NOT NULL,
  `cargo` varchar(45) NOT NULL,
  `fecha_ingreso` date NOT NULL,
  `gerencia_asignada` varchar(45) NOT NULL,
  `persona_id_persona` int(11) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `empleados`
--

INSERT INTO `empleados` (`id_empleados`, `nombre_empleado`, `cargo`, `fecha_ingreso`, `gerencia_asignada`, `persona_id_persona`, `estado`) VALUES
(1, 'Juan Carlos Perez Hernandez', 'Inspector', '2026-06-20', 'Obras', 7, 1),
(2, 'Cesilia  del Carmen Suarez', 'Recepcionista', '2026-06-20', 'Atención al Ciudadano', 9, 1),
(3, 'Maria del Carmen Suarez', 'Asistente', '2026-06-20', 'Comunicaciones', 9, 1),
(5, 'Carlos Ramírez Inspector', 'Inspector', '2026-06-22', 'Obras Públicas', 1, 1),
(6, 'Freider Guedez', 'Proyectista', '2026-07-01', 'MARUSLANE', 12, 1),
(7, 'juan cfddd', 'Proyectista', '2026-07-07', 'mmmbbbhjhg', 12, 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empresa`
--

CREATE TABLE `empresa` (
  `rif` varchar(12) NOT NULL,
  `nombre_empresa` varchar(80) NOT NULL,
  `telefono` varchar(12) NOT NULL COMMENT 'Tabla de empresas.',
  `domicilio_fiscal` varchar(100) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `empresa`
--

INSERT INTO `empresa` (`rif`, `nombre_empresa`, `telefono`, `domicilio_fiscal`, `estado`) VALUES
('12', 'Polar', '04122212121', 'Calle 13c', 1),
('J-377323626', 'Shampooos', '0414-7854411', 'mxvshidfhheuifpotgkpkwqkd,mcxmf', 0),
('J-412357777', 'GOKU SJJ 2', '0414-1345655', 'AVJEEDWEWD', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `evidencia`
--

CREATE TABLE `evidencia` (
  `id_evidencia` int(11) NOT NULL,
  `fotos` varchar(45) NOT NULL,
  `url_archivos` varchar(90) NOT NULL,
  `fecha_registro` datetime NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)',
  `etapa` enum('antes','durante','despues') NOT NULL DEFAULT 'antes' COMMENT 'Etapa de la evidencia fotográfica'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `evidencia`
--

INSERT INTO `evidencia` (`id_evidencia`, `fotos`, `url_archivos`, `fecha_registro`, `estado`, `etapa`) VALUES
(6, 'Captura de pantalla 2026-06-05 212200.png', 'uploads/evidencias/7751abc82705_Captura_de_pantalla_2026-06-05_212200.jpg', '2026-07-07 19:59:15', 1, 'antes'),
(7, 'Captura de pantalla 2026-06-08 231740.png', 'uploads/evidencias/ecf241f4b015_Captura_de_pantalla_2026-06-08_231740.jpg', '2026-07-07 19:59:15', 1, 'durante'),
(8, 'Captura de pantalla 2026-06-08 235811.png', 'uploads/evidencias/85d2f8120533_Captura_de_pantalla_2026-06-08_235811.jpg', '2026-07-07 19:59:15', 1, 'despues');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gravedad_obra`
--

CREATE TABLE `gravedad_obra` (
  `id_gravedad` int(11) NOT NULL,
  `nivel_gravedad` varchar(20) NOT NULL,
  `criticidad` varchar(10) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gravedad_obra_has_prioridad`
--

CREATE TABLE `gravedad_obra_has_prioridad` (
  `gravedad_obra_id_gravedad` int(11) NOT NULL,
  `prioridad_id_gestion_prioridad` int(11) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `informe_avance_obra`
--

CREATE TABLE `informe_avance_obra` (
  `id_informe` int(11) NOT NULL,
  `fecha` datetime NOT NULL,
  `estatus_informe` varchar(25) NOT NULL,
  `poblacion_beneficiada` varchar(45) NOT NULL DEFAULT 'No especificado',
  `tipo_informe` varchar(30) NOT NULL,
  `evidencia_antes` varchar(50) NOT NULL,
  `evidencia_durante` varchar(50) NOT NULL,
  `evidencia_despues` varchar(50) NOT NULL,
  `avance_id_avance` varchar(45) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de informes de avances de obras';

--
-- Volcado de datos para la tabla `informe_avance_obra`
--

INSERT INTO `informe_avance_obra` (`id_informe`, `fecha`, `estatus_informe`, `poblacion_beneficiada`, `tipo_informe`, `evidencia_antes`, `evidencia_durante`, `evidencia_despues`, `avance_id_avance`, `estado`) VALUES
(1, '2026-07-07 20:25:00', 'Paralizado', 'cuujios', 'Ficha Inspeccion Tecnica', '6', '7', '8', '3d65f647b8e9', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `inspeccion`
--

CREATE TABLE `inspeccion` (
  `id_inspeccion` int(11) NOT NULL,
  `inspector` varchar(45) NOT NULL,
  `fecha_inspeccion` date NOT NULL,
  `tipo_inspeccion` varchar(45) NOT NULL,
  `observaciones` varchar(255) NOT NULL,
  `obra_id_obra` int(11) NOT NULL,
  `obra_semaforo_id_semaforo` int(11) NOT NULL,
  `obra_contratacion_id_contratacion` int(11) NOT NULL,
  `obra_gestionar_proyectos_codigo_proyecto` varchar(15) NOT NULL,
  `obra_id_obra1` int(11) NOT NULL,
  `obra_semaforo_id_semaforo1` int(11) NOT NULL,
  `obra_contratacion_id_contratacion1` int(11) NOT NULL,
  `obra_gestionar_proyectos_codigo_proyecto1` varchar(15) NOT NULL,
  `evidencia_id_evidencia` int(11) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `institucion`
--

CREATE TABLE `institucion` (
  `id_institucion` int(11) NOT NULL,
  `nombre_representante` varchar(45) NOT NULL,
  `razon_social` varchar(120) NOT NULL,
  `persona_id_persona` int(11) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `institucion`
--

INSERT INTO `institucion` (`id_institucion`, `nombre_representante`, `razon_social`, `persona_id_persona`, `estado`) VALUES
(1, 'gabriel', 'youtube', 3, 1),
(2, 'IRIS GONZALES', 'MORROCOY', 11, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `maquinaria`
--

CREATE TABLE `maquinaria` (
  `id_maquinaria` int(11) NOT NULL,
  `nombre_maquinaria` varchar(50) NOT NULL COMMENT 'Tabla de nombres de maquinarias',
  `tipo_maquinaria` varchar(45) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `maquinaria`
--

INSERT INTO `maquinaria` (`id_maquinaria`, `nombre_maquinaria`, `tipo_maquinaria`, `estado`) VALUES
(1, 'Carro 4000', 'Pesada', 1),
(2, 'BICICLETAA', 'Pesada', 1),
(11, 'EXCABADORA 20000', 'Liviana', 0),
(12, 'ESCABADORA 20000', 'Liviana', 1),
(13, 'croooo 82882', 'Pesada', 1),
(14, 'cumbia 9000212', 'Pesada', 1),
(15, 'mantequilla 90222', 'Liviana', 1),
(16, 'jamon 2000', 'Herramienta', 1),
(17, 'ratata 7222', 'Herramienta', 1),
(18, 'caoroass21', 'Herramienta', 1),
(19, 'jamon 2000221', 'Herramienta', 1),
(20, 'corte 32331', 'Vehículo', 1),
(21, 'ratas', 'Liviana', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `obra`
--

CREATE TABLE `obra` (
  `id_obra` int(11) NOT NULL,
  `titulo_obra` varchar(45) NOT NULL,
  `ubicacion_obra` varchar(80) NOT NULL,
  `periodo_ejecucion` int(11) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `mediciones_obra` varchar(45) NOT NULL,
  `valuaciones` varchar(100) NOT NULL,
  `modificaciones_contrato` varchar(100) NOT NULL,
  `certificaciones_obras_ejecutadas` int(11) NOT NULL,
  `numero_contrato` varchar(20) NOT NULL,
  `porcentaje_avance_obra` int(11) NOT NULL,
  `semaforo_id_semaforo` int(11) NOT NULL,
  `contratacion_id_contratacion` int(11) NOT NULL,
  `gestionar_proyectos_codigo_proyecto` varchar(15) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de las inspecciones';

--
-- Volcado de datos para la tabla `obra`
--

INSERT INTO `obra` (`id_obra`, `titulo_obra`, `ubicacion_obra`, `periodo_ejecucion`, `fecha_inicio`, `fecha_fin`, `mediciones_obra`, `valuaciones`, `modificaciones_contrato`, `certificaciones_obras_ejecutadas`, `numero_contrato`, `porcentaje_avance_obra`, `semaforo_id_semaforo`, `contratacion_id_contratacion`, `gestionar_proyectos_codigo_proyecto`, `estado`) VALUES
(1, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-07', '2026-07-07', 'N/A', 'N/A', 'N/A', 0, 'N/A', 0, 1, 1, 'FRE-001', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `particular`
--

CREATE TABLE `particular` (
  `id_particular` int(11) NOT NULL,
  `nombre` varchar(45) NOT NULL,
  `apellido` varchar(45) NOT NULL,
  `persona_id_persona` int(11) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `particular`
--

INSERT INTO `particular` (`id_particular`, `nombre`, `apellido`, `persona_id_persona`, `estado`) VALUES
(1, 'Gabriel', 'Mujica', 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `persona`
--

CREATE TABLE `persona` (
  `id_persona` int(11) NOT NULL,
  `cedula_persona` int(11) NOT NULL,
  `direccion` varchar(200) NOT NULL,
  `parroquia` varchar(45) NOT NULL,
  `municipio` varchar(45) NOT NULL,
  `telefono` tinytext NOT NULL,
  `correo` varchar(45) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `persona`
--

INSERT INTO `persona` (`id_persona`, `cedula_persona`, `direccion`, `parroquia`, `municipio`, `telefono`, `correo`, `estado`) VALUES
(1, 29957469, 'CAlle 24 entre 32 y 33', 'Catedral', 'Iribarren', '04128280586', 'gabrielenriquemch@gmail.com', 1),
(2, 34567896, 'prueba', 'Agua Viva', 'Palavecino', '04245678568', 'fedegtq2@gmail.com', 1),
(3, 56785729, 'calle miami', 'Hilario Luna y Luna', 'Morán', '04245678934', 'youtube@gmail.coom', 1),
(4, 31258936, 'cuji', 'Freitez', 'Crespo', '04245087200', 'redfiury21@gmail.com', 1),
(5, 30088284, 'ihjdsk', 'Cabudare', 'Palavecino', '04120587814', 'jose@gmail.com', 1),
(6, 28433546, 'San Francisco', 'Guerrera Ana Soto (Juan de Villegas)', 'Iribarren', '04123582233', 'mafer25@gmail.com', 1),
(7, 29345267, 'Calle 52 con Carrera 24 y 25 ', 'Iribarren', 'Guerrera Ana Soto', '04123456420', 'Juan45p@gmail.com', 1),
(9, 7833562, 'Carrera 24 entre Calles 36 y 37', 'Iribarren', 'Juan de Villegas', '04248379835', 'Cesif67@gmail.com', 1),
(11, 1455575885, 'AV PRINCIPAL EL TOSTAO', 'Guerrera Ana Soto (Juan de Villegas)', 'Iribarren', '04267441144', 'JOSEGUILLERMO@GMAIL.COM', 1),
(12, 30528058, 'Avenida principal el tostao sector morrocoy', 'juan de villegas', 'Iribarren', '04267955615', 'guedezfreider3@gmail.com', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prioridad`
--

CREATE TABLE `prioridad` (
  `id_gestion_prioridad` int(11) NOT NULL,
  `rango_prioridad` float NOT NULL,
  `fecha_asignacion` datetime NOT NULL,
  `responsable_ajuste` varchar(30) NOT NULL,
  `justificacion_cambio` varchar(150) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `prioridad`
--

INSERT INTO `prioridad` (`id_gestion_prioridad`, `rango_prioridad`, `fecha_asignacion`, `responsable_ajuste`, `justificacion_cambio`, `estado`) VALUES
(1, 1, '2026-06-15 16:38:02', 'Sistema', 'Default', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proyecto`
--

CREATE TABLE `proyecto` (
  `codigo_proyecto` varchar(15) NOT NULL,
  `fecha_planificacion` datetime NOT NULL,
  `descripcion_tecnica` varchar(200) NOT NULL,
  `computos_metricos` varchar(255) NOT NULL,
  `estimacion_costo` varchar(45) NOT NULL,
  `proyecto_has_empleado` varchar(85) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de gestion de proyectos';

--
-- Volcado de datos para la tabla `proyecto`
--

INSERT INTO `proyecto` (`codigo_proyecto`, `fecha_planificacion`, `descripcion_tecnica`, `computos_metricos`, `estimacion_costo`, `proyecto_has_empleado`, `estado`) VALUES
('112-222', '2026-07-11 00:00:00', 'SSSSSSSSSSS', '', '', '', 0),
('454-555', '2026-07-17 00:00:00', 'amencdddssa', '150m2222', '50.222,44', '', 0),
('65H-HHH', '2026-07-16 00:00:00', 'jjjjhgtytr', '', '', '', 0),
('666-666', '2026-07-05 03:23:09', 'hahydrere', '4343m2ss', '88.888,88', '', 0),
('BNF-001', '2026-07-02 00:00:00', 'motivaciones', '1353mdsmdaaasd', '47510.00', '', 0),
('BNF-0013', '2026-07-24 00:00:00', 'UUUUUUUUUUU', '777jujjRE', '77.777,77', '', 0),
('BNN-122', '2026-07-02 00:00:00', 'motivaciones', '1203fmsww', '54.100,00', '', 0),
('EEE-EEE', '2026-07-10 00:00:00', '', '', '', '', 0),
('ETF-0012', '2026-07-25 00:00:00', 'aver qlq aa', 'ajajsjjasasd', '80.000,00', '', 0),
('FGT-867', '2026-07-08 23:28:33', 'jjghfffccccf', '888mmgfgvvfgfff', '78885555', '6', 1),
('FRE-001', '2026-07-07 20:19:35', 'Restauracion Vial', '0 m2', '0', 'Sin asignar', 1),
('FTT-RYT', '2026-07-10 00:00:00', 'jghgtht', '', '', '', 0),
('GHH-666', '2026-07-24 00:00:00', 'HHHGTRYRYTR', '', '', '', 0),
('GHT-787', '2026-07-23 00:00:00', 'motivosjodios', '150mw2ww', '858.888,88', '', 0),
('HHH-45445', '2026-07-30 00:00:00', 'motivacionesss', '150m2hsdd', '85.577,74', '', 0),
('HTY-455', '2026-07-03 00:00:00', 'amdhgtterew', 'wq12323', '58.444,44', '', 0),
('IUT-744', '2026-07-04 00:00:00', 'ratatatata', '1203243wds', '74.555,55', '', 0),
('IUY-777', '2026-07-25 00:00:00', 'uytyytttee', '19383m,ww', '78.444,44', '', 0),
('JUH-001', '2026-07-23 03:37:40', 'motivaciones', '150m2wsa', '524444.44', '', 0),
('JUJ-UJJ', '2026-07-17 00:00:00', 'wggtgtewee', '234rfrfer', '58.000,00', '', 0),
('JUU-744', '2026-07-10 00:00:00', 'probando vainas', '123m2221', '50.000,00', '', 0),
('JUY-999', '2026-07-24 00:00:00', 'ooooooiuhujhn', '4554mmh', '87.774,44', '', 0),
('KOU-144', '2026-07-03 00:00:00', 'motivosdwsd', '1402wmww', '50.000,00', '', 0),
('LLL-989', '2026-07-25 00:00:00', 'yyeteeeeqw', '129922ddxd', '84.444,44', '', 0),
('MCO-001', '2026-07-29 14:32:13', 'ARREGLAR VIALIDAD', '105MW CUBICOS', '58222214.44', '', 0),
('MMN-454', '2026-07-24 00:00:00', 'kkkiuhgboo', '88kjin8', '785.555,55', '', 0),
('NGN-101', '2026-07-25 00:00:00', 'amencholes', '188mww22', '777.888,88', '', 0),
('NNT-100', '2026-07-04 00:00:00', 'estabamos trabajamdo', '73492212m2 ff', '47100000', '', 0),
('OOO-L87', '2026-07-18 00:00:00', 'motivcnasw', '192mw22', '78.877,77', '', 0),
('OOO-L879', '2026-07-18 04:14:43', 'motivacionesss', '150mw22w', '787888.89', '', 0),
('OPP-PPE', '2026-07-31 00:00:00', 'motvacionss', '1022mwws', '87.444,44', '', 0),
('OUO-444', '2026-07-10 00:00:00', 'ÑÑJNNJHGHV', '999MJFG', '50000.00', '', 0),
('PPO-777', '2026-07-25 00:00:00', 'jjghbbbbbcvff', '888mhgbgb', '85.554,41', '', 0),
('PPP-502', '2026-07-03 00:00:00', 'motivaciomes', '12wswerdddf3', '50.444,44', '', 0),
('PPP-734', '2026-07-18 00:00:00', 'jajjajahshss', '1222mmsws', '78.888,85', '', 0),
('PPP-788', '2026-07-25 00:00:00', 'motivaciones', '122mwqaw12', '77.716,23', '', 0),
('PYU-777', '2026-07-31 03:22:15', 'noce qie paso', '150m2whdd', '502.544,44', '', 0),
('RGT-022', '2026-07-10 00:00:00', 'AHAHAHHADDD', '12303MWW', '77.777,77', '', 0),
('SBR-4000', '2026-07-01 00:00:00', 'motivos jajaa', '1203mwdd', '80.000,00', '', 0),
('SBR-992', '2026-07-25 00:00:00', 'tecnicas de estt', '1230432ddd', '78.777,77', '', 0),
('TRG-400', '2026-07-03 00:00:00', 'noce que esta pasando aca', '150mw22', '85.777,44', '', 0),
('TRT-999', '2026-07-11 00:00:00', '', '150mwww2', '78.888,88', '', 0),
('TTT-432', '2026-07-17 00:00:00', 'amenchcdddddddd', '122nn dsa', '8.777,77', '', 0),
('UHY-002', '2026-07-04 00:00:00', 'motvcacionesssa', '1204mwmw', '70.558,44', '', 0),
('UJT-666', '2026-07-25 03:42:50', 'camibassss', '1233404mww', '777777.77', '', 0),
('UJU-999', '2026-07-17 00:00:00', 'jjdjdjdd323', '10292mww', '85.555,55', '', 0),
('UUU-454', '2026-07-02 00:00:00', '', '102yee21', '85.222,00', '', 0),
('UUU-888', '2026-07-18 00:00:00', '', '', '', '', 0),
('UYR-599', '2026-07-31 14:25:58', 'tecniocas mejoradas', '150m2sjssw', '854441.14', '', 0),
('UYU-74', '2026-07-02 00:00:00', 'nativo papa', '12023mw cuadrs', '78.555,55', '', 0),
('WWW-WWW', '2026-07-18 00:00:00', 'aaaasqwqw2', '', '', '', 0),
('YHT-222', '2026-07-02 00:00:00', 'motivaciones', '12302mwq', '85.777,77', '', 0),
('YHU-454', '2026-07-25 03:45:45', 'jamon con queso', 'jajsjjs3833', '78777.77', '', 0),
('YTY-122', '2026-07-25 00:00:00', 'cshamoppoo', '174mw2ss', '75.444,44', '', 0),
('YUY-U77', '2026-07-30 00:00:00', 'dtehe22ddcx', '120wsmsw', '87.777,77', '', 0),
('YYU-9838', '2026-07-22 16:49:15', 'mtoyvacioness ', '1230emwq  ', '78444.44', '', 0),
('YYY-78', '2026-07-03 00:00:00', 'motivos de casos', '123554ggg', '78.744,11', '', 0),
('YYY-888', '2026-07-16 00:00:00', 'UGHGHGHGFHF', '', '0.00', '', 0),
('YYY-YYI', '2026-07-05 03:28:52', 'motivosssss', '', '', '', 0),
('YYY-YYY', '2026-07-05 01:51:05', 'segrtghnbyttt', '', '', '', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proyecto_has_maquinaria`
--

CREATE TABLE `proyecto_has_maquinaria` (
  `proyecto_codigo_proyecto` varchar(15) NOT NULL,
  `maquinaria_id_maquinaria` int(11) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `proyecto_has_maquinaria`
--

INSERT INTO `proyecto_has_maquinaria` (`proyecto_codigo_proyecto`, `maquinaria_id_maquinaria`, `estado`) VALUES
('112-222', 1, 1),
('454-555', 1, 1),
('65H-HHH', 2, 1),
('666-666', 1, 1),
('BNF-001', 1, 1),
('BNF-0013', 2, 1),
('BNN-122', 2, 1),
('EEE-EEE', 2, 1),
('ETF-0012', 2, 1),
('FGT-867', 14, 1),
('FTT-RYT', 2, 1),
('GHH-666', 2, 1),
('GHT-787', 1, 1),
('HHH-45445', 1, 1),
('HTY-455', 2, 1),
('IUT-744', 1, 1),
('IUY-777', 2, 1),
('JUH-001', 2, 1),
('JUJ-UJJ', 1, 1),
('JUU-744', 1, 1),
('JUY-999', 2, 1),
('KOU-144', 2, 1),
('LLL-989', 1, 1),
('MCO-001', 2, 1),
('MMN-454', 1, 1),
('NGN-101', 2, 1),
('NNT-100', 2, 1),
('OOO-L87', 1, 1),
('OOO-L879', 1, 1),
('OPP-PPE', 2, 1),
('OUO-444', 2, 1),
('PPO-777', 2, 1),
('PPP-502', 2, 1),
('PPP-734', 2, 1),
('PPP-788', 2, 1),
('PYU-777', 1, 1),
('RGT-022', 2, 1),
('SBR-4000', 1, 1),
('SBR-992', 2, 1),
('TRG-400', 1, 1),
('TRT-999', 2, 1),
('TTT-432', 2, 1),
('UHY-002', 1, 1),
('UJT-666', 2, 1),
('UJU-999', 1, 1),
('UUU-454', 1, 1),
('UUU-888', 2, 1),
('UYR-599', 1, 1),
('UYU-74', 1, 1),
('WWW-WWW', 2, 1),
('YHT-222', 2, 1),
('YHU-454', 1, 1),
('YTY-122', 2, 1),
('YUY-U77', 2, 1),
('YYU-9838', 21, 1),
('YYY-78', 1, 1),
('YYY-888', 2, 1),
('YYY-YYI', 2, 1),
('YYY-YYY', 2, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proyecto_has_solicitudes`
--

CREATE TABLE `proyecto_has_solicitudes` (
  `proyecto_codigo_proyecto` varchar(15) NOT NULL,
  `solicitudes_id_solicitudes` int(11) NOT NULL,
  `solicitudes_persona_id_persona` int(11) NOT NULL,
  `solicitudes_prioridad_id_gestion_prioridad` int(11) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `proyecto_has_solicitudes`
--

INSERT INTO `proyecto_has_solicitudes` (`proyecto_codigo_proyecto`, `solicitudes_id_solicitudes`, `solicitudes_persona_id_persona`, `solicitudes_prioridad_id_gestion_prioridad`, `estado`) VALUES
('112-222', 5, 4, 1, 1),
('454-555', 5, 4, 1, 1),
('BNF-001', 1, 1, 1, 1),
('BNF-0013', 2, 2, 1, 1),
('BNN-122', 1, 1, 1, 1),
('EEE-EEE', 5, 4, 1, 1),
('ETF-0012', 6, 5, 1, 1),
('FGT-867', 1, 1, 1, 1),
('GHH-666', 3, 3, 1, 1),
('GHT-787', 5, 4, 1, 1),
('HHH-45445', 1, 1, 1, 1),
('HTY-455', 1, 1, 1, 1),
('IUT-744', 3, 3, 1, 1),
('IUY-777', 5, 4, 1, 1),
('JUH-001', 5, 4, 1, 1),
('JUJ-UJJ', 1, 1, 1, 1),
('JUU-744', 3, 3, 1, 1),
('JUY-999', 7, 6, 1, 1),
('KOU-144', 5, 4, 1, 1),
('LLL-989', 5, 4, 1, 1),
('MCO-001', 8, 11, 1, 1),
('MMN-454', 3, 3, 1, 1),
('NGN-101', 1, 1, 1, 1),
('NNT-100', 1, 1, 1, 1),
('OOO-L87', 2, 2, 1, 1),
('OOO-L879', 3, 3, 1, 1),
('OPP-PPE', 5, 4, 1, 1),
('OUO-444', 1, 1, 1, 1),
('PPO-777', 1, 1, 1, 1),
('PPP-502', 7, 6, 1, 1),
('PPP-734', 3, 3, 1, 1),
('PPP-788', 7, 6, 1, 1),
('PYU-777', 3, 3, 1, 1),
('RGT-022', 3, 3, 1, 1),
('SBR-4000', 3, 3, 1, 1),
('SBR-992', 5, 4, 1, 1),
('TRG-400', 7, 6, 1, 1),
('TRT-999', 5, 4, 1, 1),
('TTT-432', 3, 3, 1, 1),
('UHY-002', 1, 1, 1, 1),
('UJT-666', 1, 1, 1, 1),
('UJU-999', 7, 6, 1, 1),
('UUU-454', 7, 6, 1, 1),
('UUU-888', 5, 4, 1, 1),
('UYR-599', 1, 1, 1, 1),
('UYU-74', 3, 3, 1, 1),
('YHT-222', 5, 4, 1, 1),
('YHU-454', 7, 6, 1, 1),
('YTY-122', 7, 6, 1, 1),
('YUY-U77', 6, 5, 1, 1),
('YYU-9838', 5, 4, 1, 1),
('YYY-78', 1, 1, 1, 1),
('YYY-888', 5, 4, 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `publicacion`
--

CREATE TABLE `publicacion` (
  `id_publicacion` int(11) NOT NULL,
  `titulo_publicacion` varchar(150) NOT NULL,
  `nombre_responsable` varchar(45) NOT NULL,
  `tipo_publicacion` varchar(15) NOT NULL,
  `fecha_publicacion` datetime NOT NULL COMMENT 'Tabla de gestion de publicaciones',
  `informe_avance_obra_id_informe` int(11) NOT NULL,
  `cuerpo_publicacion` text DEFAULT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recurso_obra`
--

CREATE TABLE `recurso_obra` (
  `id_recurso` int(11) NOT NULL,
  `descripcion_material` varchar(45) NOT NULL,
  `cantidad_material` decimal(5,2) NOT NULL,
  `unidad_material` varchar(20) NOT NULL,
  `informe_avance_obra_id_informe` int(11) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reporte`
--

CREATE TABLE `reporte` (
  `id_reporte` int(11) NOT NULL,
  `fecha` datetime NOT NULL,
  `ubicacion` varchar(255) NOT NULL,
  `solicitudes_pendientes` int(11) NOT NULL,
  `solicitudes_procesadas` int(11) NOT NULL,
  `cantidad_total_solicitudes` int(11) NOT NULL,
  `cantidad_comunidades_atendidas` int(11) NOT NULL,
  `informe_avance_obra_id_informe` int(11) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `respaldo_bd`
--

CREATE TABLE `respaldo_bd` (
  `id_respaldo` int(11) NOT NULL,
  `nombre_archivo` varchar(255) NOT NULL,
  `tamano` bigint(20) NOT NULL DEFAULT 0,
  `descripcion` varchar(255) DEFAULT '',
  `fecha_respaldo` timestamp NOT NULL DEFAULT current_timestamp(),
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `respaldo_bd`
--

INSERT INTO `respaldo_bd` (`id_respaldo`, `nombre_archivo`, `tamano`, `descripcion`, `fecha_respaldo`, `estado`) VALUES
(1, 'respaldo_20260707_212053.sql', 45223, 'alavaresssss', '2026-07-08 05:20:54', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `semaforo`
--

CREATE TABLE `semaforo` (
  `id_semaforo` int(11) NOT NULL,
  `estatus_semaforo` varchar(20) NOT NULL,
  `color` enum('VERDE','AMARILLO','ROJO') NOT NULL,
  `descripcion` varchar(50) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `semaforo`
--

INSERT INTO `semaforo` (`id_semaforo`, `estatus_semaforo`, `color`, `descripcion`, `estado`) VALUES
(1, 'Activo', 'VERDE', 'Semaforo generado automaticamente', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `solicitudes`
--

CREATE TABLE `solicitudes` (
  `id_solicitudes` int(11) NOT NULL,
  `fecha` datetime NOT NULL,
  `tipo_solicitud` varchar(45) NOT NULL,
  `estatus_solicitud` varchar(15) NOT NULL,
  `problematica` varchar(255) NOT NULL,
  `persona_id_persona` int(11) NOT NULL,
  `prioridad_id_gestion_prioridad` int(11) NOT NULL,
  `estado` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla general de las solicitudes';

--
-- Volcado de datos para la tabla `solicitudes`
--

INSERT INTO `solicitudes` (`id_solicitudes`, `fecha`, `tipo_solicitud`, `estatus_solicitud`, `problematica`, `persona_id_persona`, `prioridad_id_gestion_prioridad`, `estado`) VALUES
(1, '2026-06-15 16:38:02', 'Particular', 'En Proceso', '[Servicios Básicos (Agua, Luz, Gas)] Haciendo rgistro de prueba mortadela', 1, 1, 1),
(2, '2026-06-15 16:40:32', 'Comunidad', 'Completada', '[Salud y Asistencia Médica] hhhhhhhhhuuuuuuuuuuuuuuuuu  mantequilla', 2, 1, 1),
(3, '2026-06-15 16:42:00', 'Institucion', 'En Proceso', '[Servicios Básicos (Agua, Luz, Gas)] gggggggggggggggggggggggggggggggggggggg jamon', 3, 1, 1),
(5, '2026-06-15 16:46:00', 'Comunidad', 'En Proceso', '[Servicios Básicos (Agua, Luz, Gas)] hueco en la avenida donde salen aguas negras', 4, 1, 1),
(6, '2026-06-15 19:07:05', 'Comunidad', 'Completada', '[Infraestructura y Vialidad] aaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 5, 1, 1),
(7, '2026-06-16 17:58:23', 'Comunidad', 'En Proceso', '[Infraestructura y Vialidad] Acondicionamiento vial', 6, 1, 1),
(8, '2026-07-05 14:31:15', 'Institucion', 'En Proceso', '[Infraestructura y Vialidad] LA ESCUELA NECESITA MEJORAS', 11, 1, 1);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_evidencia_informe`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `vista_evidencia_informe` (
`id_evidencia` int(11)
,`fotos` varchar(45)
,`url_archivos` varchar(90)
,`fecha_registro` datetime
,`etapa` enum('antes','durante','despues')
,`estado` tinyint(4)
,`id_informe` int(11)
,`fecha_informe` datetime
,`tipo_informe` varchar(30)
,`estado_informe` tinyint(4)
);

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
-- Indices de la tabla `respaldo_bd`
--
ALTER TABLE `respaldo_bd`
  ADD PRIMARY KEY (`id_respaldo`);

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
  MODIFY `id_cargo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `comunidad`
--
ALTER TABLE `comunidad`
  MODIFY `id_comunidad` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `contratacion`
--
ALTER TABLE `contratacion`
  MODIFY `id_contratacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `empleados`
--
ALTER TABLE `empleados`
  MODIFY `id_empleados` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `evidencia`
--
ALTER TABLE `evidencia`
  MODIFY `id_evidencia` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `gravedad_obra`
--
ALTER TABLE `gravedad_obra`
  MODIFY `id_gravedad` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `informe_avance_obra`
--
ALTER TABLE `informe_avance_obra`
  MODIFY `id_informe` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `inspeccion`
--
ALTER TABLE `inspeccion`
  MODIFY `id_inspeccion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `institucion`
--
ALTER TABLE `institucion`
  MODIFY `id_institucion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `maquinaria`
--
ALTER TABLE `maquinaria`
  MODIFY `id_maquinaria` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT de la tabla `obra`
--
ALTER TABLE `obra`
  MODIFY `id_obra` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `particular`
--
ALTER TABLE `particular`
  MODIFY `id_particular` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `persona`
--
ALTER TABLE `persona`
  MODIFY `id_persona` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `prioridad`
--
ALTER TABLE `prioridad`
  MODIFY `id_gestion_prioridad` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `publicacion`
--
ALTER TABLE `publicacion`
  MODIFY `id_publicacion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reporte`
--
ALTER TABLE `reporte`
  MODIFY `id_reporte` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `respaldo_bd`
--
ALTER TABLE `respaldo_bd`
  MODIFY `id_respaldo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `semaforo`
--
ALTER TABLE `semaforo`
  MODIFY `id_semaforo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `solicitudes`
--
ALTER TABLE `solicitudes`
  MODIFY `id_solicitudes` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

-- --------------------------------------------------------

--
-- Estructura para la vista `vista_evidencia_informe`
--
DROP TABLE IF EXISTS `vista_evidencia_informe`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_evidencia_informe`  AS SELECT `e`.`id_evidencia` AS `id_evidencia`, `e`.`fotos` AS `fotos`, `e`.`url_archivos` AS `url_archivos`, `e`.`fecha_registro` AS `fecha_registro`, `e`.`etapa` AS `etapa`, `e`.`estado` AS `estado`, `i`.`id_informe` AS `id_informe`, `i`.`fecha` AS `fecha_informe`, `i`.`tipo_informe` AS `tipo_informe`, `i`.`estado` AS `estado_informe` FROM (`evidencia` `e` left join `informe_avance_obra` `i` on(`e`.`etapa` = 'antes' and `i`.`evidencia_antes` like concat('%',`e`.`id_evidencia`,'%') or `e`.`etapa` = 'durante' and `i`.`evidencia_durante` like concat('%',`e`.`id_evidencia`,'%') or `e`.`etapa` = 'despues' and `i`.`evidencia_despues` like concat('%',`e`.`id_evidencia`,'%'))) WHERE `e`.`estado` = 1 ;

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
