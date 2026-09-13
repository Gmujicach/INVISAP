-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 13-09-2026 a las 02:02:09
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
  `tamaño_respaldo` decimal(10,2) NOT NULL,
  `usuarios_id_usuarios` int NOT NULL,
  `estado` tinyint(1) NOT NULL,
  `nombre_archivo` varchar(255) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `descripcion` varchar(255) COLLATE utf8mb4_general_ci DEFAULT ''
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

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `modulos`
--

CREATE TABLE `modulos` (
  `id_modulo` int NOT NULL,
  `nombre` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Clave corta del módulo (debe coincidir con tiene_permiso(''clave''))',
  `descripcion` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Descripción de lo que hace el módulo',
  `url` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'URL principal del módulo en el sidebar',
  `tipo` enum('CRUD','Transaccional','Enlace') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'CRUD' COMMENT 'CRUD o Transaccional (Enlace = manual/documentación)',
  `icono` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Clase del ícono del sidebar',
  `orden` int NOT NULL DEFAULT '0' COMMENT 'Orden de aparición en el menú',
  `estado` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1 activo, 0 inactivo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Catálogo de módulos del sistema (sidebar)';

--
-- Volcado de datos para la tabla `modulos`
--

INSERT INTO `modulos` (`id_modulo`, `nombre`, `descripcion`, `url`, `tipo`, `icono`, `orden`, `estado`) VALUES
(1, 'solicitudes', 'Registro y gestión de solicitudes ciudadanas.', '/lista-de-solicitudes', 'CRUD', 'bi-card-text', 1, 1),
(2, 'proyectos', 'Asignación de proyectos a partir de solicitudes aprobadas.', '/gestionar-proyectos', 'Transaccional', 'bi-folder', 2, 1),
(3, 'obras', 'Gestión de obras vinculadas a proyectos y contrataciones.', '/gestionar-obras', 'Transaccional', 'bi-house-gear', 3, 1),
(4, 'publicaciones', 'Publicación de avances e información de obras.', '/lista-publicaciones', 'Transaccional', 'bi-newspaper', 4, 1),
(5, 'contrataciones', 'Registro de contrataciones asociadas a obras.', '/contratacion', 'Transaccional', 'bi-briefcase', 5, 1),
(6, 'usuarios', 'Registro, edición y eliminación de usuarios del sistema.', '/users', 'CRUD', 'bi-people-fill', 6, 1),
(7, 'bitacora', 'Registro de auditoría de acciones de los usuarios.', '/bitacora', 'CRUD', 'bi-clock-history', 7, 1),
(8, 'evidencias', 'Registro y listado de evidencias fotográficas de obras.', '/evidencias/listar', 'CRUD', 'bi-images', 8, 1),
(9, 'informes', 'Informe de avance de obra (depende de obras y evidencias).', '/inf_avance_obra', 'Transaccional', 'bi-graph-up', 9, 1),
(10, 'reportes', 'Generación de reportes en Excel, PDF y estadísticos.', '/reportes', 'CRUD', 'bi-bar-chart-line-fill', 10, 1),
(11, 'gravedad', 'Catálogo de niveles de gravedad de las obras.', '/gestionar-gravedad', 'CRUD', 'bi-exclamation-triangle', 11, 1),
(12, 'prioridad', 'Catálogo de niveles de prioridad de las solicitudes.', '/gestionar-prioridad', 'CRUD', 'bi-arrow-up', 12, 1),
(13, 'empleados', 'Registro y listado de empleados de la institución.', '/empleados', 'CRUD', 'bi-person-badge-fill', 13, 1),
(14, 'empresas', 'Registro y listado de empresas contratistas.', '/lista-empresas', 'CRUD', 'bi-building', 14, 1),
(15, 'inspecciones', 'Registro y listado de inspecciones de obras.', '/inspecciones', 'CRUD', 'bi-clipboard-check', 15, 1),
(16, 'maquinaria', 'Registro y listado de maquinaria pesada.', '/maquinaria', 'CRUD', 'bi-truck', 16, 1),
(17, 'respaldos', 'Administración de respaldos de la base de datos.', '/administrar-respaldos', 'CRUD', 'bi-download', 17, 1),
(18, 'manual', 'Manual del sistema (documentación de usuario).', '/manual', 'Enlace', 'bi-journal-bookmark-fill', 18, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notificaciones`
--

CREATE TABLE `notificaciones` (
  `id_notificacion` int NOT NULL,
  `usuarios_id_usuarios` int NOT NULL DEFAULT '0',
  `modulo` varchar(30) NOT NULL DEFAULT 'General',
  `titulo` varchar(120) NOT NULL DEFAULT '',
  `mensaje` varchar(255) NOT NULL DEFAULT '',
  `enlace` varchar(255) DEFAULT NULL,
  `leida` tinyint(1) NOT NULL DEFAULT '0',
  `creado_por` varchar(60) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `creado_por_avatar` varchar(255) DEFAULT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id_rol` int NOT NULL,
  `nombre` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Nombre del rol (coincide con usuarios.rol)',
  `descripcion` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1 activo, 0 inactivo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Catálogo de roles/cargos';

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`id_rol`, `nombre`, `descripcion`, `estado`) VALUES
(1, 'Super Usuario', 'Control total del sistema.', 1),
(2, 'Administrador', 'Gestión operativa y de usuarios.', 1),
(3, 'Gerente', 'Supervisión de obras, informes y prioridades.', 1),
(4, 'Inspector', 'Inspección de obras y registro de evidencias.', 1),
(5, 'Recepcionista', 'Recepción de solicitudes y consulta de reportes.', 1),
(6, 'Asistente', 'Apoyo del departamento del ciuadadano.', 1),
(7, 'Proyectista', 'Diseño y seguimiento de proyectos y obras.', 1),
(8, 'Usuario', 'Acceso básico de consulta.', 1),
(9, 'Presidente', 'Visualización institucional de módulos clave.', 1),
(10, 'ciudadania', 'encargados de ayudar a los solicitantes', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles_permisos`
--

CREATE TABLE `roles_permisos` (
  `id_rol_permiso` int NOT NULL,
  `id_rol` int NOT NULL,
  `id_modulo` int NOT NULL,
  `puede_ver` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Puede visualizar/abrir el módulo',
  `puede_crear` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Puede registrar (CREAR)',
  `puede_editar` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Puede modificar (EDITAR)',
  `puede_eliminar` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Puede borrar (ELIMINAR)',
  `estado` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1 activo, 0 inactivo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Permisos específicos por rol y módulo';

--
-- Volcado de datos para la tabla `roles_permisos`
--

INSERT INTO `roles_permisos` (`id_rol_permiso`, `id_rol`, `id_modulo`, `puede_ver`, `puede_crear`, `puede_editar`, `puede_eliminar`, `estado`) VALUES
(1, 1, 1, 1, 1, 1, 1, 1),
(2, 1, 2, 1, 1, 1, 1, 1),
(3, 1, 3, 1, 1, 1, 1, 1),
(4, 1, 4, 1, 1, 1, 1, 1),
(5, 1, 5, 1, 1, 1, 1, 1),
(6, 1, 6, 1, 1, 1, 1, 1),
(7, 1, 7, 1, 0, 0, 0, 1),
(8, 1, 8, 1, 1, 1, 1, 1),
(9, 1, 9, 1, 1, 1, 1, 1),
(10, 1, 10, 1, 1, 1, 1, 1),
(11, 1, 11, 1, 1, 1, 1, 1),
(12, 1, 12, 1, 1, 1, 1, 1),
(13, 1, 13, 1, 1, 1, 1, 1),
(14, 1, 14, 1, 1, 1, 1, 1),
(15, 1, 15, 1, 1, 1, 1, 1),
(16, 1, 16, 1, 1, 1, 1, 1),
(17, 1, 17, 1, 1, 1, 1, 1),
(18, 1, 18, 1, 0, 0, 0, 1),
(19, 2, 6, 1, 1, 1, 1, 1),
(20, 2, 1, 1, 1, 1, 1, 1),
(21, 2, 13, 1, 1, 1, 1, 1),
(22, 2, 3, 1, 1, 1, 1, 1),
(23, 2, 2, 1, 1, 1, 1, 1),
(24, 2, 8, 1, 1, 1, 1, 1),
(25, 2, 4, 1, 1, 1, 1, 1),
(26, 2, 10, 1, 1, 1, 1, 1),
(27, 2, 7, 1, 0, 0, 0, 1),
(28, 2, 11, 1, 1, 1, 1, 1),
(29, 2, 12, 1, 1, 1, 1, 1),
(30, 2, 9, 1, 1, 1, 1, 1),
(31, 2, 18, 1, 0, 0, 0, 1),
(32, 3, 1, 1, 1, 1, 1, 1),
(33, 3, 3, 1, 1, 1, 1, 1),
(34, 3, 13, 1, 1, 1, 1, 1),
(35, 3, 10, 1, 1, 1, 1, 1),
(36, 3, 9, 1, 1, 1, 1, 1),
(37, 3, 11, 1, 1, 1, 1, 1),
(38, 3, 12, 1, 1, 1, 1, 1),
(39, 4, 1, 1, 1, 1, 1, 1),
(40, 4, 3, 1, 1, 1, 1, 1),
(41, 4, 15, 1, 1, 1, 1, 1),
(42, 4, 8, 1, 1, 1, 1, 1),
(43, 4, 9, 1, 1, 1, 1, 1),
(44, 5, 1, 1, 1, 1, 1, 1),
(45, 5, 10, 1, 1, 1, 1, 1),
(46, 5, 9, 1, 1, 1, 1, 1),
(47, 6, 1, 1, 1, 1, 1, 1),
(48, 7, 2, 1, 1, 1, 1, 1),
(49, 7, 3, 1, 1, 1, 1, 1),
(50, 7, 9, 1, 1, 1, 1, 1),
(51, 8, 1, 1, 1, 1, 1, 1),
(52, 8, 9, 1, 1, 1, 1, 1),
(53, 9, 1, 1, 1, 1, 1, 1),
(54, 9, 2, 1, 1, 1, 1, 1),
(55, 9, 3, 1, 1, 1, 1, 1),
(56, 9, 4, 1, 1, 1, 1, 1),
(57, 9, 5, 1, 1, 1, 1, 1),
(58, 9, 14, 1, 1, 1, 1, 1),
(59, 9, 13, 1, 1, 1, 1, 1),
(60, 9, 16, 1, 1, 1, 1, 1),
(61, 9, 8, 1, 1, 1, 1, 1),
(62, 9, 15, 1, 1, 1, 1, 1),
(63, 9, 10, 1, 1, 1, 1, 1),
(64, 9, 7, 1, 0, 0, 0, 1),
(65, 9, 11, 1, 1, 1, 1, 1),
(66, 9, 12, 1, 1, 1, 1, 1),
(67, 9, 9, 1, 1, 1, 1, 1),
(68, 9, 18, 1, 0, 0, 0, 1);

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
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'assets/img/avatars/1.png' COMMENT 'Foto de perfil del usuario'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Tabla de usuarios';

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuarios`, `nombre`, `cedula_usuario`, `contrasena`, `correo`, `rol`, `otp_code`, `otp_expiry`, `otp_attempts`, `estado`, `avatar`) VALUES
(1, 'admin', '12345678', 'pbkdf2:sha256:600000$55dFI8r0mPOkdiR2$a437b96290e42be3cc8c847fb37c088aafc6894dddc904465813a5e849da2e6d', 'admin@gmail.com', 'Super Usuario', NULL, NULL, 0, 1, 'assets/img/avatars/1.png'),
(2, 'David Peña', '30304373', 'pbkdf2:sha256:600000$hNB86qI4PJLFj5zI$a8db74876d9381392452fc144ee2156d98dfb5f30d0b26e0dc7ee93518d9bada', 'davidalejandropegaso@gmail.com', 'Asistente', NULL, NULL, 0, 1, 'assets/img/avatars/1.png'),
(3, 'prueba1', '09321765', 'pbkdf2:sha256:600000$MLVBG6gIQHOhds5b$206e5507217733b5cd32f778b54b56fa95ce47f9aab8f0ea48257e3fde959562', 'prueba@gmail.com', 'Administrador', NULL, NULL, 0, 1, 'assets/img/avatars/1.png'),
(4, 'Lenny Reyes', '10841560', 'pbkdf2:sha256:600000$A9tsjRGrOtg7MytU$364943a4dcd71d7093110fe2dc1701c31b56978791f4ad5030247e046ce5a25d', 'reyeslennyf72@gmail.com', 'Recepcionista', NULL, NULL, 0, 1, 'assets/img/avatars/40dddc18b6f748b781a4a943c6a12239.jpeg'),
(5, 'Frangher Pereira', '30553759', 'pbkdf2:sha256:600000$9RdO5FjhNZDoOLuo$de664dbbbba289ba9504edab378fbd6eca14c1b1cb982e5ce8284e18920365f7', 'frangher200@gmail.com', 'Gerente', NULL, NULL, 0, 1, 'assets/img/avatars/1.png'),
(6, 'prueba2', '3054125315', 'pbkdf2:sha256:600000$2giL7omaooLb7h6s$a24344c192f7dbce7b8fcdd1e938fefd141b7e59590c8520602b7d37491ab693', 'prueba2@gmail.com', 'Presidente', NULL, NULL, 0, 1, 'assets/img/avatars/1.png'),
(7, 'prueba3', '29464612', 'pbkdf2:sha256:600000$LjGwccCDdlkoWjgT$49f6ce4de45eb3e39b5f88bce4f720fa7108bd1e0b72149f421f07d733a5966d', 'prueba3@gmail.com', 'Usuario', NULL, NULL, 0, 1, 'assets/img/avatars/f0003ef9eff64e349ec9a8e67a2c640b.jpg');

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `v_permisos_rol`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `v_permisos_rol` (
`id_rol` int
,`rol` varchar(20)
,`id_modulo` int
,`modulo` varchar(40)
,`url` varchar(120)
,`tipo` enum('CRUD','Transaccional','Enlace')
,`icono` varchar(60)
,`orden` int
,`puede_ver` tinyint(1)
,`puede_crear` tinyint(1)
,`puede_editar` tinyint(1)
,`puede_eliminar` tinyint(1)
);

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
-- Indices de la tabla `modulos`
--
ALTER TABLE `modulos`
  ADD PRIMARY KEY (`id_modulo`),
  ADD UNIQUE KEY `uk_modulos_nombre` (`nombre`);

--
-- Indices de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD PRIMARY KEY (`id_notificacion`),
  ADD KEY `idx_notif_usuario` (`usuarios_id_usuarios`,`leida`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id_rol`),
  ADD UNIQUE KEY `uk_roles_nombre` (`nombre`);

--
-- Indices de la tabla `roles_permisos`
--
ALTER TABLE `roles_permisos`
  ADD PRIMARY KEY (`id_rol_permiso`),
  ADD UNIQUE KEY `uk_rol_modulo` (`id_rol`,`id_modulo`),
  ADD KEY `fk_roles_permisos_modulos_idx` (`id_modulo`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuarios`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `modulos`
--
ALTER TABLE `modulos`
  MODIFY `id_modulo` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  MODIFY `id_notificacion` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id_rol` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `roles_permisos`
--
ALTER TABLE `roles_permisos`
  MODIFY `id_rol_permiso` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=69;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuarios` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

-- --------------------------------------------------------

--
-- Estructura para la vista `v_permisos_rol`
--
DROP TABLE IF EXISTS `v_permisos_rol`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_permisos_rol`  AS SELECT `r`.`id_rol` AS `id_rol`, `r`.`nombre` AS `rol`, `m`.`id_modulo` AS `id_modulo`, `m`.`nombre` AS `modulo`, `m`.`url` AS `url`, `m`.`tipo` AS `tipo`, `m`.`icono` AS `icono`, `m`.`orden` AS `orden`, `rp`.`puede_ver` AS `puede_ver`, `rp`.`puede_crear` AS `puede_crear`, `rp`.`puede_editar` AS `puede_editar`, `rp`.`puede_eliminar` AS `puede_eliminar` FROM ((`roles` `r` join `roles_permisos` `rp` on((`rp`.`id_rol` = `r`.`id_rol`))) join `modulos` `m` on((`m`.`id_modulo` = `rp`.`id_modulo`))) WHERE ((`r`.`estado` = 1) AND (`rp`.`estado` = 1) AND (`m`.`estado` = 1)) ;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `roles_permisos`
--
ALTER TABLE `roles_permisos`
  ADD CONSTRAINT `fk_roles_permisos_modulos` FOREIGN KEY (`id_modulo`) REFERENCES `modulos` (`id_modulo`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_roles_permisos_roles` FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id_rol`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
