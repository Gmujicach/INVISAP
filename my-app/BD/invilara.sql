-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 09-07-2026 a las 04:03:14
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
-- Estructura de tabla para la tabla `administracion_respaldos`
--

CREATE TABLE `administracion_respaldos` (
  `id_respaldo` int NOT NULL,
  `nombre_archivo` varchar(255) NOT NULL,
  `tamano` bigint NOT NULL DEFAULT '0',
  `descripcion` varchar(255) DEFAULT '',
  `fecha_respaldo` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
  `obra_gestionar_proyectos_codigo_proyecto` varchar(15) NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `avance`
--

INSERT INTO `avance` (`id_avance`, `porcentaje_avance`, `descripcion`, `gerente`, `fecha_avance`, `obra_id_obra`, `obra_semaforo_id_semaforo`, `obra_contratacion_id_contratacion`, `obra_gestionar_proyectos_codigo_proyecto`, `estado`) VALUES
('0780c1c2a553', 67, 'Carretera Nacional hay que reparar', '6', '2026-07-04', 24, 24, 1, 'FRE-001', 1),
('098264b7eef9', 50, 'Test obs', '1', '2026-07-05', 24, 24, 1, 'FRE-001', 1),
('0a9a55ead39b', 100, 'En la Luis Hurtado se llevo a cabo la restaur', '5', '2026-07-01', 4, 4, 1, 'FRE-001', 1),
('0c8eb3a83706', 28, 'hay que asfaltar equisde', '1', '2026-07-05', 24, 24, 1, 'FRE-001', 1),
('113a14ea70b7', 50, 'reparar la Comunidad', '6', '2026-07-05', 24, 24, 1, 'FRE-001', 1),
('15e07374f523', 64, 'En la comunidad Nuevo horizonte', '6', '2026-07-02', 24, 24, 1, 'FRE-001', 1),
('1c039681733a', 90, 'Updated', '1', '2026-07-05', 24, 24, 1, 'FRE-001', 1),
('1df486355cd0', 100, 'En la Luis Hurtado se llevo a cabo la restaur', '5', '2026-07-01', 8, 8, 1, 'FRE-001', 1),
('1df6b8f707d0', 25, 'Prueba', '1', '2026-07-01', 19, 19, 1, 'FRE-001', 1),
('22a8d98cd659', 100, 'En la Luis Hurtado se arreglo la via', '1', '2026-07-01', 18, 18, 1, 'FRE-001', 1),
('2eb5dc872fcf', 100, 'En la Luis Hurtado se llevo a cabo la restaur', '5', '2026-07-01', 11, 11, 1, 'FRE-001', 1),
('3d03370f9b8b', 100, 'En la Luis Hurtado se arreglo la via', '1', '2026-07-01', 13, 13, 1, 'FRE-001', 1),
('4881290ca4c3', 7, 'hay que reparar en Av. Intercomunal', '6', '2026-07-04', 24, 24, 1, 'FRE-001', 1),
('49143e692fde', 7, 'hay que reparar en Av. Intercomunal', '6', '2026-07-04', 24, 24, 1, 'FRE-001', 1),
('5e48bd43ec2b', 100, 'En la Luis Hurtado se arreglo la via', '1', '2026-07-01', 17, 17, 1, 'FRE-001', 1),
('6d2ff375fef8', 30, 'Test', '1', '2026-07-05', 24, 24, 1, 'FRE-001', 1),
('7317ea5dba7d', 44, 'Sector La Aguada se necesita asfaltar', '1', '2026-07-04', 24, 24, 1, 'FRE-001', 1),
('752f90f2b837', 100, 'en la urbanizacion hay que asfaltar', '1', '2026-07-04', 24, 24, 1, 'FRE-001', 1),
('7a4e67e5c2ce', 40, 'Siguiendo Las Instrucciones del gobernador Cm', '1', '2026-07-06', 24, 24, 1, 'FRE-001', 1),
('7abe4665215b', 100, 'En la Luis Hurtado se arreglo la via', '1', '2026-07-01', 16, 16, 1, 'FRE-001', 1),
('80e3115d8f95', 44, 'Sector La Aguada se necesita asfaltar', '1', '2026-07-04', 24, 24, 1, 'FRE-001', 1),
('83bc77674b51', 100, 'En la Luis Hurtado se arreglo la via', '1', '2026-07-01', 15, 15, 1, 'FRE-001', 1),
('8e85d8b4f2a0', 25, 'Test', '1', '2026-07-05', 24, 24, 1, 'FRE-001', 1),
('9214ff06713f', 100, 'En la Luis Hurtado se llevo a cabo la restaur', '5', '2026-07-01', 7, 7, 1, 'FRE-001', 1),
('942e517e2048', 38, 'En Tamaca hay que asfaltar', '1', '2026-07-04', 24, 24, 1, 'FRE-001', 1),
('a09e4dfbbe8c', 64, 'En la comunidad Nuevo horizonte', '6', '2026-07-02', 23, 23, 1, 'FRE-001', 1),
('a12e302ae883', 100, 'En la Luis Hurtado se arreglo la via', '1', '2026-07-01', 14, 14, 1, 'FRE-001', 1),
('ad20d3759114', 13, 'En Av. Intercomunal se hizo un asfaltado y em', '5', '2026-07-03', 24, 24, 1, 'FRE-001', 1),
('ae8c50e964e9', 50, 'reparar la Comunidad', '6', '2026-07-05', 24, 24, 1, 'FRE-001', 1),
('b07c92e0e7ff', 13, 'En Av. Intercomunal se hizo un asfaltado y em', '5', '2026-07-03', 24, 24, 1, 'FRE-001', 1),
('b0d8247b2d01', 100, 'en Morán hay que reparar', '1', '2026-07-06', 24, 24, 1, 'FRE-001', 1),
('b25c0cb85384', 16, 'En san francisco se hizo un bache', '6', '2026-07-01', 21, 21, 1, 'FRE-001', 1),
('b70e531c3f5f', 30, 'En Cabudares nos informaron de que no cargan ', '5', '2026-06-30', 2, 2, 1, 'FRE-001', 1),
('b7b4eb5ecb30', 100, 'En la Luis Hurtado se llevo a cabo la restaur', '5', '2026-07-01', 3, 3, 1, 'FRE-001', 1),
('b7c87235e5e2', 16, 'En san francisco se hizo un bache', '6', '2026-07-01', 20, 20, 1, 'FRE-001', 1),
('b7ed15f05b88', 100, 'En la Luis Hurtado se llevo a cabo la restaur', '5', '2026-07-01', 9, 9, 1, 'FRE-001', 1),
('bc2a0329e738', 56, 'Hay que reparar algo', '10', '2026-07-07', 24, 24, 1, 'FRE-001', 1),
('beda52ea9bd1', 50, 'Test obs', '1', '2026-07-05', 24, 24, 1, 'FRE-001', 1),
('bf0e7abdad06', 93, 'En el Cují, en la Calle 3 se realizara un asf', '5', '2026-07-04', 24, 24, 1, 'FRE-001', 1),
('c0ecec782081', 38, 'reparaciones en Cabudares', '1', '2026-07-03', 24, 24, 1, 'FRE-001', 1),
('c46ec2a9eb43', 39, 'En el Sector La Aguada se realizaran reparaci', '10', '2026-07-07', 24, 24, 1, 'FRE-001', 1),
('d159b72e9c16', 28, 'En la Salle se comenzo a hacer una obra', '1', '2026-07-04', 24, 24, 1, 'FRE-001', 1),
('d169eb15ef98', 100, 'En la Luis Hurtado se llevo a cabo la restaur', '5', '2026-07-01', 12, 12, 1, 'FRE-001', 1),
('d3c620ff34ad', 100, 'En la Luis Hurtado se llevo a cabo la restaur', '5', '2026-07-01', 5, 5, 1, 'FRE-001', 1),
('d9b6d8dfb228', 38, 'reparaciones en Iribarren Av. Venezuela', '1', '2026-07-03', 24, 24, 1, 'FRE-001', 1),
('dd708c7466cf', 93, 'En el Cují, en la Calle 3 se realizara un asf', '5', '2026-07-04', 24, 24, 1, 'FRE-001', 1),
('e316f1191384', 100, 'En la Luis Hurtado se llevo a cabo la restaur', '5', '2026-07-01', 6, 6, 1, 'FRE-001', 1),
('e862a33d0c7c', 100, 'en la urbanizacion hay que asfaltar', '1', '2026-07-04', 24, 24, 1, 'FRE-001', 1),
('f220e9404f00', 100, 'En la Luis Hurtado se llevo a cabo la restaur', '5', '2026-07-01', 10, 10, 1, 'FRE-001', 1),
('fa7f402d9b98', 13, 'En Av. Intercomunal se hizo un asfaltado y em', '5', '2026-07-03', 24, 24, 1, 'FRE-001', 1),
('fb5af05a3a48', 25, 'Prueba', '1', '2026-07-01', 22, 22, 1, 'FRE-001', 1),
('fef7ab9d0883', 69, 'Se esta restaurando la via de Pueblo Nuevo', '6', '2026-06-30', 1, 1, 1, 'FRE-001', 1);

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
  `id_comunidad` int NOT NULL,
  `nombre_comunidad` varchar(100) NOT NULL,
  `ambito` varchar(45) NOT NULL,
  `sector` varchar(45) NOT NULL,
  `persona_id_persona` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
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

--
-- Volcado de datos para la tabla `contratacion`
--

INSERT INTO `contratacion` (`id_contratacion`, `descripcion`, `empresa_ganadora`, `numero_contrato`, `monto`, `fecha_inicio_procedimiento`, `fecha_adjudicacion`, `tipo_contrato`, `modalidad`, `objeto`, `observacion`, `fecha_registro`, `empresa_rif`, `estado`) VALUES
(1, 'Hola', 'Polar', '12', '12 Dolares', '2026-06-17 00:00:00', '2026-06-24 00:00:00', 'Anual', 'Fisica', 'Afaltado', 'Calles irregulares', '2026-06-17 00:00:00', '12', 0),
(2, 'En la Empresa del señor Pereira se ha solicitado una restauracion en frente de su negocio', 'Empresa Pereira', 'FLR-23580', 'BS 31.745.715,41', '2026-06-24 00:00:00', '2026-08-12 00:00:00', 'Contrato de Obra', 'Concurso Abierto', 'Ejecución de Obras', 'Acondicionamiento', '2026-06-24 00:00:00', 'J-714712571', 0);

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
-- Volcado de datos para la tabla `empleados`
--

INSERT INTO `empleados` (`id_empleados`, `nombre_empleado`, `cargo`, `fecha_ingreso`, `gerencia_asignada`, `persona_id_persona`, `estado`) VALUES
(1, 'Juan Carlos Perez Hernandez', 'Inspector', '2026-06-20', 'Obras', 7, 1),
(2, 'Cesilia  del Carmen Suarez', 'Recepcionista', '2026-06-20', 'Atención al Ciudadano', 9, 1),
(3, 'Maria del Carmen Suarez', 'Asistente', '2026-06-20', 'Comunicaciones', 9, 1),
(5, 'Carlos Ramírez Inspector', 'Inspector', '2026-06-22', 'Obras Públicas', 1, 1),
(6, 'Alejandro Mejia Bautista', 'Inspector', '2026-06-08', 'Gerencia de Obras', 12, 1),
(7, 'Elena María Riera', 'Proyectista', '2017-02-13', 'Gerencia de Proyectos', 13, 1),
(8, 'Javier Eduardo Páez', 'Proyectista', '2021-11-14', 'Gerencia de Proyectos', 14, 1),
(9, 'Sofía Alexandra Guedez', 'Asistente', '2023-08-17', 'Atencion al Ciudadano', 15, 1),
(10, 'José Gregorio Montes', 'Inspector', '2026-07-01', 'Gerencias de Obras', 12, 1);

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

--
-- Volcado de datos para la tabla `empresa`
--

INSERT INTO `empresa` (`rif`, `nombre_empresa`, `telefono`, `domicilio_fiscal`, `estado`) VALUES
('12', 'Polar', '04122212121', 'Calle 13c', 0),
('J-714712571', 'Empresa Pereira', '0414-5125412', 'Calle 14, Sector Centro', 1);

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
-- Volcado de datos para la tabla `evidencia`
--

INSERT INTO `evidencia` (`id_evidencia`, `fotos`, `url_archivos`, `fecha_registro`, `estado`, `etapa`) VALUES
(12, 'WhatsApp Image 2026-06-23 at 11.53.09 AM (2).', 'uploads/evidencias/596546b1d461_WhatsApp_Image_2026-06-23_at_11_53_09_AM_2.jpg', '2026-06-30 18:19:23', 1, 'antes'),
(13, 'WhatsApp Image 2026-06-23 at 11.53.08 AM (2).', 'uploads/evidencias/1f659ea9faeb_WhatsApp_Image_2026-06-23_at_11_53_08_AM_2.jpg', '2026-06-30 18:19:23', 1, 'durante'),
(14, 'WhatsApp Image 2026-06-23 at 11.53.18 AM (1).', 'uploads/evidencias/58a2b979b634_WhatsApp_Image_2026-06-23_at_11_53_18_AM_1.jpg', '2026-06-30 18:19:23', 1, 'despues'),
(15, 'WhatsApp Image 2026-06-18 at 2.44.38 PM (4).j', 'uploads/evidencias/5e75f66e31dd_WhatsApp_Image_2026-06-18_at_2_44_38_PM_4.jpg', '2026-06-30 19:34:59', 1, 'durante'),
(16, 'WhatsApp Image 2026-06-18 at 2.44.38 PM.jpeg', 'uploads/evidencias/5aff3e056a00_WhatsApp_Image_2026-06-18_at_2_44_38_PM.jpg', '2026-06-30 19:34:59', 1, 'durante'),
(17, 'WhatsApp Image 2026-06-23 at 11.53.16 AM (2).', 'uploads/evidencias/3ca6bdacc414_WhatsApp_Image_2026-06-23_at_11_53_16_AM_2.jpg', '2026-06-30 19:34:59', 1, 'durante'),
(18, 'WhatsApp Image 2026-06-23 at 11.53.16 AM (3).', 'uploads/evidencias/60474e154639_WhatsApp_Image_2026-06-23_at_11_53_16_AM_3.jpg', '2026-06-30 19:34:59', 1, 'durante'),
(19, 'WhatsApp Image 2026-06-23 at 11.53.09 AM (1).', 'uploads/evidencias/6d82d404846d_WhatsApp_Image_2026-06-23_at_11_53_09_AM_1.jpg', '2026-07-02 12:39:56', 1, 'antes'),
(20, 'WhatsApp Image 2026-06-23 at 11.53.09 AM (3).', 'uploads/evidencias/58992d937a7b_WhatsApp_Image_2026-06-23_at_11_53_09_AM_3.jpg', '2026-07-02 12:39:56', 1, 'antes'),
(21, 'WhatsApp Image 2026-06-23 at 11.53.09 AM.jpeg', 'uploads/evidencias/30890868dd1a_WhatsApp_Image_2026-06-23_at_11_53_09_AM.jpg', '2026-07-02 12:39:56', 1, 'antes'),
(22, 'WhatsApp Image 2026-06-23 at 11.53.10 AM.jpeg', 'uploads/evidencias/6c30a9cf957a_WhatsApp_Image_2026-06-23_at_11_53_10_AM.jpg', '2026-07-02 12:39:56', 1, 'antes'),
(23, 'WhatsApp Image 2026-06-23 at 11.53.10 AM (2).', 'uploads/evidencias/cdcc3fdbc656_WhatsApp_Image_2026-06-23_at_11_53_10_AM_2.jpg', '2026-07-02 12:41:58', 1, 'despues'),
(24, 'WhatsApp Image 2026-06-23 at 11.53.12 AM.jpeg', 'uploads/evidencias/813a552771db_WhatsApp_Image_2026-06-23_at_11_53_12_AM.jpg', '2026-07-02 12:41:58', 1, 'despues'),
(25, 'WhatsApp Image 2026-06-23 at 11.53.16 AM.jpeg', 'uploads/evidencias/e7ff13fd5448_WhatsApp_Image_2026-06-23_at_11_53_16_AM.jpg', '2026-07-02 12:41:58', 1, 'despues'),
(26, 'WhatsApp Image 2026-06-23 at 11.53.18 AM.jpeg', 'uploads/evidencias/4f11bdb292bc_WhatsApp_Image_2026-06-23_at_11_53_18_AM.jpg', '2026-07-02 12:41:58', 1, 'despues'),
(27, 'WhatsApp Image 2026-06-23 at 11.53.17 AM (1).', 'uploads/evidencias/7c33d9c267d2_WhatsApp_Image_2026-06-23_at_11_53_17_AM_1.jpg', '2026-07-07 20:21:59', 1, 'antes'),
(28, 'WhatsApp Image 2026-06-23 at 11.53.18 AM (2).', 'uploads/evidencias/d9b8ae567bd1_WhatsApp_Image_2026-06-23_at_11_53_18_AM_2.jpg', '2026-07-07 20:21:59', 1, 'durante'),
(29, 'WhatsApp Image 2026-06-23 at 11.53.18 AM.jpeg', 'uploads/evidencias/9b211391d781_WhatsApp_Image_2026-06-23_at_11_53_18_AM.jpg', '2026-07-07 20:21:59', 1, 'despues'),
(30, 'WhatsApp Image 2026-06-23 at 11.53.19 AM.jpeg', 'uploads/evidencias/a77ab3b0c6ca_WhatsApp_Image_2026-06-23_at_11_53_19_AM.jpg', '2026-07-07 20:21:59', 1, 'antes');

--
-- Disparadores `evidencia`
--
DELIMITER $$
CREATE TRIGGER `trg_limite_evidencias` BEFORE INSERT ON `evidencia` FOR EACH ROW BEGIN
    DECLARE total INT;
    SELECT COUNT(*) INTO total FROM evidencia WHERE estado = 1;
    IF total >= 5 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Límite de evidencias alcanzado (máximo 5).';
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

--
-- Volcado de datos para la tabla `gravedad_obra`
--

INSERT INTO `gravedad_obra` (`id_gravedad`, `nivel_gravedad`, `criticidad`, `estado`) VALUES
(1, 'baja', '0.24', 1),
(2, 'Media', '0.52', 1);

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
  `evidencia_antes` varchar(50) NOT NULL,
  `evidencia_durante` varchar(50) NOT NULL,
  `evidencia_despues` varchar(50) NOT NULL,
  `avance_id_avance` varchar(45) NOT NULL,
  `estado_registro` tinyint NOT NULL DEFAULT '1' COMMENT '1=Activo, 0=Inactivo (borrado lógico)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de informes de avances de obras';

--
-- Volcado de datos para la tabla `informe_avance_obra`
--

INSERT INTO `informe_avance_obra` (`id_informe`, `fecha`, `estado`, `poblacion_beneficiada`, `tipo_informe`, `evidencia_antes`, `evidencia_durante`, `evidencia_despues`, `avance_id_avance`, `estado_registro`) VALUES
(1, '2026-06-30 21:13:31', 'Aprobado', 'Pueblo Nuevo Avenida 4 con Calle 5', 'Menor', '12', '15', '', 'fef7ab9d0883', 1),
(2, '2026-06-30 22:12:15', 'En Ejecucion', 'Cabudares', 'Mayor', '12', '16', '', 'b70e531c3f5f', 1),
(18, '2026-07-01 22:31:07', 'Culminado', 'Luis Hurtado', 'Ficha Inspeccion Tecnica', '12', '17', '14', '22a8d98cd659', 1),
(23, '2026-07-02 20:28:32', 'En Ejecucion', 'Comunidad Nuevo Horizonte en Iribarren', 'Avance Mensual', '21', '18', '24', 'a09e4dfbbe8c', 1),
(25, '2026-07-03 00:12:09', 'En Ejecucion', 'Palavecino Av. Intercomunal, Conjunto Res', 'Menor', '19', '16', '', 'ad20d3759114', 1),
(26, '2026-07-03 00:12:14', 'En Ejecucion', 'Palavecino Av. Intercomunal, Conjunto Res', 'Menor', '19', '16', '', 'b07c92e0e7ff', 1),
(28, '2026-07-03 02:17:51', 'En Ejecucion', 'Iribarren Av. Venezuela, Urb. Fundalara', 'Mayor', '', '', '', 'd9b6d8dfb228', 1),
(29, '2026-07-03 02:18:12', 'En Ejecucion', 'Cabudare Urb. La Rosaleda Calle 5 Casa 12', 'Menor', '', '', '', 'c0ecec782081', 1),
(30, '2026-07-04 17:34:27', 'Aprobado', 'La Salle Avenida 4 con Calle 3', 'Mayor', '19,20', '17', '', 'd159b72e9c16', 1),
(33, '2026-07-04 20:14:59', 'En Ejecucion', 'Urb. El Cují, Calle 3, Lote 14', 'Avance Mensual', '21', '18', '', 'bf0e7abdad06', 1),
(34, '2026-07-04 21:13:37', 'En Ejecucion', 'Tamaca Urb. El Recreo, Calle Principal, Casa', 'Avance Mensual', '19', '16,17', '', '942e517e2048', 1),
(35, '2026-07-04 21:17:41', 'Aprobado', 'José Gregorio Bastidas Av. Intercomunal', 'Ficha Inspeccion Tecnica', '19,21,22', '15,16', '', '49143e692fde', 1),
(37, '2026-07-04 22:00:18', 'Aprobado', 'Juares Sector La Aguada, Calle Principal', 'Menor', '19,20,21,22', '15,17,16,18', '', '7317ea5dba7d', 1),
(38, '2026-07-04 22:00:40', 'Aprobado', 'Juares Sector La Aguada, Calle Principal', 'Menor', '20,21,22', '16,18', '', '80e3115d8f95', 1),
(39, '2026-07-04 23:02:06', 'Culminado', 'Urb. La Piedad, Manzana C, Casa 15', 'Ficha Inspeccion Tecnica', '19,20,21,22,12', '15,16,17,18,13', '23,24,25,26,14', 'e862a33d0c7c', 1),
(40, '2026-07-04 23:07:05', 'Culminado', 'Urb. La Piedad, Manzana C, Casa 15', 'Ficha Inspeccion Tecnica', '19,20,21,22,12', '15,16,17,18,13', '23,24,25,26,14', '752f90f2b837', 1),
(41, '2026-07-04 23:36:56', 'En Ejecucion', 'Carretera Nacional, Caserío El Copey', 'Avance Mensual', '', '', '', '0780c1c2a553', 1),
(42, '2026-07-05 00:28:47', 'En Ejecucion', 'El Tocuyo Av. Rotaria, Sector La Montañita', 'Avance Mensual', '20,21', '16,15', '', '0c8eb3a83706', 1),
(43, '2026-07-05 01:00:13', 'Aprobado', 'para la Comunidad santa la Osa', 'Menor', '20,21', '18,13', '23', 'ae8c50e964e9', 1),
(50, '2026-07-06 04:24:19', 'En Ejecucion', 'Urb. La Piedad, Manzana C, Casa 15', 'Ficha Inspeccion Tecnica', '20', '18,17', '', '7a4e67e5c2ce', 1),
(51, '2026-07-06 19:53:13', 'Culminado', 'Av. Rotaria, Sector La Montañita en Morán', 'Mayor', '19,21,20', '15,16,17', '', 'b0d8247b2d01', 1),
(52, '2026-07-07 00:44:24', 'En Ejecucion', 'Sector La Aguada, Calle Principal 20 personas', 'Menor', '19,12,22', '', '', 'c46ec2a9eb43', 1),
(53, '2026-07-07 20:04:11', 'En Ejecucion', 'La Salle por donde los edificios', 'Avance Mensual', '19,20,21', '18,13', '', 'bc2a0329e738', 0);

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
  `evidencia_id_evidencia` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Disparadores `inspeccion`
--
DELIMITER $$
CREATE TRIGGER `trg_cambiar_estatus_solicitud` AFTER INSERT ON `inspeccion` FOR EACH ROW BEGIN
    UPDATE solicitudes 
    SET estatus_solicitud = 'En Proceso'
    WHERE id_solicitudes = NEW.obra_contratacion_id_contratacion;
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

--
-- Volcado de datos para la tabla `institucion`
--

INSERT INTO `institucion` (`id_institucion`, `nombre_representante`, `razon_social`, `persona_id_persona`, `estado`) VALUES
(2, 'María Rodríguez', 'U.E.N. Lisandro Alvarado', 16, 1);

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

--
-- Volcado de datos para la tabla `maquinaria`
--

INSERT INTO `maquinaria` (`id_maquinaria`, `nombre_maquinaria`, `tipo_maquinaria`, `estado`) VALUES
(1, 'Excavadora CAT 320', 'Pesada', 1),
(2, 'Retroexcavadora', 'Pesada', 1),
(3, 'Motoniveladora', 'Pesada', 1),
(4, 'Bulldozer (Topadora)', 'Pesada', 1),
(5, 'Compactador Rodillo liso', 'Pesada', 1),
(6, 'Pavimentadora (Terminadora de asfalto)', 'Pesada', 1),
(7, 'Fresadora de pavimento', 'Pesada', 1),
(8, 'Mototraílla (Scraper)', 'Pesada', 1),
(9, 'Mini cargadora (tipo Bobcat)', 'Liviana', 1),
(10, 'Placa vibratoria Wacker Neuson', 'Liviana', 1),
(11, 'Pisón vibratorio (Canguro)', 'Liviana', 1),
(12, 'Cortadora de pavimento (Suelo/Asfalto)', 'Liviana', 1),
(13, 'Generador eléctrico', 'Liviana', 1),
(14, 'Barredora mecánica', 'Liviana', 1),
(15, 'Motosierra', 'Herramienta', 1),
(16, 'Taladro percutor / Rotomartillo', 'Herramienta', 1),
(17, 'Esmeriladora', 'Herramienta', 1),
(18, 'Estación total Leica TS06', 'Herramienta', 1),
(19, 'Palas', 'Herramienta', 1),
(20, 'Picos', 'Herramienta', 1),
(21, 'rastrillos', 'Herramienta', 1),
(22, 'macetas', 'Herramienta', 1),
(23, 'Camión volquete (Dúmper) Mack Granite', 'Vehículo', 1),
(24, 'Camión cisterna', 'Vehículo', 1),
(25, 'Camión hormigonera (Mixer)', 'Vehículo', 1),
(26, 'Camión plataforma', 'Vehículo', 0);

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
  `gestionar_proyectos_codigo_proyecto` varchar(15) NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de las inspecciones';

--
-- Volcado de datos para la tabla `obra`
--

INSERT INTO `obra` (`id_obra`, `titulo_obra`, `ubicacion_obra`, `periodo_ejecucion`, `fecha_inicio`, `fecha_fin`, `mediciones_obra`, `valuaciones`, `modificaciones_contrato`, `certificaciones_obras_ejecutadas`, `numero_contrato`, `porcentaje_avance_obra`, `semaforo_id_semaforo`, `contratacion_id_contratacion`, `gestionar_proyectos_codigo_proyecto`, `estado`) VALUES
(1, 'Obra Generada', 'Sin ubicacion', 1, '2026-06-30', '2026-06-30', 'N/A', 'N/A', 'N/A', 0, 'N/A', 69, 1, 1, 'FRE-001', 1),
(2, 'Obra Generada', 'Sin ubicacion', 1, '2026-06-30', '2026-06-30', 'N/A', 'N/A', 'N/A', 0, 'N/A', 30, 2, 1, 'FRE-001', 1),
(3, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 3, 1, 'FRE-001', 1),
(4, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 4, 1, 'FRE-001', 1),
(5, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 5, 1, 'FRE-001', 1),
(6, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 6, 1, 'FRE-001', 1),
(7, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 7, 1, 'FRE-001', 1),
(8, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 8, 1, 'FRE-001', 1),
(9, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 9, 1, 'FRE-001', 1),
(10, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 10, 1, 'FRE-001', 1),
(11, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 11, 1, 'FRE-001', 1),
(12, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 12, 1, 'FRE-001', 1),
(13, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 13, 1, 'FRE-001', 1),
(14, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 14, 1, 'FRE-001', 1),
(15, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 15, 1, 'FRE-001', 1),
(16, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 16, 1, 'FRE-001', 1),
(17, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 17, 1, 'FRE-001', 1),
(18, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 100, 18, 1, 'FRE-001', 1),
(19, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 25, 19, 1, 'FRE-001', 1),
(20, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 16, 20, 1, 'FRE-001', 1),
(21, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 16, 21, 1, 'FRE-001', 1),
(22, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-01', '2026-07-01', 'N/A', 'N/A', 'N/A', 0, 'N/A', 25, 22, 1, 'FRE-001', 1),
(23, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-02', '2026-07-02', 'N/A', 'N/A', 'N/A', 0, 'N/A', 64, 23, 1, 'FRE-001', 1),
(24, 'Obra Generada', 'Sin ubicacion', 1, '2026-07-02', '2026-07-02', 'N/A', 'N/A', 'N/A', 0, 'N/A', 64, 24, 1, 'FRE-001', 1);

--
-- Disparadores `obra`
--
DELIMITER $$
CREATE TRIGGER `actualizar_semaforo_obra` BEFORE UPDATE ON `obra` FOR EACH ROW BEGIN
    -- Semáforo: 1=Verde (0-10%), 2=Amarillo (11-89%), 3=Rojo (90-100%)
    IF NEW.porcentaje_avance_obra >= 90 THEN
        SET NEW.semaforo_id_semaforo = 3; -- Rojo (Más crítico)
    ELSEIF NEW.porcentaje_avance_obra >= 11 THEN
        SET NEW.semaforo_id_semaforo = 2; -- Amarillo
    ELSE
        SET NEW.semaforo_id_semaforo = 1; -- Verde
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

--
-- Volcado de datos para la tabla `particular`
--

INSERT INTO `particular` (`id_particular`, `nombre`, `apellido`, `persona_id_persona`, `estado`) VALUES
(1, 'Gabriel', 'Mujica', 1, 1),
(2, 'Mariangel', 'Bokor', 11, 1),
(3, 'Guillermo', 'Torres', 18, 1);

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
  `correo` varchar(45) NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
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
(11, 30587785, 'Carrera 4 con Calle 5', 'Cabudare', 'Palavecino', '04245319088', 'bokorMBmariposa@gmail.com', 1),
(12, 8977634, 'Av. Los Horcones con Av. La Salle.', 'Catedral', 'Iribarren', '04125677474', 'MejiAlejandro443@gmail.com', 1),
(13, 28542148, 'Calle 9 entre Cra. 20 y 21, Casa N° 20-15', 'Concepción', 'Iribarren', '04163347465', 'Elenaita22Ri@gmail.com', 1),
(14, 29723582, 'Urb. La Rosaleda, Calle 5, Casa 12', 'Cabudare', 'Palavecino', '04125543568', 'ElJavivi@gmail.com', 1),
(15, 29545867, 'Av. Los Abogados, Res. El Parque, Torre A', 'Santa Rosa', 'Iribarren', '04146564722', 'LaSofi23@gmail.com', 1),
(16, 12345678, 'Av. Principal, Sector Centro', 'Catedral', 'Iribarren', '0251-2319786', 'contacto@l-alvarado.edu.ve', 1),
(17, 25289197, 'Calle Carabobo, Casa N° 34', 'Anzoátegui', 'Morán', '04120896778', 'FranVier@gmail.com', 1),
(18, 28342778, 'Calle 5 con Carrera 6', 'Freitez', 'Crespo', '04127766654', 'Guille@gmail.com', 1);

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

--
-- Volcado de datos para la tabla `prioridad`
--

INSERT INTO `prioridad` (`id_gestion_prioridad`, `rango_prioridad`, `fecha_asignacion`, `responsable_ajuste`, `justificacion_cambio`, `estado`) VALUES
(1, 0.5, '2026-06-15 16:38:02', 'Test', 'Clasificación por heurística (IA no disponible): Ollama no está disponible en http://localhost:11434', 1);

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
  `estado` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de gestion de proyectos';

--
-- Volcado de datos para la tabla `proyecto`
--

INSERT INTO `proyecto` (`codigo_proyecto`, `fecha_planificacion`, `descripcion_tecnica`, `computos_metricos`, `estimacion_costo`, `estado`) VALUES
('FRE-001', '2026-06-24 00:00:00', 'Restauración Vial', '230 m2', '200000 dolares', 0),
('WEY-001', '2026-07-01 00:00:00', 'Servicio Basico ', '11513424m2', '237523', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proyecto_has_maquinaria`
--

CREATE TABLE `proyecto_has_maquinaria` (
  `proyecto_codigo_proyecto` varchar(15) NOT NULL,
  `maquinaria_id_maquinaria` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `proyecto_has_maquinaria`
--

INSERT INTO `proyecto_has_maquinaria` (`proyecto_codigo_proyecto`, `maquinaria_id_maquinaria`, `estado`) VALUES
('FRE-001', 7, 1),
('WEY-001', 16, 1);

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

--
-- Volcado de datos para la tabla `proyecto_has_solicitudes`
--

INSERT INTO `proyecto_has_solicitudes` (`proyecto_codigo_proyecto`, `solicitudes_id_solicitudes`, `solicitudes_persona_id_persona`, `solicitudes_prioridad_id_gestion_prioridad`, `estado`) VALUES
('FRE-001', 7, 6, 1, 1),
('WEY-001', 8, 11, 1, 1);

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

--
-- Volcado de datos para la tabla `publicacion`
--

INSERT INTO `publicacion` (`id_publicacion`, `titulo_publicacion`, `nombre_responsable`, `tipo_publicacion`, `fecha_publicacion`, `informe_avance_obra_id_informe`, `cuerpo_publicacion`, `estado`) VALUES
(1, 'Cabudares esta en escaces de agua por varias semanas', 'Administrador', 'General', '2026-07-07 00:55:59', 2, 'Gracias a las orientaciones del gobernador Cmdte. Luis Reyes Reyes, seguimos activos y avanzando con el despliegue estrategico para la reconstrucción y sustitución de las estructuras de alcantarillas en diferentes sectores de la parroquia Cabudare del municipio Palavecino, Estado Lara.', 1);

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
-- Estructura de tabla para la tabla `respaldo_bd`
--

CREATE TABLE `respaldo_bd` (
  `id_respaldo` int NOT NULL,
  `nombre_archivo` varchar(255) NOT NULL,
  `tamano` bigint NOT NULL DEFAULT '0',
  `descripcion` varchar(255) DEFAULT '',
  `fecha_respaldo` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `estado` tinyint NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `respaldo_bd`
--

INSERT INTO `respaldo_bd` (`id_respaldo`, `nombre_archivo`, `tamano`, `descripcion`, `fecha_respaldo`, `estado`) VALUES
(2, 'respaldo_20260708_225811.sql', 62834, 'respaldo general', '2026-07-09 02:58:12', 1);

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
(1, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(2, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(3, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(4, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(5, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(6, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(7, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(8, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(9, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(10, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(11, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(12, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(13, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(14, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(15, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(16, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(17, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(18, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(19, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(20, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(21, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(22, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(23, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0),
(24, 'Activo', 'VERDE', 'Semáforo generado automáticamente', 0);

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

--
-- Volcado de datos para la tabla `solicitudes`
--

INSERT INTO `solicitudes` (`id_solicitudes`, `fecha`, `tipo_solicitud`, `estatus_solicitud`, `problematica`, `persona_id_persona`, `prioridad_id_gestion_prioridad`, `estado`) VALUES
(1, '2026-06-15 16:38:02', 'Particular', 'Pendiente', '[Servicios Básicos (Agua, Luz, Gas)] no hay gaz de prueba mortadela', 1, 1, 1),
(2, '2026-06-15 16:40:32', 'Comunidad', 'Completada', '[Salud y Asistencia Médica] En la comunidad necesitamos una jornada de vacunación', 2, 1, 1),
(3, '2026-06-15 16:46:00', 'Comunidad', 'Pendiente', '[Servicios Básicos (Agua, Luz, Gas)] hueco en la avenida donde salen aguas negras', 4, 1, 1),
(7, '2026-06-16 17:58:23', 'Comunidad', 'En Proceso', '[Infraestructura y Vialidad] Acondicionamiento vial', 6, 1, 1),
(8, '2026-06-24 16:04:42', 'Particular', 'En Proceso', '[Servicios Básicos (Agua, Luz, Gas)] No hay agua y todos nos estamos derritiendo, porfis traigan aguita aaaaaaaaa', 11, 1, 1),
(9, '2026-07-05 22:32:39', 'Institucion', 'En Proceso', '[Infraestructura y Vialidad] Reparación de bacheo profundo en el acceso principal de la institución por filtraciones.', 16, 1, 1),
(10, '2026-07-07 19:59:35', 'Particular', 'En Proceso', '[Salud y Asistencia Médica] Se necesita una jornada de vacunacion', 18, 1, 1);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_evidencia_informe`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `vista_evidencia_informe` (
`estado` tinyint
,`estado_informe` varchar(25)
,`etapa` enum('antes','durante','despues')
,`fecha_informe` datetime
,`fecha_registro` datetime
,`fotos` varchar(255)
,`id_evidencia` int
,`id_informe` int
,`tipo_informe` varchar(30)
,`url_archivos` varchar(255)
);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `administracion_respaldos`
--
ALTER TABLE `administracion_respaldos`
  ADD PRIMARY KEY (`id_respaldo`);

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
  ADD KEY `fk_informe_avance_obra_avance1_idx` (`avance_id_avance`),
  ADD KEY `idx_informe_estado_registro` (`estado_registro`);

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
-- AUTO_INCREMENT de la tabla `administracion_respaldos`
--
ALTER TABLE `administracion_respaldos`
  MODIFY `id_respaldo` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `catalogo_cargos`
--
ALTER TABLE `catalogo_cargos`
  MODIFY `id_cargo` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `comunidad`
--
ALTER TABLE `comunidad`
  MODIFY `id_comunidad` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `contratacion`
--
ALTER TABLE `contratacion`
  MODIFY `id_contratacion` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `empleados`
--
ALTER TABLE `empleados`
  MODIFY `id_empleados` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT de la tabla `evidencia`
--
ALTER TABLE `evidencia`
  MODIFY `id_evidencia` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT de la tabla `gravedad_obra`
--
ALTER TABLE `gravedad_obra`
  MODIFY `id_gravedad` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `informe_avance_obra`
--
ALTER TABLE `informe_avance_obra`
  MODIFY `id_informe` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

--
-- AUTO_INCREMENT de la tabla `inspeccion`
--
ALTER TABLE `inspeccion`
  MODIFY `id_inspeccion` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `institucion`
--
ALTER TABLE `institucion`
  MODIFY `id_institucion` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `maquinaria`
--
ALTER TABLE `maquinaria`
  MODIFY `id_maquinaria` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT de la tabla `obra`
--
ALTER TABLE `obra`
  MODIFY `id_obra` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT de la tabla `particular`
--
ALTER TABLE `particular`
  MODIFY `id_particular` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `persona`
--
ALTER TABLE `persona`
  MODIFY `id_persona` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT de la tabla `prioridad`
--
ALTER TABLE `prioridad`
  MODIFY `id_gestion_prioridad` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `publicacion`
--
ALTER TABLE `publicacion`
  MODIFY `id_publicacion` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `reporte`
--
ALTER TABLE `reporte`
  MODIFY `id_reporte` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `respaldo_bd`
--
ALTER TABLE `respaldo_bd`
  MODIFY `id_respaldo` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `semaforo`
--
ALTER TABLE `semaforo`
  MODIFY `id_semaforo` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT de la tabla `solicitudes`
--
ALTER TABLE `solicitudes`
  MODIFY `id_solicitudes` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

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
