-- phpMyAdmin SQL Dump
-- version 5.2.2deb1+deb13u1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 08-07-2026 a las 07:46:29
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
-- Base de datos: `invilara_seguridad`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `administracion_respaldos`
--

CREATE TABLE `administracion_respaldos` (
  `id_respaldo` int(11) NOT NULL,
  `fecha_respaldo` datetime NOT NULL,
  `tamaño_respaldo` decimal(4,2) NOT NULL,
  `usuarios_id_usuarios` int(11) NOT NULL,
  `estado` tinyint(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Tabla de administracion de respaldos.';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bitacora`
--

CREATE TABLE `bitacora` (
  `id_bitacora` int(11) NOT NULL,
  `usuario` varchar(15) NOT NULL,
  `id_modulo` int(11) NOT NULL,
  `modulo` varchar(20) NOT NULL,
  `accion` varchar(45) NOT NULL,
  `fecha` datetime NOT NULL,
  `hora_inicio_sesion` datetime NOT NULL,
  `hora_cierre_sesion` datetime NOT NULL,
  `usuarios_id_usuarios` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Tabla de la bitacora del sistema.';

--
-- Volcado de datos para la tabla `bitacora`
--

INSERT INTO `bitacora` (`id_bitacora`, `usuario`, `id_modulo`, `modulo`, `accion`, `fecha`, `hora_inicio_sesion`, `hora_cierre_sesion`, `usuarios_id_usuarios`) VALUES
(1, 'Frangher', 0, 'Solicitudes', 'CREAR', '2026-06-25 22:16:54', '2026-06-25 22:16:54', '2026-06-25 22:16:54', 1),
(2, 'Frangher', 0, 'Solicitudes', 'ELIMINAR', '2026-06-25 22:18:03', '2026-06-25 22:18:03', '2026-06-25 22:18:03', 1),
(3, 'Frangher', 0, 'Proyectos', 'VER', '2026-06-25 22:19:25', '2026-06-25 22:19:25', '2026-06-25 22:19:25', 1),
(4, 'Frangher', 0, 'Proyectos', 'EDITAR', '2026-06-25 22:19:48', '2026-06-25 22:19:48', '2026-06-25 22:19:48', 1),
(5, 'Frangher', 0, 'Proyectos', 'VER', '2026-06-25 22:19:48', '2026-06-25 22:19:48', '2026-06-25 22:19:48', 1),
(6, 'Frangher', 0, 'Proyectos', 'CREAR', '2026-06-25 22:20:44', '2026-06-25 22:20:44', '2026-06-25 22:20:44', 1),
(7, 'Frangher', 0, 'Proyectos', 'VER', '2026-06-25 22:20:45', '2026-06-25 22:20:45', '2026-06-25 22:20:45', 1),
(8, 'Frangher', 0, 'Contrataciones', 'EDITAR', '2026-06-25 22:33:01', '2026-06-25 22:33:01', '2026-06-25 22:33:01', 1),
(9, 'Frangher', 0, 'Empresas', 'EDITAR', '2026-06-25 22:40:13', '2026-06-25 22:40:13', '2026-06-25 22:40:13', 1),
(10, 'Frangher', 0, 'Login', 'LOGIN', '2026-06-30 19:14:16', '2026-06-30 19:14:16', '2026-06-30 19:14:16', 1),
(11, 'Frangher', 0, 'Empresas', 'CREAR', '2026-06-30 19:15:20', '2026-06-30 19:15:20', '2026-06-30 19:15:20', 1),
(12, 'Frangher', 0, 'Contrataciones', 'CREAR', '2026-06-30 19:17:37', '2026-06-30 19:17:37', '2026-06-30 19:17:37', 1),
(13, 'Frangher', 0, 'Proyectos', 'VER', '2026-06-30 19:19:43', '2026-06-30 19:19:43', '2026-06-30 19:19:43', 1),
(14, 'Frangher', 0, 'Contrataciones', 'EDITAR', '2026-06-30 19:38:17', '2026-06-30 19:38:17', '2026-06-30 19:38:17', 1),
(15, 'Frangher', 0, 'Contrataciones', 'CREAR', '2026-06-30 20:14:20', '2026-06-30 20:14:20', '2026-06-30 20:14:20', 1),
(16, 'Frangher', 0, 'Contrataciones', 'ELIMINAR', '2026-06-30 20:15:43', '2026-06-30 20:15:43', '2026-06-30 20:15:43', 1),
(17, 'Frangher', 0, 'Contrataciones', 'EDITAR', '2026-06-30 20:16:36', '2026-06-30 20:16:36', '2026-06-30 20:16:36', 1),
(18, 'Frangher', 0, 'Login', 'LOGIN', '2026-07-01 22:47:54', '2026-07-01 22:47:54', '2026-07-01 22:47:54', 1),
(19, 'Frangher', 0, 'Proyectos', 'VER', '2026-07-01 22:48:02', '2026-07-01 22:48:02', '2026-07-01 22:48:02', 1),
(20, 'Frangher', 0, 'Proyectos', 'VER', '2026-07-01 22:49:21', '2026-07-01 22:49:21', '2026-07-01 22:49:21', 1),
(21, 'Frangher', 0, 'Informes de Avance', 'VER', '2026-07-01 22:52:06', '2026-07-01 22:52:06', '2026-07-01 22:52:06', 1),
(22, 'Frangher', 0, 'Informes de Avance', 'VER', '2026-07-01 22:54:23', '2026-07-01 22:54:23', '2026-07-01 22:54:23', 1),
(23, 'Frangher', 0, 'Informes de Avance', 'VER', '2026-07-01 22:54:32', '2026-07-01 22:54:32', '2026-07-01 22:54:32', 1),
(24, 'Frangher', 0, 'Informes de Avance', 'VER', '2026-07-01 22:54:51', '2026-07-01 22:54:51', '2026-07-01 22:54:51', 1),
(25, 'Frangher', 0, 'Empresas', 'ELIMINAR', '2026-07-01 22:56:50', '2026-07-01 22:56:50', '2026-07-01 22:56:50', 1),
(26, 'Frangher', 0, 'Contrataciones', 'EDITAR', '2026-07-01 23:35:44', '2026-07-01 23:35:44', '2026-07-01 23:35:44', 1),
(27, 'Frangher', 0, 'Empresas', 'CREAR', '2026-07-02 00:33:23', '2026-07-02 00:33:23', '2026-07-02 00:33:23', 1),
(28, 'Frangher', 0, 'Empresas', 'EDITAR', '2026-07-02 00:33:38', '2026-07-02 00:33:38', '2026-07-02 00:33:38', 1),
(29, 'Frangher', 0, 'Proyectos', 'VER', '2026-07-02 00:33:53', '2026-07-02 00:33:53', '2026-07-02 00:33:53', 1),
(30, 'Frangher', 0, 'Empresas', 'CREAR', '2026-07-02 03:11:50', '2026-07-02 03:11:50', '2026-07-02 03:11:50', 1),
(31, 'Frangher', 0, 'Empresas', 'ELIMINAR', '2026-07-02 03:12:40', '2026-07-02 03:12:40', '2026-07-02 03:12:40', 1),
(32, 'Frangher', 0, 'Empresas', 'EDITAR', '2026-07-02 03:12:56', '2026-07-02 03:12:56', '2026-07-02 03:12:56', 1),
(33, 'Frangher', 0, 'Login', 'LOGIN', '2026-07-02 23:06:24', '2026-07-02 23:06:24', '2026-07-02 23:06:24', 1),
(34, 'Frangher', 0, 'Informes de Avance', 'VER', '2026-07-02 23:09:56', '2026-07-02 23:09:56', '2026-07-02 23:09:56', 1),
(35, 'Frangher', 0, 'Informes de Avance', 'VER', '2026-07-02 23:10:00', '2026-07-02 23:10:00', '2026-07-02 23:10:00', 1),
(36, 'Frangher', 0, 'Informes de Avance', 'VER', '2026-07-02 23:10:22', '2026-07-02 23:10:22', '2026-07-02 23:10:22', 1),
(37, 'Frangher', 0, 'Informes de Avance', 'VER', '2026-07-02 23:14:40', '2026-07-02 23:14:40', '2026-07-02 23:14:40', 1),
(38, 'Frangher', 0, 'Proyectos', 'VER', '2026-07-02 23:14:46', '2026-07-02 23:14:46', '2026-07-02 23:14:46', 1),
(39, 'Frangher', 0, 'Login', 'LOGIN', '2026-07-06 17:50:10', '2026-07-06 17:50:10', '2026-07-06 17:50:10', 1),
(40, 'Frangher', 0, 'Solicitudes', 'ELIMINAR', '2026-07-06 19:02:12', '2026-07-06 19:02:12', '2026-07-06 19:02:12', 1),
(41, 'Frangher', 0, 'Empresas', 'ELIMINAR', '2026-07-06 19:41:28', '2026-07-06 19:41:28', '2026-07-06 19:41:28', 1),
(42, 'Frangher', 0, 'Empresas', 'ELIMINAR', '2026-07-06 19:41:35', '2026-07-06 19:41:35', '2026-07-06 19:41:35', 1),
(43, 'Frangher', 0, 'Empresas', 'ELIMINAR', '2026-07-06 19:41:38', '2026-07-06 19:41:38', '2026-07-06 19:41:38', 1),
(44, 'Frangher', 0, 'Empresas', 'ELIMINAR', '2026-07-06 19:41:42', '2026-07-06 19:41:42', '2026-07-06 19:41:42', 1),
(45, 'Frangher', 0, 'Empresas', 'CREAR', '2026-07-06 19:43:42', '2026-07-06 19:43:42', '2026-07-06 19:43:42', 1),
(46, 'Frangher', 0, 'Empresas', 'EDITAR', '2026-07-06 19:44:12', '2026-07-06 19:44:12', '2026-07-06 19:44:12', 1),
(47, 'Frangher', 0, 'Proyectos', 'VER', '2026-07-06 23:50:58', '2026-07-06 23:50:58', '2026-07-06 23:50:58', 1),
(48, 'Frangher', 0, 'Informes de Avance', 'VER', '2026-07-07 00:08:56', '2026-07-07 00:08:56', '2026-07-07 00:08:56', 1),
(49, 'Frangher', 0, 'Login', 'LOGIN', '2026-07-08 00:19:43', '2026-07-08 00:19:43', '2026-07-08 00:19:43', 1),
(50, 'Frangher', 0, 'Solicitudes', 'ELIMINAR', '2026-07-08 00:36:09', '2026-07-08 00:36:09', '2026-07-08 00:36:09', 1),
(51, 'Frangher', 0, 'Proyectos', 'VER', '2026-07-08 02:03:12', '2026-07-08 02:03:12', '2026-07-08 02:03:12', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuarios` int(11) NOT NULL,
  `nombre` varchar(25) NOT NULL,
  `cedula_usuario` varchar(10) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `correo` varchar(45) NOT NULL,
  `rol` varchar(20) NOT NULL COMMENT 'Tabla de los usuarios.',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 para activo, 0 para inactivo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Tabla de usuarios';

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuarios`, `nombre`, `cedula_usuario`, `contrasena`, `correo`, `rol`, `estado`) VALUES
(1, 'Frangher', '3221222', 'pbkdf2:sha256:600000$qBwul27GhcUkwqx5$473938e274ad52297935ba089dfc13cdc51f691b2515d9200f6f832b8d7e438b', 'frangher@gmail.com', 'Usuario', 1);

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
  ADD PRIMARY KEY (`id_usuarios`),
  ADD UNIQUE KEY `cedula_usuario_UNIQUE` (`cedula_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `administracion_respaldos`
--
ALTER TABLE `administracion_respaldos`
  MODIFY `id_respaldo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `bitacora`
--
ALTER TABLE `bitacora`
  MODIFY `id_bitacora` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=52;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuarios` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `administracion_respaldos`
--
ALTER TABLE `administracion_respaldos`
  ADD CONSTRAINT `fk_administracion_respaldos_usuarios` FOREIGN KEY (`usuarios_id_usuarios`) REFERENCES `usuarios` (`id_usuarios`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Filtros para la tabla `bitacora`
--
ALTER TABLE `bitacora`
  ADD CONSTRAINT `fk_bitacora_usuarios1` FOREIGN KEY (`usuarios_id_usuarios`) REFERENCES `usuarios` (`id_usuarios`) ON DELETE NO ACTION ON UPDATE NO ACTION;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
