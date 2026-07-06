-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 06-07-2026 a las 02:10:34
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
-- Base de datos: `invilara_seguridad`
--
CREATE DATABASE IF NOT EXISTS `invilara_seguridad` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `invilara_seguridad`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `administracion_respaldos`
--

CREATE TABLE `administracion_respaldos` (
  `id_respaldo` int NOT NULL,
  `fecha_respaldo` datetime NOT NULL,
  `tamaño_respaldo` decimal(4,2) NOT NULL,
  `usuarios_id_usuarios` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Tabla de administracion de respaldos.';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bitacora`
--

CREATE TABLE `bitacora` (
  `id_bitacora` int NOT NULL,
  `usuario` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `id_modulo` int NOT NULL,
  `modulo` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `accion` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `fecha` datetime NOT NULL,
  `hora_inicio_sesion` datetime NOT NULL,
  `hora_cierre_sesion` datetime NOT NULL,
  `usuarios_id_usuarios` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Tabla de la bitacora del sistema.';

--
-- Volcado de datos para la tabla `bitacora`
--

INSERT INTO `bitacora` (`id_bitacora`, `usuario`, `id_modulo`, `modulo`, `accion`, `fecha`, `hora_inicio_sesion`, `hora_cierre_sesion`, `usuarios_id_usuarios`) VALUES
(1, 'Sistema', 0, 'Solicitudes', 'CREAR', '2026-06-19 08:46:43', '2026-06-19 08:46:43', '2026-06-19 08:46:43', 1),
(2, 'Sistema', 0, 'Solicitudes', 'CREAR', '2026-06-19 09:32:39', '2026-06-19 09:32:39', '2026-06-19 09:32:39', 1),
(3, 'Sistema', 0, 'Solicitudes', 'CREAR', '2026-06-19 09:34:13', '2026-06-19 09:34:13', '2026-06-19 09:34:13', 1),
(4, 'Sistema', 0, 'Solicitudes', 'CREAR', '2026-06-19 09:35:15', '2026-06-19 09:35:15', '2026-06-19 09:35:15', 1),
(5, 'Sistema', 0, 'Solicitudes', 'CREAR', '2026-06-19 09:36:51', '2026-06-19 09:36:51', '2026-06-19 09:36:51', 1),
(6, 'Sistema', 0, 'Solicitudes', 'VER', '2026-06-19 09:39:03', '2026-06-19 09:39:03', '2026-06-19 09:39:03', 1),
(7, 'Sistema', 0, 'Solicitudes', 'VER', '2026-06-19 09:39:14', '2026-06-19 09:39:14', '2026-06-19 09:39:14', 1),
(8, 'Sistema', 0, 'Solicitudes', 'EDITAR', '2026-06-19 09:39:19', '2026-06-19 09:39:19', '2026-06-19 09:39:19', 1),
(9, 'Sistema', 0, 'Solicitudes', 'VER', '2026-06-19 09:39:27', '2026-06-19 09:39:27', '2026-06-19 09:39:27', 1),
(10, 'Sistema', 0, 'Solicitudes', 'EDITAR', '2026-06-19 09:39:32', '2026-06-19 09:39:32', '2026-06-19 09:39:32', 1),
(11, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-22 19:27:32', '2026-06-22 19:27:32', '2026-06-22 19:27:32', 1),
(12, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-22 19:28:32', '2026-06-22 19:28:32', '2026-06-22 19:28:32', 1),
(13, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-22 21:28:16', '2026-06-22 21:28:16', '2026-06-22 21:28:16', 1),
(14, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-22 21:32:28', '2026-06-22 21:32:28', '2026-06-22 21:32:28', 1),
(15, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-23 23:47:47', '2026-06-23 23:47:47', '2026-06-23 23:47:47', 1),
(16, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 00:17:16', '2026-06-24 00:17:16', '2026-06-24 00:17:16', 1),
(17, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 00:51:38', '2026-06-24 00:51:38', '2026-06-24 00:51:38', 1),
(18, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 00:53:23', '2026-06-24 00:53:23', '2026-06-24 00:53:23', 1),
(19, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 00:54:41', '2026-06-24 00:54:41', '2026-06-24 00:54:41', 1),
(20, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 00:59:43', '2026-06-24 00:59:43', '2026-06-24 00:59:43', 1),
(21, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 01:01:54', '2026-06-24 01:01:54', '2026-06-24 01:01:54', 1),
(22, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 01:07:59', '2026-06-24 01:07:59', '2026-06-24 01:07:59', 1),
(23, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 01:10:09', '2026-06-24 01:10:09', '2026-06-24 01:10:09', 1),
(24, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 01:35:59', '2026-06-24 01:35:59', '2026-06-24 01:35:59', 1),
(25, 'Sistema', 0, 'Solicitudes', 'CREAR', '2026-06-24 16:04:43', '2026-06-24 16:04:43', '2026-06-24 16:04:43', 1),
(26, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 18:35:11', '2026-06-24 18:35:11', '2026-06-24 18:35:11', 1),
(27, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 18:39:48', '2026-06-24 18:39:48', '2026-06-24 18:39:48', 1),
(28, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 21:23:36', '2026-06-24 21:23:36', '2026-06-24 21:23:36', 1),
(29, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 21:23:38', '2026-06-24 21:23:38', '2026-06-24 21:23:38', 1),
(30, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 22:00:34', '2026-06-24 22:00:34', '2026-06-24 22:00:34', 1),
(31, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 22:45:48', '2026-06-24 22:45:48', '2026-06-24 22:45:48', 1),
(32, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 22:45:50', '2026-06-24 22:45:50', '2026-06-24 22:45:50', 1),
(33, 'Sistema', 0, 'Informes de Avance', 'VER', '2026-06-24 22:46:26', '2026-06-24 22:46:26', '2026-06-24 22:46:26', 1),
(34, 'admin', 0, 'Proyectos', 'VER', '2026-06-26 06:17:59', '2026-06-26 06:17:59', '2026-06-26 06:17:59', 1),
(35, 'admin', 0, 'Login', 'LOGIN', '2026-06-26 15:45:22', '2026-06-26 15:45:22', '2026-06-26 15:45:22', 1),
(36, 'admin', 0, 'Proyectos', 'VER', '2026-06-27 05:16:22', '2026-06-27 05:16:22', '2026-06-27 05:16:22', 1),
(37, 'admin', 0, 'Login', 'LOGIN', '2026-06-28 01:41:39', '2026-06-28 01:41:39', '2026-06-28 01:41:39', 1),
(38, 'admin', 0, 'Login', 'LOGIN', '2026-06-28 02:38:12', '2026-06-28 02:38:12', '2026-06-28 02:38:12', 1),
(39, 'admin', 0, 'Login', 'LOGIN', '2026-06-28 13:36:50', '2026-06-28 13:36:50', '2026-06-28 13:36:50', 1),
(40, 'admin', 0, 'Informes de Avance', 'VER', '2026-06-28 15:30:08', '2026-06-28 15:30:08', '2026-06-28 15:30:08', 1),
(41, 'admin', 0, 'Login', 'LOGIN', '2026-06-30 18:14:01', '2026-06-30 18:14:01', '2026-06-30 18:14:01', 1),
(42, 'admin', 0, 'Informes de Avance', 'VER', '2026-06-30 18:20:09', '2026-06-30 18:20:09', '2026-06-30 18:20:09', 1),
(43, 'admin', 0, 'Informes de Avance', 'VER', '2026-06-30 19:26:59', '2026-06-30 19:26:59', '2026-06-30 19:26:59', 1),
(44, 'admin', 0, 'Informes de Avance', 'VER', '2026-06-30 19:35:12', '2026-06-30 19:35:12', '2026-06-30 19:35:12', 1),
(45, 'admin', 0, 'Informes de Avance', 'VER', '2026-06-30 19:51:59', '2026-06-30 19:51:59', '2026-06-30 19:51:59', 1),
(46, 'admin', 0, 'Informes de Avance', 'VER', '2026-06-30 19:52:02', '2026-06-30 19:52:02', '2026-06-30 19:52:02', 1),
(47, 'admin', 0, 'Informes de Avance', 'VER', '2026-06-30 20:06:31', '2026-06-30 20:06:31', '2026-06-30 20:06:31', 1),
(48, 'admin', 0, 'Informes de Avance', 'VER', '2026-06-30 21:12:35', '2026-06-30 21:12:35', '2026-06-30 21:12:35', 1),
(49, 'admin', 0, 'Informes de Avance', 'CREAR', '2026-06-30 21:13:31', '2026-06-30 21:13:31', '2026-06-30 21:13:31', 1),
(50, 'admin', 0, 'Informes de Avance', 'VER', '2026-06-30 21:13:48', '2026-06-30 21:13:48', '2026-06-30 21:13:48', 1),
(51, 'admin', 0, 'Informes de Avance', 'VER', '2026-06-30 21:13:49', '2026-06-30 21:13:49', '2026-06-30 21:13:49', 1),
(52, 'admin', 0, 'Informes de Avance', 'VER', '2026-06-30 21:13:57', '2026-06-30 21:13:57', '2026-06-30 21:13:57', 1),
(53, 'admin', 0, 'Informes de Avance', 'VER', '2026-06-30 21:13:58', '2026-06-30 21:13:58', '2026-06-30 21:13:58', 1),
(54, 'admin', 0, 'Informes de Avance', 'CREAR', '2026-06-30 22:12:16', '2026-06-30 22:12:16', '2026-06-30 22:12:16', 1),
(55, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 02:59:01', '2026-07-01 02:59:01', '2026-07-01 02:59:01', 1),
(56, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 02:59:21', '2026-07-01 02:59:21', '2026-07-01 02:59:21', 1),
(57, 'admin', 0, 'Login', 'LOGIN', '2026-07-01 16:11:02', '2026-07-01 16:11:02', '2026-07-01 16:11:02', 1),
(58, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 16:11:09', '2026-07-01 16:11:09', '2026-07-01 16:11:09', 1),
(59, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 20:09:50', '2026-07-01 20:09:50', '2026-07-01 20:09:50', 1),
(60, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 20:25:58', '2026-07-01 20:25:58', '2026-07-01 20:25:58', 1),
(61, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 22:58:26', '2026-07-01 22:58:26', '2026-07-01 22:58:26', 1),
(62, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:01:01', '2026-07-01 23:01:01', '2026-07-01 23:01:01', 1),
(63, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-01 23:01:26', '2026-07-01 23:01:26', '2026-07-01 23:01:26', 1),
(64, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:06:22', '2026-07-01 23:06:22', '2026-07-01 23:06:22', 1),
(65, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-01 23:06:30', '2026-07-01 23:06:30', '2026-07-01 23:06:30', 1),
(66, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-01 23:06:51', '2026-07-01 23:06:51', '2026-07-01 23:06:51', 1),
(67, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:06:52', '2026-07-01 23:06:52', '2026-07-01 23:06:52', 1),
(68, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:08:01', '2026-07-01 23:08:01', '2026-07-01 23:08:01', 1),
(69, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:34:56', '2026-07-01 23:34:56', '2026-07-01 23:34:56', 1),
(70, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-01 23:35:17', '2026-07-01 23:35:17', '2026-07-01 23:35:17', 1),
(71, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:35:18', '2026-07-01 23:35:18', '2026-07-01 23:35:18', 1),
(72, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-01 23:35:30', '2026-07-01 23:35:30', '2026-07-01 23:35:30', 1),
(73, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:35:30', '2026-07-01 23:35:30', '2026-07-01 23:35:30', 1),
(74, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:36:22', '2026-07-01 23:36:22', '2026-07-01 23:36:22', 1),
(75, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:49:34', '2026-07-01 23:49:34', '2026-07-01 23:49:34', 1),
(76, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-01 23:49:45', '2026-07-01 23:49:45', '2026-07-01 23:49:45', 1),
(77, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:49:46', '2026-07-01 23:49:46', '2026-07-01 23:49:46', 1),
(78, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:49:47', '2026-07-01 23:49:47', '2026-07-01 23:49:47', 1),
(79, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:49:53', '2026-07-01 23:49:53', '2026-07-01 23:49:53', 1),
(80, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-01 23:50:03', '2026-07-01 23:50:03', '2026-07-01 23:50:03', 1),
(81, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:50:03', '2026-07-01 23:50:03', '2026-07-01 23:50:03', 1),
(82, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-01 23:50:23', '2026-07-01 23:50:23', '2026-07-01 23:50:23', 1),
(83, 'admin', 0, 'Login', 'LOGIN', '2026-07-02 11:49:53', '2026-07-02 11:49:53', '2026-07-02 11:49:53', 1),
(84, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 11:50:01', '2026-07-02 11:50:01', '2026-07-02 11:50:01', 1),
(85, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 12:42:12', '2026-07-02 12:42:12', '2026-07-02 12:42:12', 1),
(86, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 19:20:51', '2026-07-02 19:20:51', '2026-07-02 19:20:51', 1),
(87, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 19:37:16', '2026-07-02 19:37:16', '2026-07-02 19:37:16', 1),
(88, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 20:14:25', '2026-07-02 20:14:25', '2026-07-02 20:14:25', 1),
(89, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 20:22:14', '2026-07-02 20:22:14', '2026-07-02 20:22:14', 1),
(90, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 20:27:23', '2026-07-02 20:27:23', '2026-07-02 20:27:23', 1),
(91, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 22:59:15', '2026-07-02 22:59:15', '2026-07-02 22:59:15', 1),
(92, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-02 22:59:40', '2026-07-02 22:59:40', '2026-07-02 22:59:40', 1),
(93, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 22:59:41', '2026-07-02 22:59:41', '2026-07-02 22:59:41', 1),
(94, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 23:00:33', '2026-07-02 23:00:33', '2026-07-02 23:00:33', 1),
(95, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 23:00:34', '2026-07-02 23:00:34', '2026-07-02 23:00:34', 1),
(96, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 23:00:40', '2026-07-02 23:00:40', '2026-07-02 23:00:40', 1),
(97, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 23:00:40', '2026-07-02 23:00:40', '2026-07-02 23:00:40', 1),
(98, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 23:00:45', '2026-07-02 23:00:45', '2026-07-02 23:00:45', 1),
(99, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 23:00:45', '2026-07-02 23:00:45', '2026-07-02 23:00:45', 1),
(100, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 23:04:17', '2026-07-02 23:04:17', '2026-07-02 23:04:17', 1),
(101, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-02 23:34:56', '2026-07-02 23:34:56', '2026-07-02 23:34:56', 1),
(102, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:07:59', '2026-07-03 00:07:59', '2026-07-03 00:07:59', 1),
(103, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:08:42', '2026-07-03 00:08:42', '2026-07-03 00:08:42', 1),
(104, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:08:43', '2026-07-03 00:08:43', '2026-07-03 00:08:43', 1),
(105, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:08:57', '2026-07-03 00:08:57', '2026-07-03 00:08:57', 1),
(106, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:08:57', '2026-07-03 00:08:57', '2026-07-03 00:08:57', 1),
(107, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:09:01', '2026-07-03 00:09:01', '2026-07-03 00:09:01', 1),
(108, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:09:01', '2026-07-03 00:09:01', '2026-07-03 00:09:01', 1),
(109, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:20:13', '2026-07-03 00:20:13', '2026-07-03 00:20:13', 1),
(110, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-03 00:20:28', '2026-07-03 00:20:28', '2026-07-03 00:20:28', 1),
(111, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:20:28', '2026-07-03 00:20:28', '2026-07-03 00:20:28', 1),
(112, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-03 00:20:36', '2026-07-03 00:20:36', '2026-07-03 00:20:36', 1),
(113, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:20:37', '2026-07-03 00:20:37', '2026-07-03 00:20:37', 1),
(114, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-03 00:20:53', '2026-07-03 00:20:53', '2026-07-03 00:20:53', 1),
(115, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:20:54', '2026-07-03 00:20:54', '2026-07-03 00:20:54', 1),
(116, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:21:03', '2026-07-03 00:21:03', '2026-07-03 00:21:03', 1),
(117, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:21:03', '2026-07-03 00:21:03', '2026-07-03 00:21:03', 1),
(118, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:22:06', '2026-07-03 00:22:06', '2026-07-03 00:22:06', 1),
(119, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:22:06', '2026-07-03 00:22:06', '2026-07-03 00:22:06', 1),
(120, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:23:20', '2026-07-03 00:23:20', '2026-07-03 00:23:20', 1),
(121, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:23:20', '2026-07-03 00:23:20', '2026-07-03 00:23:20', 1),
(122, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:23:35', '2026-07-03 00:23:35', '2026-07-03 00:23:35', 1),
(123, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:23:36', '2026-07-03 00:23:36', '2026-07-03 00:23:36', 1),
(124, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:23:50', '2026-07-03 00:23:50', '2026-07-03 00:23:50', 1),
(125, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 00:23:50', '2026-07-03 00:23:50', '2026-07-03 00:23:50', 1),
(126, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 02:15:31', '2026-07-03 02:15:31', '2026-07-03 02:15:31', 1),
(127, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 02:15:32', '2026-07-03 02:15:32', '2026-07-03 02:15:32', 1),
(128, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 03:19:01', '2026-07-03 03:19:01', '2026-07-03 03:19:01', 1),
(129, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 03:19:33', '2026-07-03 03:19:33', '2026-07-03 03:19:33', 1),
(130, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 03:19:57', '2026-07-03 03:19:57', '2026-07-03 03:19:57', 1),
(131, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-03 03:20:11', '2026-07-03 03:20:11', '2026-07-03 03:20:11', 1),
(132, 'admin', 0, 'Login', 'LOGIN', '2026-07-04 02:20:51', '2026-07-04 02:20:51', '2026-07-04 02:20:51', 1),
(133, 'admin', 0, 'Proyectos', 'VER', '2026-07-04 03:25:01', '2026-07-04 03:25:01', '2026-07-04 03:25:01', 1),
(134, 'Frangher Pereir', 0, 'Login', 'LOGIN', '2026-07-04 17:28:14', '2026-07-04 17:28:14', '2026-07-04 17:28:14', 5),
(135, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 17:32:21', '2026-07-04 17:32:21', '2026-07-04 17:32:21', 5),
(136, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 18:00:15', '2026-07-04 18:00:15', '2026-07-04 18:00:15', 5),
(137, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 18:01:51', '2026-07-04 18:01:51', '2026-07-04 18:01:51', 5),
(138, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 18:47:56', '2026-07-04 18:47:56', '2026-07-04 18:47:56', 5),
(139, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 18:49:06', '2026-07-04 18:49:06', '2026-07-04 18:49:06', 5),
(140, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 18:52:21', '2026-07-04 18:52:21', '2026-07-04 18:52:21', 5),
(141, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 19:01:32', '2026-07-04 19:01:32', '2026-07-04 19:01:32', 5),
(142, 'Frangher Pereir', 0, 'Informes de Avance', 'EDITAR', '2026-07-04 19:02:15', '2026-07-04 19:02:15', '2026-07-04 19:02:15', 5),
(143, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 19:04:20', '2026-07-04 19:04:20', '2026-07-04 19:04:20', 5),
(144, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 20:02:20', '2026-07-04 20:02:20', '2026-07-04 20:02:20', 5),
(145, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 20:12:07', '2026-07-04 20:12:07', '2026-07-04 20:12:07', 5),
(146, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 20:48:08', '2026-07-04 20:48:08', '2026-07-04 20:48:08', 5),
(147, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 20:57:11', '2026-07-04 20:57:11', '2026-07-04 20:57:11', 5),
(148, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:02:10', '2026-07-04 21:02:10', '2026-07-04 21:02:10', 5),
(149, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:11:11', '2026-07-04 21:11:11', '2026-07-04 21:11:11', 5),
(150, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:11:11', '2026-07-04 21:11:11', '2026-07-04 21:11:11', 5),
(151, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:11:12', '2026-07-04 21:11:12', '2026-07-04 21:11:12', 5),
(152, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:11:13', '2026-07-04 21:11:13', '2026-07-04 21:11:13', 5),
(153, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:15:06', '2026-07-04 21:15:06', '2026-07-04 21:15:06', 5),
(154, 'Frangher Pereir', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-04 21:15:13', '2026-07-04 21:15:13', '2026-07-04 21:15:13', 5),
(155, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:15:14', '2026-07-04 21:15:14', '2026-07-04 21:15:14', 5),
(156, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:15:20', '2026-07-04 21:15:20', '2026-07-04 21:15:20', 5),
(157, 'Frangher Pereir', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-04 21:15:39', '2026-07-04 21:15:39', '2026-07-04 21:15:39', 5),
(158, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:15:40', '2026-07-04 21:15:40', '2026-07-04 21:15:40', 5),
(159, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:49:51', '2026-07-04 21:49:51', '2026-07-04 21:49:51', 5),
(160, 'Frangher Pereir', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-04 21:49:59', '2026-07-04 21:49:59', '2026-07-04 21:49:59', 5),
(161, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:49:59', '2026-07-04 21:49:59', '2026-07-04 21:49:59', 5),
(162, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:51:26', '2026-07-04 21:51:26', '2026-07-04 21:51:26', 5),
(163, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:51:42', '2026-07-04 21:51:42', '2026-07-04 21:51:42', 5),
(164, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 21:54:04', '2026-07-04 21:54:04', '2026-07-04 21:54:04', 5),
(165, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 22:31:12', '2026-07-04 22:31:12', '2026-07-04 22:31:12', 5),
(166, 'Frangher Pereir', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-04 22:31:47', '2026-07-04 22:31:47', '2026-07-04 22:31:47', 5),
(167, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 22:31:48', '2026-07-04 22:31:48', '2026-07-04 22:31:48', 5),
(168, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 22:32:20', '2026-07-04 22:32:20', '2026-07-04 22:32:20', 5),
(169, 'Frangher Pereir', 0, 'Proyectos', 'VER', '2026-07-04 22:37:36', '2026-07-04 22:37:36', '2026-07-04 22:37:36', 5),
(170, 'Frangher Pereir', 0, 'Proyectos', 'VER', '2026-07-04 22:39:20', '2026-07-04 22:39:20', '2026-07-04 22:39:20', 5),
(171, 'Frangher Pereir', 0, 'Empresas', 'CREAR', '2026-07-04 22:44:41', '2026-07-04 22:44:41', '2026-07-04 22:44:41', 5),
(172, 'Frangher Pereir', 0, 'Proyectos', 'VER', '2026-07-04 22:45:35', '2026-07-04 22:45:35', '2026-07-04 22:45:35', 5),
(173, 'Frangher Pereir', 0, 'Proyectos', 'VER', '2026-07-04 22:47:06', '2026-07-04 22:47:06', '2026-07-04 22:47:06', 5),
(174, 'Frangher Pereir', 0, 'Proyectos', 'VER', '2026-07-04 22:48:08', '2026-07-04 22:48:08', '2026-07-04 22:48:08', 5),
(175, 'Frangher Pereir', 0, 'Proyectos', 'CREAR', '2026-07-04 22:50:47', '2026-07-04 22:50:47', '2026-07-04 22:50:47', 5),
(176, 'Frangher Pereir', 0, 'Proyectos', 'VER', '2026-07-04 22:50:48', '2026-07-04 22:50:48', '2026-07-04 22:50:48', 5),
(177, 'Frangher Pereir', 0, 'Proyectos', 'EDITAR', '2026-07-04 22:52:21', '2026-07-04 22:52:21', '2026-07-04 22:52:21', 5),
(178, 'Frangher Pereir', 0, 'Proyectos', 'VER', '2026-07-04 22:52:22', '2026-07-04 22:52:22', '2026-07-04 22:52:22', 5),
(179, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 23:00:10', '2026-07-04 23:00:10', '2026-07-04 23:00:10', 5),
(180, 'Frangher Pereir', 0, 'Proyectos', 'VER', '2026-07-04 23:09:57', '2026-07-04 23:09:57', '2026-07-04 23:09:57', 5),
(181, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 23:10:45', '2026-07-04 23:10:45', '2026-07-04 23:10:45', 5),
(182, 'Frangher Pereir', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-04 23:11:09', '2026-07-04 23:11:09', '2026-07-04 23:11:09', 5),
(183, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 23:11:10', '2026-07-04 23:11:10', '2026-07-04 23:11:10', 5),
(184, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 23:11:46', '2026-07-04 23:11:46', '2026-07-04 23:11:46', 5),
(185, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 23:12:04', '2026-07-04 23:12:04', '2026-07-04 23:12:04', 5),
(186, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-04 23:34:31', '2026-07-04 23:34:31', '2026-07-04 23:34:31', 5),
(187, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 00:27:04', '2026-07-05 00:27:04', '2026-07-05 00:27:04', 5),
(188, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 00:30:03', '2026-07-05 00:30:03', '2026-07-05 00:30:03', 5),
(189, 'Frangher Pereir', 0, 'Informes de Avance', 'EDITAR', '2026-07-05 00:30:24', '2026-07-05 00:30:24', '2026-07-05 00:30:24', 5),
(190, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 00:30:25', '2026-07-05 00:30:25', '2026-07-05 00:30:25', 5),
(191, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 00:30:47', '2026-07-05 00:30:47', '2026-07-05 00:30:47', 5),
(192, 'Frangher Pereir', 0, 'Informes de Avance', 'EDITAR', '2026-07-05 00:31:25', '2026-07-05 00:31:25', '2026-07-05 00:31:25', 5),
(193, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 00:31:27', '2026-07-05 00:31:27', '2026-07-05 00:31:27', 5),
(194, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 00:31:46', '2026-07-05 00:31:46', '2026-07-05 00:31:46', 5),
(195, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 00:39:42', '2026-07-05 00:39:42', '2026-07-05 00:39:42', 5),
(196, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 00:57:56', '2026-07-05 00:57:56', '2026-07-05 00:57:56', 5),
(197, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 01:05:32', '2026-07-05 01:05:32', '2026-07-05 01:05:32', 5),
(198, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 01:05:33', '2026-07-05 01:05:33', '2026-07-05 01:05:33', 5),
(199, 'Frangher Pereir', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-05 01:05:42', '2026-07-05 01:05:42', '2026-07-05 01:05:42', 5),
(200, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 01:05:42', '2026-07-05 01:05:42', '2026-07-05 01:05:42', 5),
(201, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-05 01:08:55', '2026-07-05 01:08:55', '2026-07-05 01:08:55', 1),
(202, 'admin', 0, 'Informes de Avance', 'CREAR', '2026-07-05 01:12:07', '2026-07-05 01:12:07', '2026-07-05 01:12:07', 1),
(203, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-05 01:17:26', '2026-07-05 01:17:26', '2026-07-05 01:17:26', 1),
(204, 'admin', 0, 'Informes de Avance', 'CREAR', '2026-07-05 01:17:48', '2026-07-05 01:17:48', '2026-07-05 01:17:48', 1),
(205, 'admin', 0, 'Informes de Avance', 'EDITAR', '2026-07-05 01:21:03', '2026-07-05 01:21:03', '2026-07-05 01:21:03', 1),
(206, 'admin', 0, 'Informes de Avance', 'VER', '2026-07-05 01:22:24', '2026-07-05 01:22:24', '2026-07-05 01:22:24', 1),
(207, 'admin', 0, 'Informes de Avance', 'CREAR', '2026-07-05 01:27:27', '2026-07-05 01:27:27', '2026-07-05 01:27:27', 1),
(208, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-05 01:27:28', '2026-07-05 01:27:28', '2026-07-05 01:27:28', 1),
(209, 'admin', 0, 'Informes de Avance', 'CREAR', '2026-07-05 01:28:27', '2026-07-05 01:28:27', '2026-07-05 01:28:27', 1),
(210, 'admin', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-05 01:28:27', '2026-07-05 01:28:27', '2026-07-05 01:28:27', 1),
(211, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 01:29:30', '2026-07-05 01:29:30', '2026-07-05 01:29:30', 5),
(212, 'Frangher Pereir', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-05 01:29:44', '2026-07-05 01:29:44', '2026-07-05 01:29:44', 5),
(213, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 01:38:44', '2026-07-05 01:38:44', '2026-07-05 01:38:44', 5),
(214, 'Frangher Pereir', 0, 'Informes de Avance', 'ELIMINAR', '2026-07-05 01:39:02', '2026-07-05 01:39:02', '2026-07-05 01:39:02', 5),
(215, 'Frangher Pereir', 0, 'Informes de Avance', 'VER', '2026-07-05 01:39:41', '2026-07-05 01:39:41', '2026-07-05 01:39:41', 5),
(216, 'Sistema', 0, 'Login', 'LOGOUT', '2026-07-05 01:47:06', '2026-07-05 01:47:06', '2026-07-05 01:47:06', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuarios` int NOT NULL,
  `nombre` varchar(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `cedula_usuario` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `contrasena` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `correo` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `rol` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Tabla de los usuarios.',
  `otp_code` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Código OTP de 4 dígitos',
  `otp_expiry` datetime DEFAULT NULL COMMENT 'Fecha de expiración del OTP',
  `otp_attempts` int DEFAULT '0' COMMENT 'Intentos fallidos de OTP',
  `estado` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1 para activo, 0 para inactivo',
  `avatar` varchar(255) COLLATE utf8mb4_general_ci DEFAULT 'assets/img/avatars/1.png' COMMENT 'Foto de perfil del usuario'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Tabla de usuarios';

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuarios`, `nombre`, `cedula_usuario`, `contrasena`, `correo`, `rol`, `otp_code`, `otp_expiry`, `otp_attempts`, `estado`, `avatar`) VALUES
(1, 'admin', '12345678', 'pbkdf2:sha256:600000$55dFI8r0mPOkdiR2$a437b96290e42be3cc8c847fb37c088aafc6894dddc904465813a5e849da2e6d', 'admin@gmail.com', 'Super Usuario', NULL, NULL, 0, 1, 'assets/img/avatars/1.png'),
(2, 'David Peña', '30304373', 'pbkdf2:sha256:600000$hNB86qI4PJLFj5zI$a8db74876d9381392452fc144ee2156d98dfb5f30d0b26e0dc7ee93518d9bada', 'davidalejandropegaso@gmail.com', 'Asistente', NULL, NULL, 0, 1, 'assets/img/avatars/1.png'),
(3, 'prueba1', '09321765', 'pbkdf2:sha256:600000$MLVBG6gIQHOhds5b$206e5507217733b5cd32f778b54b56fa95ce47f9aab8f0ea48257e3fde959562', 'prueba@gmail.com', 'Administrador', NULL, NULL, 0, 1, 'assets/img/avatars/1.png'),
(4, 'Lenny Reyes', '10841560', 'pbkdf2:sha256:600000$A9tsjRGrOtg7MytU$364943a4dcd71d7093110fe2dc1701c31b56978791f4ad5030247e046ce5a25d', 'reyeslennyf72@gmail.com', 'Recepcionista', NULL, NULL, 0, 1, 'assets/img/avatars/1.png'),
(5, 'Frangher Pereira', '30553759', 'pbkdf2:sha256:600000$9RdO5FjhNZDoOLuo$de664dbbbba289ba9504edab378fbd6eca14c1b1cb982e5ce8284e18920365f7', 'frangher200@gmail.com', 'Gerente', NULL, NULL, 0, 1, 'assets/img/avatars/1.png');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `administracion_respaldos`
--
ALTER TABLE `administracion_respaldos`
  ADD PRIMARY KEY (`id_respaldo`,`usuarios_id_usuarios`),
  ADD KEY `fk_administracion_respaldos_usuarios_idx` (`usuarios_id_usuarios`);

--
-- Indices de la tabla `bitacora`
--
ALTER TABLE `bitacora`
  ADD PRIMARY KEY (`id_bitacora`,`usuarios_id_usuarios`),
  ADD KEY `fk_bitacora_usuarios1_idx` (`usuarios_id_usuarios`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuarios`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuarios` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
