-- MySQL dump 10.13  Distrib 9.7.1, for Win64 (x86_64)
--
-- Host: localhost    Database: invilara
-- ------------------------------------------------------
-- Server version	9.7.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '4773c216-9e66-11f1-8782-c4346b70723b:1-3230';

--
-- Table structure for table `avance`
--

DROP TABLE IF EXISTS `avance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
  `estado` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_avance`),
  KEY `fk_avance_obra1_idx` (`obra_id_obra`,`obra_estado`,`obra_contratacion_id_contratacion`,`obra_gestionar_proyectos_codigo_proyecto`),
  KEY `fk_avance_empleado1_idx` (`gerente`),
  CONSTRAINT `fk_avance_empleado1` FOREIGN KEY (`gerente`) REFERENCES `empleados` (`id_empleados`),
  CONSTRAINT `fk_avance_obra1` FOREIGN KEY (`obra_id_obra`, `obra_estado`, `obra_contratacion_id_contratacion`, `obra_gestionar_proyectos_codigo_proyecto`) REFERENCES `obra` (`id_obra`, `estado`, `contratacion_id_contratacion`, `gestionar_proyectos_codigo_proyecto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `avance`
--

LOCK TABLES `avance` WRITE;
/*!40000 ALTER TABLE `avance` DISABLE KEYS */;
INSERT INTO `avance` VALUES ('c61bac2ca9c7',68,'Se observo que el lateral de la quebrada se mantiene estable aun cuando se le coloco el material aislante, la mezcla se adhirió a la pared de la falla y no cede a la inclinación.',6,'2026-09-17',26,3,7,'PRY-001',1),('d0436184a5a2',68,'Se observo que el lateral de la quebrada se m',6,'2026-09-17',26,3,7,'PRY-001',1);
/*!40000 ALTER TABLE `avance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalogo_cargos`
--

DROP TABLE IF EXISTS `catalogo_cargos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `catalogo_cargos` (
  `id_cargo` int NOT NULL AUTO_INCREMENT,
  `nombre_cargo` varchar(45) NOT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  `estado` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_cargo`),
  UNIQUE KEY `nombre_cargo_UNIQUE` (`nombre_cargo`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catálogo de cargos institucionales';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalogo_cargos`
--

LOCK TABLES `catalogo_cargos` WRITE;
/*!40000 ALTER TABLE `catalogo_cargos` DISABLE KEYS */;
INSERT INTO `catalogo_cargos` VALUES (1,'Gerente','Gerente de área o departamento',1),(2,'Inspector','Inspector de obras y proyectos',1),(3,'Asistente','Asistente administrativo',1),(4,'Proyectista','Responsable de diseño de proyectos',1),(5,'Recepcionista','Atención al público',1),(6,'Ingeniero','Ingeniero técnico',1);
/*!40000 ALTER TABLE `catalogo_cargos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comunidad`
--

DROP TABLE IF EXISTS `comunidad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comunidad` (
  `id_comunidad` int NOT NULL AUTO_INCREMENT,
  `nombre_comunidad` varchar(100) NOT NULL,
  `ambito` varchar(45) NOT NULL,
  `sector` varchar(45) NOT NULL,
  `persona_id_persona` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_comunidad`,`persona_id_persona`),
  KEY `fk_comunidad_persona1_idx` (`persona_id_persona`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comunidad`
--

LOCK TABLES `comunidad` WRITE;
/*!40000 ALTER TABLE `comunidad` DISABLE KEYS */;
INSERT INTO `comunidad` VALUES (1,'prueba02','prueba','pruuuu',2,1),(2,'carorita','cuji','la playa',4,1),(3,'hskHJS','ihjdsk','hjajda',5,1),(4,'Nuevo Horizonte','San Francisco','Oeste',6,1),(5,'Gato Negro','Rural','Rastrojitos',22,1),(6,'La mata','Urbano','acañada grande',23,1);
/*!40000 ALTER TABLE `comunidad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contratacion`
--

DROP TABLE IF EXISTS `contratacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contratacion` (
  `id_contratacion` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(255) NOT NULL,
  `empresa_ganadora` varchar(150) NOT NULL,
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
  `estado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id_contratacion`),
  UNIQUE KEY `numero_contrato_UNIQUE` (`numero_contrato`),
  KEY `fk_contratacion_empresa1_idx` (`empresa_rif`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de contrataciones';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contratacion`
--

LOCK TABLES `contratacion` WRITE;
/*!40000 ALTER TABLE `contratacion` DISABLE KEYS */;
INSERT INTO `contratacion` VALUES (1,'Suministro y aplicación de mezcla asfáltica en caliente tipo IV para plan de bacheo en Av. Ribereña.','Asfaltos y Construcciones de Occidente, C.A.','INV-045-2026','USD 350.000,00','2027-02-10 00:00:00','2027-02-16 00:00:00','Contrato de Obra','Contratación Directa','Ejecución de Obras','Ejecución prioritaria aprobada por la gobernación para solventar fallas de borde críticas','2026-09-16 00:00:00','J-295412360',1),(2,'Adquisición de emulsión asfáltica de rompimiento rápido para imprimación de bases viales','Asfaltos y Pavimentos de Venezuela, C.A','INV-078-2026','USD 185.400,00','2026-09-30 00:00:00','2026-10-16 00:00:00','Contrato de Bienes','Concurso Abierto','Suministro de Bienes','Materiales destinados al almacenamiento estratégico del parque','2026-09-14 00:00:00','J-408912345',1),(3,'Servicio de transporte de carga pesada para traslado de agregados pétreos hacia planta de asfalto','Autocarga Lara, C.A.','INV-102-3322','BS 1.250.000,00','2026-11-17 00:00:00','2026-12-14 00:00:00','Contrato de Servicio','Consulta de Precios','Prestación de Servicios','Movilización de áridos desde canteras locales para garantizar la continuidad operativa de producción','2026-08-16 00:00:00','J-296107165',1),(4,'Suministro de rollos de manto asfáltico y primer para rehabilitación de puentes y alcantarillas.','Distribuidora Edil de Occidente, C.A','INV-115','EUR 45.800,00','2027-01-08 00:00:00','2027-02-16 00:00:00','Contrato de Bienes','Concurso Cerrado','Suministro de Bienes','Insumos requeridos para impermeabilización de juntas estructurales en distribuidores viales del este','2026-08-05 00:00:00','J-304521897',1),(5,'Dotación de parchos asfálticos en frío y aditivos sellantes para atención de emergencias viales.','Impermeabilizadora y Distribuidora La Casa del Asfalto','INV-1342','USD 9.233,22','2026-10-22 00:00:00','2026-10-30 00:00:00','Contrato de Bienes','Contratación Directa','Suministro de Bienes','Compra directa para atender de manera inmediata socavaciones','2026-09-16 00:00:00','J-401234567',1),(6,'Fabricación y suministro de elementos metálicos estructurales para pasarelas y defensas viales.','Lamilara C.A','INV-159-2026','BS 4.100.000,00','2026-11-05 00:00:00','2026-11-30 00:00:00','Contrato de Obra','Concurso Abierto','Ejecución de Obras','Componentes metálicos destinados al reemplazo de defensas impactadas en la intercomunal Barquisimeto','2026-08-17 00:00:00','J-309876543',1),(7,'Se contratan los servicios de la empresa Construcciones Racelca para la remocion y sustitucion vial.','Construcciones Racelca','INV-OB-001','BS 4.562.716,00','2026-09-15 00:00:00','2026-09-18 00:00:00','Contrato de Obra','Concurso Abierto','Ejecución de Obras','Contrato sujeto a cambios','2026-09-16 00:00:00','J-74438453',1),(8,'Se contratan los servicios de la empresa Construcciones Racelca para la remocion y sustitucion vial.','Construcciones Racelca','INV-OB-003','BS 4.562.716,00','2026-09-15 00:00:00','2026-09-18 00:00:00','Contrato de Obra','Concurso Abierto','Ejecución de Obras','Contrato sujeto a cambios','2026-09-16 00:00:00','J-74438453',1);
/*!40000 ALTER TABLE `contratacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleados`
--

DROP TABLE IF EXISTS `empleados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleados` (
  `id_empleados` int NOT NULL AUTO_INCREMENT,
  `nombre_empleado` varchar(45) NOT NULL,
  `cargo` varchar(45) NOT NULL,
  `fecha_ingreso` date NOT NULL,
  `gerencia_asignada` varchar(45) NOT NULL,
  `persona_id_persona` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1' COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)',
  PRIMARY KEY (`id_empleados`),
  KEY `fk_empleados_persona1_idx` (`persona_id_persona`),
  KEY `idx_empleados_estado` (`estado`),
  KEY `idx_empleados_cargo` (`cargo`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleados`
--

LOCK TABLES `empleados` WRITE;
/*!40000 ALTER TABLE `empleados` DISABLE KEYS */;
INSERT INTO `empleados` VALUES (1,'Juan Carlos Perez Hernandez','Inspector','2026-06-20','Obras',7,1),(2,'Cesilia  del Carmen Suarez','Recepcionista','2026-06-20','Atención al Ciudadano',9,1),(3,'Maria del Carmen Suarez','Asistente','2026-06-20','Comunicaciones',9,1),(5,'Carlos Ramírez Inspector','Inspector','2026-06-22','Obras Públicas',1,1),(6,'Alejandro Mejia Bautista','Inspector','2026-06-08','Gerencia de Obras',12,1),(7,'Elena María Riera','Proyectista','2017-02-13','Gerencia de Proyectos',13,1),(8,'Javier Eduardo Páez','Proyectista','2021-11-14','Gerencia de Proyectos',14,1),(9,'Sofía Alexandra Guedez','Asistente','2023-08-17','Atencion al Ciudadano',15,1),(10,'José Gregorio Montes','Inspector','2026-07-01','Gerencias de Obras',12,1),(11,'María Antonieta Pérez Silva','Asistente','2026-07-29','Gerencia de Comunicaciones',19,1),(12,'Carlos Eduardo Gómez Linares','Ingeniero','2026-08-01','Gerencia de Tecnología',20,1);
/*!40000 ALTER TABLE `empleados` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_borrado_logico_empleados` BEFORE DELETE ON `empleados` FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000' 
    SET MESSAGE_TEXT = 'La eliminación física está prohibida. El sistema realizará un borrado lógico.';
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `empresa`
--

DROP TABLE IF EXISTS `empresa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empresa` (
  `rif` varchar(12) NOT NULL,
  `nombre_empresa` varchar(80) NOT NULL,
  `telefono` varchar(12) NOT NULL COMMENT 'Tabla de empresas.',
  `domicilio_fiscal` varchar(100) NOT NULL,
  `cumple_requisitos` tinyint(1) NOT NULL DEFAULT '0',
  `estado` tinyint(1) NOT NULL,
  PRIMARY KEY (`rif`),
  UNIQUE KEY `rif_UNIQUE` (`rif`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empresa`
--

LOCK TABLES `empresa` WRITE;
/*!40000 ALTER TABLE `empresa` DISABLE KEYS */;
INSERT INTO `empresa` VALUES ('J-295412360','Asfaltos y Construcciones de Occidente, C.A.','0416-2324567','Zona Industrial I, Calle 26 con Carrera 5, Barquisimeto, Estado Lara',1,0),('J-296107165','Autocarga Lara, C.A.','0424-4911001','Av. Vía Barquisimeto - Quíbor, Km. 17, Sector Buenos Aires, Barquisimeto',1,0),('J-304521897','Distribuidora Edil de Occidente, C.A','0414-5102563','Carrera 17 con Calle 60, Barquisimeto, Estado Lara.',1,1),('J-309876543','Lamilara C.A','0414-9552909','Calle 29 entre Carrera 4 y 5, Zona Industrial I, Barquisimeto, Estado Lara.',1,1),('J-401234567','Impermeabilizadora y Distribuidora La Casa del Asfalto','0412-4452579','19 esquina con Calle 35, Edificio Carache, Barquisimeto, Estado Lara.',1,1),('J-408912345','Asfaltos y Pavimentos de Venezuela, C.A','0414-2694112','Zona Industrial II, Calle 3 con Av. Antena, Barquisimeto, Estado Lara.',1,1),('J-74438453','Construcciones Racelca','0424-9831936','Prolongacion Av. Los Leones, Torre Bel, piso 9, Of. 2A',1,1);
/*!40000 ALTER TABLE `empresa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evidencia`
--

DROP TABLE IF EXISTS `evidencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evidencia` (
  `id_evidencia` int NOT NULL AUTO_INCREMENT,
  `fotos` varchar(255) NOT NULL,
  `url_archivos` varchar(255) NOT NULL,
  `fecha_registro` datetime NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1' COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)',
  `etapa` enum('antes','durante','despues') NOT NULL DEFAULT 'antes' COMMENT 'Etapa de la evidencia fotográfica',
  PRIMARY KEY (`id_evidencia`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidencia`
--

LOCK TABLES `evidencia` WRITE;
/*!40000 ALTER TABLE `evidencia` DISABLE KEYS */;
INSERT INTO `evidencia` VALUES (12,'WhatsApp Image 2026-06-23 at 11.53.09 AM (2).','uploads/evidencias/596546b1d461_WhatsApp_Image_2026-06-23_at_11_53_09_AM_2.jpg','2026-06-30 18:19:23',1,'antes'),(13,'WhatsApp Image 2026-06-23 at 11.53.08 AM (2).','uploads/evidencias/1f659ea9faeb_WhatsApp_Image_2026-06-23_at_11_53_08_AM_2.jpg','2026-06-30 18:19:23',1,'durante'),(14,'WhatsApp Image 2026-06-23 at 11.53.18 AM (1).','uploads/evidencias/58a2b979b634_WhatsApp_Image_2026-06-23_at_11_53_18_AM_1.jpg','2026-06-30 18:19:23',1,'despues'),(15,'WhatsApp Image 2026-06-18 at 2.44.38 PM (4).j','uploads/evidencias/5e75f66e31dd_WhatsApp_Image_2026-06-18_at_2_44_38_PM_4.jpg','2026-06-30 19:34:59',1,'durante'),(16,'WhatsApp Image 2026-06-18 at 2.44.38 PM.jpeg','uploads/evidencias/5aff3e056a00_WhatsApp_Image_2026-06-18_at_2_44_38_PM.jpg','2026-06-30 19:34:59',1,'durante'),(17,'WhatsApp Image 2026-06-23 at 11.53.16 AM (2).','uploads/evidencias/3ca6bdacc414_WhatsApp_Image_2026-06-23_at_11_53_16_AM_2.jpg','2026-06-30 19:34:59',1,'durante'),(18,'WhatsApp Image 2026-06-23 at 11.53.16 AM (3).','uploads/evidencias/60474e154639_WhatsApp_Image_2026-06-23_at_11_53_16_AM_3.jpg','2026-06-30 19:34:59',1,'durante'),(19,'WhatsApp Image 2026-06-23 at 11.53.09 AM (1).','uploads/evidencias/6d82d404846d_WhatsApp_Image_2026-06-23_at_11_53_09_AM_1.jpg','2026-07-02 12:39:56',1,'antes'),(20,'WhatsApp Image 2026-06-23 at 11.53.09 AM (3).','uploads/evidencias/58992d937a7b_WhatsApp_Image_2026-06-23_at_11_53_09_AM_3.jpg','2026-07-02 12:39:56',1,'antes'),(21,'WhatsApp Image 2026-06-23 at 11.53.09 AM.jpeg','uploads/evidencias/30890868dd1a_WhatsApp_Image_2026-06-23_at_11_53_09_AM.jpg','2026-07-02 12:39:56',1,'antes'),(22,'WhatsApp Image 2026-06-23 at 11.53.10 AM.jpeg','uploads/evidencias/6c30a9cf957a_WhatsApp_Image_2026-06-23_at_11_53_10_AM.jpg','2026-07-02 12:39:56',1,'antes'),(23,'WhatsApp Image 2026-06-23 at 11.53.10 AM (2).','uploads/evidencias/cdcc3fdbc656_WhatsApp_Image_2026-06-23_at_11_53_10_AM_2.jpg','2026-07-02 12:41:58',1,'despues'),(24,'WhatsApp Image 2026-06-23 at 11.53.12 AM.jpeg','uploads/evidencias/813a552771db_WhatsApp_Image_2026-06-23_at_11_53_12_AM.jpg','2026-07-02 12:41:58',1,'despues'),(25,'WhatsApp Image 2026-06-23 at 11.53.16 AM.jpeg','uploads/evidencias/e7ff13fd5448_WhatsApp_Image_2026-06-23_at_11_53_16_AM.jpg','2026-07-02 12:41:58',1,'despues'),(26,'WhatsApp Image 2026-06-23 at 11.53.18 AM.jpeg','uploads/evidencias/4f11bdb292bc_WhatsApp_Image_2026-06-23_at_11_53_18_AM.jpg','2026-07-02 12:41:58',1,'despues'),(27,'WhatsApp Image 2026-06-23 at 11.53.17 AM (1).','uploads/evidencias/7c33d9c267d2_WhatsApp_Image_2026-06-23_at_11_53_17_AM_1.jpg','2026-07-07 20:21:59',1,'antes'),(28,'WhatsApp Image 2026-06-23 at 11.53.18 AM (2).','uploads/evidencias/d9b8ae567bd1_WhatsApp_Image_2026-06-23_at_11_53_18_AM_2.jpg','2026-07-07 20:21:59',1,'durante'),(29,'WhatsApp Image 2026-06-23 at 11.53.18 AM.jpeg','uploads/evidencias/9b211391d781_WhatsApp_Image_2026-06-23_at_11_53_18_AM.jpg','2026-07-07 20:21:59',1,'despues'),(30,'WhatsApp Image 2026-06-23 at 11.53.19 AM.jpeg','uploads/evidencias/a77ab3b0c6ca_WhatsApp_Image_2026-06-23_at_11_53_19_AM.jpg','2026-07-07 20:21:59',1,'antes'),(31,'Captura de pantalla (12).png','uploads/evidencias/bb54c4aafede_Captura_de_pantalla_12.jpg','2026-09-17 13:37:49',1,'antes'),(32,'Captura de pantalla (13).png','uploads/evidencias/c3177b2a7674_Captura_de_pantalla_13.jpg','2026-09-17 13:37:49',1,'durante'),(33,'Captura de pantalla (14).png','uploads/evidencias/3473673dd86d_Captura_de_pantalla_14.jpg','2026-09-17 13:37:49',1,'despues');
/*!40000 ALTER TABLE `evidencia` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_limite_evidencias` BEFORE INSERT ON `evidencia` FOR EACH ROW BEGIN
    DECLARE total INT;
    SELECT COUNT(*) INTO total FROM evidencia WHERE estado = 1;
    IF total >= 50 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Límite de evidencias alcanzado (máximo 50).';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `gravedad_obra`
--

DROP TABLE IF EXISTS `gravedad_obra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gravedad_obra` (
  `id_gravedad` int NOT NULL AUTO_INCREMENT,
  `nivel_gravedad` varchar(20) NOT NULL,
  `criticidad` varchar(10) NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1' COMMENT '1=Activo, 0=Inactivo (Borrado Lógico)',
  PRIMARY KEY (`id_gravedad`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gravedad_obra`
--

LOCK TABLES `gravedad_obra` WRITE;
/*!40000 ALTER TABLE `gravedad_obra` DISABLE KEYS */;
INSERT INTO `gravedad_obra` VALUES (1,'baja','0.24',1),(2,'Media','0.52',1);
/*!40000 ALTER TABLE `gravedad_obra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gravedad_obra_has_prioridad`
--

DROP TABLE IF EXISTS `gravedad_obra_has_prioridad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gravedad_obra_has_prioridad` (
  `gravedad_obra_id_gravedad` int NOT NULL,
  `prioridad_id_gestion_prioridad` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`gravedad_obra_id_gravedad`,`prioridad_id_gestion_prioridad`),
  KEY `fk_gravedad_obra_has_prioridad_prioridad1_idx` (`prioridad_id_gestion_prioridad`),
  KEY `fk_gravedad_obra_has_prioridad_gravedad_obra1_idx` (`gravedad_obra_id_gravedad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gravedad_obra_has_prioridad`
--

LOCK TABLES `gravedad_obra_has_prioridad` WRITE;
/*!40000 ALTER TABLE `gravedad_obra_has_prioridad` DISABLE KEYS */;
/*!40000 ALTER TABLE `gravedad_obra_has_prioridad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `informe_avance_obra`
--

DROP TABLE IF EXISTS `informe_avance_obra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `informe_avance_obra` (
  `id_informe` int NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL,
  `estado` varchar(25) NOT NULL,
  `poblacion_beneficiada` varchar(45) NOT NULL DEFAULT 'No especificado',
  `tipo_informe` varchar(30) NOT NULL,
  `evidencia_antes` varchar(255) NOT NULL DEFAULT '',
  `evidencia_durante` varchar(255) NOT NULL DEFAULT '',
  `evidencia_despues` varchar(255) NOT NULL DEFAULT '',
  `avance_id_avance` varchar(45) NOT NULL,
  `estado_registro` tinyint NOT NULL DEFAULT '1' COMMENT '1=Activo, 0=Inactivo (borrado lógico)',
  PRIMARY KEY (`id_informe`),
  KEY `fk_informe_avance_obra_avance1_idx` (`avance_id_avance`),
  KEY `idx_informe_estado_registro` (`estado_registro`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de informes de avances de obras';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `informe_avance_obra`
--

LOCK TABLES `informe_avance_obra` WRITE;
/*!40000 ALTER TABLE `informe_avance_obra` DISABLE KEYS */;
INSERT INTO `informe_avance_obra` VALUES (1,'2026-06-30 21:13:31','Aprobado','Pueblo Nuevo Avenida 4 con Calle 5','Menor','12','15','','fef7ab9d0883',1),(2,'2026-06-30 22:12:15','En Ejecucion','Cabudares','Mayor','12','16','','b70e531c3f5f',1),(18,'2026-07-01 22:31:07','Culminado','Luis Hurtado','Ficha Inspeccion Tecnica','12','17','14','22a8d98cd659',1),(23,'2026-07-02 20:28:32','En Ejecucion','Comunidad Nuevo Horizonte en Iribarren','Avance Mensual','21','18','24','a09e4dfbbe8c',1),(25,'2026-07-03 00:12:09','En Ejecucion','Palavecino Av. Intercomunal, Conjunto Res','Menor','19','16','','ad20d3759114',1),(26,'2026-07-03 00:12:14','En Ejecucion','Palavecino Av. Intercomunal, Conjunto Res','Menor','19','16','','b07c92e0e7ff',1),(28,'2026-07-03 02:17:51','En Ejecucion','Iribarren Av. Venezuela, Urb. Fundalara','Mayor','','','','d9b6d8dfb228',1),(29,'2026-07-03 02:18:12','En Ejecucion','Cabudare Urb. La Rosaleda Calle 5 Casa 12','Menor','','','','c0ecec782081',1),(30,'2026-07-04 17:34:27','Aprobado','La Salle Avenida 4 con Calle 3','Mayor','19,20','17','','d159b72e9c16',1),(33,'2026-07-04 20:14:59','En Ejecucion','Urb. El Cují, Calle 3, Lote 14','Avance Mensual','21','18','','bf0e7abdad06',1),(34,'2026-07-04 21:13:37','En Ejecucion','Tamaca Urb. El Recreo, Calle Principal, Casa','Avance Mensual','19','16,17','','942e517e2048',1),(35,'2026-07-04 21:17:41','Aprobado','José Gregorio Bastidas Av. Intercomunal','Ficha Inspeccion Tecnica','19,21,22','15,16','','49143e692fde',1),(37,'2026-07-04 22:00:18','Aprobado','Juares Sector La Aguada, Calle Principal','Menor','19,20,21,22','15,17,16,18','','7317ea5dba7d',1),(38,'2026-07-04 22:00:40','Aprobado','Juares Sector La Aguada, Calle Principal','Menor','20,21,22','16,18','','80e3115d8f95',1),(39,'2026-07-04 23:02:06','Culminado','Urb. La Piedad, Manzana C, Casa 15','Ficha Inspeccion Tecnica','19,20,21,22,12','15,16,17,18,13','23,24,25,26,14','e862a33d0c7c',1),(40,'2026-07-04 23:07:05','Culminado','Urb. La Piedad, Manzana C, Casa 15','Ficha Inspeccion Tecnica','19,20,21,22,12','15,16,17,18,13','23,24,25,26,14','752f90f2b837',1),(41,'2026-07-04 23:36:56','En Ejecucion','Carretera Nacional, Caserío El Copey','Avance Mensual','','','','0780c1c2a553',1),(42,'2026-07-05 00:28:47','En Ejecucion','El Tocuyo Av. Rotaria, Sector La Montañita','Avance Mensual','20,21','16,15','','0c8eb3a83706',1),(43,'2026-07-05 01:00:13','Aprobado','para la Comunidad santa la Osa','Menor','20,21','18,13','23','ae8c50e964e9',1),(50,'2026-07-06 04:24:19','En Ejecucion','Urb. La Piedad, Manzana C, Casa 15','Ficha Inspeccion Tecnica','20','18,17','','7a4e67e5c2ce',1),(51,'2026-07-06 19:53:13','Culminado','Av. Rotaria, Sector La Montañita en Morán','Mayor','19,21,20','15,16,17','','b0d8247b2d01',1),(52,'2026-07-07 00:44:24','En Ejecucion','Sector La Aguada, Calle Principal 20 personas','Menor','19,12,22','','','c46ec2a9eb43',1),(53,'2026-07-07 20:04:11','En Ejecucion','La Salle por donde los edificios','Avance Mensual','19,20,21','18,13','','bc2a0329e738',1),(54,'2026-08-10 18:48:21','Aprobado','Comunidad la Salle, El Cuji','Ficha Inspeccion Tecnica','','16,15,28','','8c961919a946',1),(55,'2026-08-18 03:31:50','Culminado','Comunidad santa la Rosa','Avance Mensual','19,12,30','16','','9a6e2816e7f4',1),(56,'2026-08-18 03:31:51','Culminado','Comunidad santa la Rosa','Avance Mensual','19,12,30','16','','86e4fcc4dfbe',1),(57,'2026-09-17 12:08:39','En Ejecucion','Santa Elena','Mayor','','15','14','c61bac2ca9c7',1);
/*!40000 ALTER TABLE `informe_avance_obra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inspeccion`
--

DROP TABLE IF EXISTS `inspeccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inspeccion` (
  `id_inspeccion` int NOT NULL AUTO_INCREMENT,
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
  `estado` tinyint NOT NULL DEFAULT '1',
  `evidencias_adicionales` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id_inspeccion`,`evidencia_id_evidencia`),
  KEY `fk_inspeccion_obra1_idx` (`obra_id_obra1`,`obra_estado1`,`obra_contratacion_id_contratacion1`,`obra_gestionar_proyectos_codigo_proyecto1`),
  KEY `fk_inspeccion_evidencia1_idx` (`evidencia_id_evidencia`),
  KEY `fk_inspeccion_empleado1_idx` (`inspector`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inspeccion`
--

LOCK TABLES `inspeccion` WRITE;
/*!40000 ALTER TABLE `inspeccion` DISABLE KEYS */;
INSERT INTO `inspeccion` VALUES (1,6,'2026-09-17','Inicial','Se observo que la zona aledaña al sitio de la obra presenta irregularidades en cuanto a la estabilidad del suelo por eso recomendamos nivelar el suelo antes de proceder a la colocación de la capa asfáltica.',26,3,7,'PRY-001',26,3,7,'PRY-001',30,1,'');
/*!40000 ALTER TABLE `inspeccion` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_cambiar_estatus_solicitud` AFTER INSERT ON `inspeccion` FOR EACH ROW BEGIN
    -- 1. Sincronizar el estatus de la Solicitud a 'En Proceso'
    UPDATE `invilara`.`solicitudes`
    SET est_solicitud = 'En Proceso' -- Ajusta el nombre real de tu columna si difiere
    WHERE id_solicitudes IN (
        SELECT solicitudes_id_solicitudes
        FROM `invilara`.`proyecto_has_solicitudes`
        WHERE proyecto_codigo_proyecto = NEW.obra_gestionar_proyectos_codigo_proyecto
    ) AND estatus_solicitud = 'Pendiente';

    -- 2. Sincronizar el estatus del Proyecto asociado a 'En Proceso'
    UPDATE `invilara`.`proyecto`
    SET estatus_proyecto = 'En Proceso' 
    WHERE codigo_proyecto = NEW.obra_gestionar_proyectos_codigo_proyecto
      AND estatus_proyecto = 'Pendiente';

    -- 3. Sincronizar el estatus de la Obra asociada a 'En Proceso'
    UPDATE `invilara`.`obra_gestionar_proyectos`
    SET estatus_obra = 'En Proceso'
    WHERE codigo_proyecto = NEW.obra_gestionar_proyectos_codigo_proyecto
      AND estatus_obra = 'Pendiente';
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `institucion`
--

DROP TABLE IF EXISTS `institucion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `institucion` (
  `id_institucion` int NOT NULL AUTO_INCREMENT,
  `nombre_representante` varchar(45) NOT NULL,
  `razon_social` varchar(120) NOT NULL,
  `persona_id_persona` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_institucion`,`persona_id_persona`),
  KEY `fk_institucion_persona1_idx` (`persona_id_persona`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `institucion`
--

LOCK TABLES `institucion` WRITE;
/*!40000 ALTER TABLE `institucion` DISABLE KEYS */;
INSERT INTO `institucion` VALUES (2,'María Rodríguez','U.E.N. Lisandro Alvarado',16,1);
/*!40000 ALTER TABLE `institucion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maquinaria`
--

DROP TABLE IF EXISTS `maquinaria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `maquinaria` (
  `id_maquinaria` int NOT NULL AUTO_INCREMENT,
  `nombre_maquinaria` varchar(50) NOT NULL COMMENT 'Tabla de nombres de maquinarias',
  `tipo_maquinaria` varchar(45) NOT NULL,
  `estado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id_maquinaria`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maquinaria`
--

LOCK TABLES `maquinaria` WRITE;
/*!40000 ALTER TABLE `maquinaria` DISABLE KEYS */;
INSERT INTO `maquinaria` VALUES (1,'Excavadora CAT 320','Pesada',1),(2,'Retroexcavadora','Pesada',1),(3,'Motoniveladora','Pesada',1),(4,'Bulldozer (Topadora)','Pesada',1),(5,'Compactador Rodillo liso','Pesada',1),(6,'Pavimentadora (Terminadora de asfalto)','Pesada',1),(7,'Fresadora de pavimento','Pesada',1),(8,'Mototraílla (Scraper)','Pesada',1),(9,'Mini cargadora (tipo Bobcat)','Liviana',1),(10,'Placa vibratoria Wacker Neuson','Liviana',1),(11,'Pisón vibratorio (Canguro)','Liviana',1),(12,'Cortadora de pavimento (Suelo/Asfalto)','Liviana',1),(13,'Generador eléctrico','Liviana',1),(14,'Barredora mecánica','Liviana',1),(15,'Motosierra','Herramienta',1),(16,'Taladro percutor / Rotomartillo','Herramienta',1),(17,'Esmeriladora','Herramienta',1),(18,'Estación total Leica TS06','Herramienta',1),(19,'Palas','Herramienta',1),(20,'Picos','Herramienta',1),(21,'rastrillos','Herramienta',1),(22,'macetas','Herramienta',1),(23,'Camión volquete (Dúmper) Mack Granite','Vehículo',1),(24,'Camión cisterna','Vehículo',1),(25,'Camión hormigonera (Mixer)','Vehículo',1),(26,'Camión plataforma','Vehículo',0);
/*!40000 ALTER TABLE `maquinaria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `obra`
--

DROP TABLE IF EXISTS `obra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `obra` (
  `id_obra` int NOT NULL AUTO_INCREMENT,
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
  `activo` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_obra`,`estado`,`contratacion_id_contratacion`,`gestionar_proyectos_codigo_proyecto`),
  UNIQUE KEY `id_obra_UNIQUE` (`id_obra`),
  KEY `fk_obra_semaforo1_idx` (`estado`),
  KEY `fk_obra_contratacion1_idx` (`contratacion_id_contratacion`),
  KEY `fk_obra_gestionar_proyectos1_idx` (`gestionar_proyectos_codigo_proyecto`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de las inspecciones';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `obra`
--

LOCK TABLES `obra` WRITE;
/*!40000 ALTER TABLE `obra` DISABLE KEYS */;
INSERT INTO `obra` VALUES (25,'Obra de Cabudares','Carrera 7A con calles 6 y 5','3 meses','2026-06-02','2026-09-18','4 mts cuadrados','Valuaciones N°1 - Bs. 50.000','maquinas usadas por las empresas contratadas',4,'INV-OB-001',47,2,2,'WEY-001',1),(26,'REHABILITACION DEL DISTRIBUIDOR BELLAS ARTES','AV. RIBEREÑA','3 SEMANAS','2026-09-17','2026-10-07','500 ton asfalto','13.723.319,93','N/A',0,'INV-OB-006',27,3,7,'PRY-001',1);
/*!40000 ALTER TABLE `obra` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `actualizar_semaforo_obra` BEFORE UPDATE ON `obra` FOR EACH ROW BEGIN
    IF NEW.estado <> OLD.estado THEN
        BEGIN END;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `particular`
--

DROP TABLE IF EXISTS `particular`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `particular` (
  `id_particular` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `apellido` varchar(45) NOT NULL,
  `persona_id_persona` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_particular`,`persona_id_persona`),
  KEY `fk_particular_persona1_idx` (`persona_id_persona`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `particular`
--

LOCK TABLES `particular` WRITE;
/*!40000 ALTER TABLE `particular` DISABLE KEYS */;
INSERT INTO `particular` VALUES (1,'Gabriel','Mujica',1,1),(2,'Mariangel','Bokor',11,1),(3,'Guillermo','Torres',18,1),(4,'Susana','Torres',21,1);
/*!40000 ALTER TABLE `particular` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `persona`
--

DROP TABLE IF EXISTS `persona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `persona` (
  `id_persona` int NOT NULL AUTO_INCREMENT,
  `cedula_persona` bigint NOT NULL,
  `direccion` varchar(200) NOT NULL,
  `parroquia` varchar(45) NOT NULL,
  `municipio` varchar(45) NOT NULL,
  `telefono` tinytext NOT NULL,
  `correo` varchar(45) NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_persona`),
  UNIQUE KEY `cedula_persona_UNIQUE` (`cedula_persona`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `persona`
--

LOCK TABLES `persona` WRITE;
/*!40000 ALTER TABLE `persona` DISABLE KEYS */;
INSERT INTO `persona` VALUES (1,29957469,'CAlle 24 entre 32 y 33','Catedral','Iribarren','04128280586','gabrielenriquemch@gmail.com',1),(2,34567896,'prueba','Agua Viva','Palavecino','04245678568','fedegtq2@gmail.com',1),(3,56785729,'calle miami','Hilario Luna y Luna','Morán','04245678934','youtube@gmail.coom',1),(4,31258936,'cuji','Freitez','Crespo','04245087200','redfiury21@gmail.com',1),(5,30088284,'ihjdsk','Cabudare','Palavecino','04120587814','jose@gmail.com',1),(6,28433546,'San Francisco','Guerrera Ana Soto (Juan de Villegas)','Iribarren','04123582233','mafer25@gmail.com',1),(7,29345267,'Calle 52 con Carrera 24 y 25 ','Iribarren','Guerrera Ana Soto','04123456420','Juan45p@gmail.com',1),(9,7833562,'Carrera 24 entre Calles 36 y 37','Iribarren','Juan de Villegas','04248379835','Cesif67@gmail.com',1),(11,30587785,'Carrera 4 con Calle 5','Cabudare','Palavecino','04245319088','bokorMBmariposa@gmail.com',1),(12,8977634,'Av. Los Horcones con Av. La Salle.','Catedral','Iribarren','04125677474','MejiAlejandro443@gmail.com',1),(13,28542148,'Calle 9 entre Cra. 20 y 21, Casa N° 20-15','Concepción','Iribarren','04163347465','Elenaita22Ri@gmail.com',1),(14,29723582,'Urb. La Rosaleda, Calle 5, Casa 12','Cabudare','Palavecino','04125543568','ElJavivi@gmail.com',1),(15,29545867,'Av. Los Abogados, Res. El Parque, Torre A','Santa Rosa','Iribarren','04146564722','LaSofi23@gmail.com',1),(16,12345678,'Av. Principal, Sector Centro','Catedral','Iribarren','0251-2319786','contacto@l-alvarado.edu.ve',1),(17,25289197,'Calle Carabobo, Casa N° 34','Anzoátegui','Morán','04120896778','FranVier@gmail.com',1),(18,28342778,'Calle 5 con Carrera 6','Freitez','Crespo','04127766654','Guille@gmail.com',1),(19,28456734,'Urb. Sucre, Avenida 27 con calle 30, Casa #15','Catedral','Iribarren','04121234567','maria.perez@ejemplo.com',1),(20,22345678,'Urb. Valle Hondo, Calle 3, Quinta La Perla','Cabudare','Palavecino','04129876543','CarlosGomezIng@gmail.com',1),(21,29057934,'Calle 5 con carrera 6B','Cabudare','Palavecino','04128763478','Susanita@gmail.com',1),(22,17478142,'Rural','Morán','Morán','0424-5130057','danielacarrasco@gmail.com',1),(23,2225788,'Urbano','Aguedo Felipe Alvarado','Iribarren','0412-5569878','lamata@gmail.com',1);
/*!40000 ALTER TABLE `persona` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prioridad`
--

DROP TABLE IF EXISTS `prioridad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prioridad` (
  `id_gestion_prioridad` int NOT NULL AUTO_INCREMENT,
  `rango_prioridad` float NOT NULL,
  `tipo_obra` varchar(20) DEFAULT NULL COMMENT 'Obra Mayor | Obra Menor',
  `gravedad_sugerida` varchar(10) DEFAULT NULL COMMENT 'Alta | Baja',
  `origen` varchar(20) DEFAULT 'manual' COMMENT 'ia | heuristica | error | manual | pendiente',
  `fecha_asignacion` datetime NOT NULL,
  `responsable_ajuste` varchar(30) NOT NULL,
  `justificacion_cambio` varchar(150) NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_gestion_prioridad`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prioridad`
--

LOCK TABLES `prioridad` WRITE;
/*!40000 ALTER TABLE `prioridad` DISABLE KEYS */;
INSERT INTO `prioridad` VALUES (1,0.8,'Obra Menor','Baja','ia','2026-06-15 16:38:02','admin','IA: tipo_obra_valor=1, gravedad_valor=1, es_zona_agricola=1.',1),(2,0.7,'Obra Mayor','Baja','ia','2026-09-02 01:23:47','Test','Prueba',1),(3,0.7,'Obra Mayor','Baja','ia','2026-09-02 01:24:56','Test','No hay necesidad de intervención urgente en este caso, ya que el problema es un simple ',1),(4,0.65,'Obra Menor','Alta','ia','2026-09-02 01:25:42','admin','IA: tipo_obra_valor=1, gravedad_valor=3, es_zona_agricola=1.',1),(5,0.45,'Obra Menor','Alta','ia','2026-09-02 01:25:46','admin','IA: tipo_obra_valor=1, gravedad_valor=3, es_zona_agricola=1.',1),(6,0.45,'Obra Menor','Alta','ia','2026-09-02 01:25:50','admin','IA: tipo_obra_valor=1, gravedad_valor=3, es_zona_agricola=1.',1),(7,0.45,'Obra Menor','Alta','ia','2026-09-02 01:25:54','admin','IA: tipo_obra_valor=1, gravedad_valor=3, es_zona_agricola=1.',1),(8,0.65,'Obra Menor','Alta','ia','2026-09-02 01:25:59','admin','IA: tipo_obra_valor=1, gravedad_valor=3, es_zona_agricola=1.',1),(9,0.55,'Obra Menor','Alta','ia','2026-09-02 01:26:05','admin','IA: tipo_obra_valor=1, gravedad_valor=3, es_zona_agricola=1.',1),(10,0.65,'Obra Menor','Alta','ia','2026-09-02 01:26:09','admin','IA: tipo_obra_valor=1, gravedad_valor=3, es_zona_agricola=1.',1),(11,1,'Obra Menor','Baja','ia','2026-09-02 01:26:15','admin','IA: tipo_obra_valor=1, gravedad_valor=1, es_zona_agricola=1.',1),(12,0.45,'Obra Menor','Alta','ia','2026-10-03 18:14:44','admin','IA: tipo_obra_valor=1, gravedad_valor=3, es_zona_agricola=1.',1);
/*!40000 ALTER TABLE `prioridad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proyecto`
--

DROP TABLE IF EXISTS `proyecto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyecto` (
  `codigo_proyecto` varchar(15) NOT NULL,
  `fecha_planificacion` datetime NOT NULL,
  `descripcion_tecnica` text NOT NULL,
  `computos_metricos` text NOT NULL,
  `estimacion_costo` varchar(45) NOT NULL,
  `proyecto_has_empleado` int DEFAULT NULL,
  `estado` tinyint(1) NOT NULL,
  PRIMARY KEY (`codigo_proyecto`),
  UNIQUE KEY `codigo_proyecto_UNIQUE` (`codigo_proyecto`),
  KEY `fk_proyecto_empleado1_idx` (`proyecto_has_empleado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla de gestion de proyectos';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proyecto`
--

LOCK TABLES `proyecto` WRITE;
/*!40000 ALTER TABLE `proyecto` DISABLE KEYS */;
INSERT INTO `proyecto` VALUES ('HGF-7697','2026-09-30 13:51:47','conformacion de viashg','[{\"metrica\":\"m3\",\"opcion\":\"asfaltado\",\"costo\":\"6665566\"},{\"metrica\":\"m2\",\"opcion\":\"agua\",\"costo\":\"666666\"}]','BS 5.000,00',8,1),('PRY-001','2026-09-15 11:35:57','Se plantea la demolicion de miembros de concreto armado con equipo liviano (compresor) base de junta, para anclar la nueva junta a colocar. Para la rehabilitacion de la via se plantea la colocacion puntual de asfalto, asi como la remocion y sustitucion de la cubre junta deteriorada por el desgaste, la demarcacion con linea continua en pavimento con material reflectivo (pintura de trafico reflectiva aplicada en frio, ancho = 14 cm) y la colocacion de marcadores reflerctivos bidireccionales, tipo ojos de gato lo cual mejorara la visibilidad en la via.','[{\"metrica\":\"m3\",\"opcion\":\"TRANSPORTE EN CAMIONES, A DISTANCIAS MAYORES DE 200 M., DE CUALQUIER TIPO DE MATERIAL PROVENIENTE DE LA PREPARACION DEL SITIO (AGREGADO Y/0 BOTE); POR TERRENO PLANO EN CARRETERA PAVIMENTADA\",\"costo\":\"194.78\"},{\"metrica\":\"m2\",\"opcion\":\"RIEGO DE ADHERENCIA EMPLEANDO MATERIAL MATERIAL ASFALTICO TIPO RC-250, INCLUYENDO LOS MATERIALES\",\"costo\":\"33.94\"},{\"metrica\":\"m2\",\"opcion\":\"LIMPIEZA DE MALEZA Y VEGETACION BAJA CON ALTURA INFERIOR A 1.5 MT. (DESMALEZADORA)\",\"costo\":\"100\"},{\"metrica\":\"kg\",\"opcion\":\"COLOCACION DE MEZCLA ASFALTICA EN CALIENTE TIPO IV (PARA BACHEO HASTA 30 M2)\",\"costo\":\"11750\"}]','BS 4.562.716,00',8,1);
/*!40000 ALTER TABLE `proyecto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proyecto_has_maquinaria`
--

DROP TABLE IF EXISTS `proyecto_has_maquinaria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyecto_has_maquinaria` (
  `proyecto_codigo_proyecto` varchar(15) NOT NULL,
  `maquinaria_id_maquinaria` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`proyecto_codigo_proyecto`,`maquinaria_id_maquinaria`),
  KEY `fk_proyecto_has_maquinaria_maquinaria1_idx` (`maquinaria_id_maquinaria`),
  KEY `fk_proyecto_has_maquinaria_proyecto1_idx` (`proyecto_codigo_proyecto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proyecto_has_maquinaria`
--

LOCK TABLES `proyecto_has_maquinaria` WRITE;
/*!40000 ALTER TABLE `proyecto_has_maquinaria` DISABLE KEYS */;
INSERT INTO `proyecto_has_maquinaria` VALUES ('FRE-001',7,1),('HGF-7697',20,1),('HGF-7697',24,1),('PRY-001',16,1),('PRY-001',19,1),('PRY-001',20,1),('PRY-001',23,1),('PRY-001',25,1),('WEY-001',16,1);
/*!40000 ALTER TABLE `proyecto_has_maquinaria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proyecto_has_solicitudes`
--

DROP TABLE IF EXISTS `proyecto_has_solicitudes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyecto_has_solicitudes` (
  `proyecto_codigo_proyecto` varchar(15) NOT NULL,
  `solicitudes_id_solicitudes` int NOT NULL,
  `solicitudes_persona_id_persona` int NOT NULL,
  `solicitudes_prioridad_id_gestion_prioridad` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`proyecto_codigo_proyecto`,`solicitudes_id_solicitudes`,`solicitudes_persona_id_persona`,`solicitudes_prioridad_id_gestion_prioridad`),
  KEY `fk_proyecto_has_solicitudes_solicitudes1_idx` (`solicitudes_id_solicitudes`,`solicitudes_persona_id_persona`,`solicitudes_prioridad_id_gestion_prioridad`),
  KEY `fk_proyecto_has_solicitudes_proyecto1_idx` (`proyecto_codigo_proyecto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proyecto_has_solicitudes`
--

LOCK TABLES `proyecto_has_solicitudes` WRITE;
/*!40000 ALTER TABLE `proyecto_has_solicitudes` DISABLE KEYS */;
INSERT INTO `proyecto_has_solicitudes` VALUES ('FRE-001',7,6,1,1),('HGF-7697',3,4,6,1),('PRY-001',12,22,1,1),('WEY-001',8,11,1,1);
/*!40000 ALTER TABLE `proyecto_has_solicitudes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `publicacion`
--

DROP TABLE IF EXISTS `publicacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `publicacion` (
  `id_publicacion` int NOT NULL AUTO_INCREMENT,
  `titulo_publicacion` varchar(150) NOT NULL,
  `nombre_responsable` varchar(45) NOT NULL,
  `tipo_publicacion` varchar(15) NOT NULL,
  `fecha_publicacion` datetime NOT NULL COMMENT 'Tabla de gestion de publicaciones',
  `informe_avance_obra_id_informe` int NOT NULL,
  `cuerpo_publicacion` text,
  `estado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id_publicacion`),
  KEY `fk_publicacion_informe_avance_obra1_idx` (`informe_avance_obra_id_informe`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `publicacion`
--

LOCK TABLES `publicacion` WRITE;
/*!40000 ALTER TABLE `publicacion` DISABLE KEYS */;
INSERT INTO `publicacion` VALUES (1,'Cabudares esta en escaces de agua por varias semanas','Administrador','General','2026-07-07 00:55:59',2,'Gracias a las orientaciones del gobernador Cmdte. Luis Reyes Reyes, seguimos activos y avanzando con el despliegue estrategico para la reconstrucción y sustitución de las estructuras de alcantarillas en diferentes sectores de la parroquia Cabudare del municipio Palavecino, Estado Lara.',1),(2,'Trabajos concluidos en la Comunidad Santa Rosa','Dayana Azuaje','General','2026-09-17 10:49:58',56,'Desde el Instituto Vial del Estado Lara (INVILARA), seguimos trabajando incansablemente para garantizar la movilidad, seguridad y bienestar de nuestras comunidades.\r\n\r\nEn esta oportunidad, informamos la culminación exitosa de los trabajos de inspección, canalización y adecuación del terreno en el sector de la Comunidad Santa Rosa. Gracias al despliegue de maquinaria y nuestro equipo técnico, logramos transformar este espacio para el beneficio directo de las familias del sector.\r\n\r\n📍 Ubicación: Comunidad Santa Rosa, Lara.\r\n\r\n✅ Estado: Obra Culminada.\r\n\r\n¡Avanzamos a paso firme por una mejor vialidad para todos!',1);
/*!40000 ALTER TABLE `publicacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recurso_obra`
--

DROP TABLE IF EXISTS `recurso_obra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recurso_obra` (
  `id_recurso` int NOT NULL,
  `descripcion_material` varchar(45) NOT NULL,
  `cantidad_material` decimal(5,2) NOT NULL,
  `unidad_material` varchar(20) NOT NULL,
  `informe_avance_obra_id_informe` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_recurso`),
  KEY `fk_recurso_obra_informe_avance_obra1_idx` (`informe_avance_obra_id_informe`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recurso_obra`
--

LOCK TABLES `recurso_obra` WRITE;
/*!40000 ALTER TABLE `recurso_obra` DISABLE KEYS */;
/*!40000 ALTER TABLE `recurso_obra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reporte`
--

DROP TABLE IF EXISTS `reporte`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reporte` (
  `id_reporte` int NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL,
  `ubicacion` varchar(255) NOT NULL,
  `solicitudes_pendientes` int NOT NULL,
  `solicitudes_procesadas` int NOT NULL,
  `cantidad_total_solicitudes` int NOT NULL,
  `cantidad_comunidades_atendidas` int NOT NULL,
  `informe_avance_obra_id_informe` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_reporte`),
  KEY `fk_reporte_informe_avance_obra1_idx` (`informe_avance_obra_id_informe`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reporte`
--

LOCK TABLES `reporte` WRITE;
/*!40000 ALTER TABLE `reporte` DISABLE KEYS */;
/*!40000 ALTER TABLE `reporte` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `semaforo`
--

DROP TABLE IF EXISTS `semaforo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `semaforo` (
  `id_semaforo` int NOT NULL AUTO_INCREMENT,
  `estado` varchar(20) NOT NULL,
  `color` enum('VERDE','AMARILLO','ROJO') NOT NULL,
  `descripcion` varchar(50) NOT NULL,
  `estado_registro` tinyint(1) NOT NULL,
  PRIMARY KEY (`id_semaforo`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `semaforo`
--

LOCK TABLES `semaforo` WRITE;
/*!40000 ALTER TABLE `semaforo` DISABLE KEYS */;
INSERT INTO `semaforo` VALUES (1,'Por Culminar','VERDE','Por Culminar',1),(2,'En progreso','AMARILLO','En progreso',1),(3,'Paralizada','ROJO','Paralizada',1);
/*!40000 ALTER TABLE `semaforo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudes`
--

DROP TABLE IF EXISTS `solicitudes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudes` (
  `id_solicitudes` int NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL,
  `tipo_solicitud` varchar(45) NOT NULL,
  `estatus_solicitud` varchar(15) NOT NULL,
  `problematica` varchar(512) NOT NULL,
  `persona_id_persona` int NOT NULL,
  `prioridad_id_gestion_prioridad` int NOT NULL,
  `estado` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_solicitudes`,`persona_id_persona`,`prioridad_id_gestion_prioridad`),
  KEY `fk_solicitudes_persona1_idx` (`persona_id_persona`),
  KEY `fk_solicitudes_prioridad1_idx` (`prioridad_id_gestion_prioridad`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tabla general de las solicitudes';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudes`
--

LOCK TABLES `solicitudes` WRITE;
/*!40000 ALTER TABLE `solicitudes` DISABLE KEYS */;
INSERT INTO `solicitudes` VALUES (1,'2026-06-15 16:38:02','Particular','Pendiente','[Servicios Básicos (Agua, Luz, Gas)] no hay gaz de prueba mortadela',1,4,1),(2,'2026-06-15 16:40:32','Comunidad','Completada','[Salud y Asistencia Médica] En la comunidad necesitamos una jornada de vacunación',2,5,1),(3,'2026-06-15 16:46:00','Comunidad','En Proceso','[Servicios Básicos (Agua, Luz, Gas)] hueco en la avenida donde salen aguas negras',4,6,1),(7,'2026-06-16 17:58:23','Comunidad','En Proceso','[Infraestructura y Vialidad] Acondicionamiento vial',6,7,1),(8,'2026-06-24 16:04:42','Particular','En Proceso','[Servicios Básicos (Agua, Luz, Gas)] No hay agua y todos nos estamos derritiendo, porfis traigan aguita aaaaaaaaa',11,8,1),(9,'2026-07-05 22:32:39','Institucion','En Proceso','[Infraestructura y Vialidad] Reparación de bacheo profundo en el acceso principal de la institución por filtraciones.',16,9,1),(10,'2026-07-07 19:59:35','Particular','En Proceso','[Salud y Asistencia Médica] Se necesita una jornada de vacunacion',18,10,1),(11,'2026-08-17 00:55:59','Particular','Pendiente','[Servicios Básicos (Agua, Luz, Gas)] En la comunidad no hay agua',21,11,1),(12,'2026-09-15 15:09:27','Comunidad','En Proceso','[Otros] Se solicita la reconstruccion de alcantarilla en la entrada de la comunidad Gato Negro, la cual se encuentra en malas condiciones, ademas, parte de la misma se encuentra sobresaliendo de la via.',22,1,1),(13,'2026-10-03 18:14:44','Comunidad','Pendiente','[Educación y Deporte] registro de prueba',23,12,1);
/*!40000 ALTER TABLE `solicitudes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `vista_evidencia_informe`
--

DROP TABLE IF EXISTS `vista_evidencia_informe`;
/*!50001 DROP VIEW IF EXISTS `vista_evidencia_informe`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_evidencia_informe` AS SELECT 
 1 AS `id_evidencia`,
 1 AS `fotos`,
 1 AS `url_archivos`,
 1 AS `fecha_registro`,
 1 AS `etapa`,
 1 AS `estado`,
 1 AS `id_informe`,
 1 AS `fecha_informe`,
 1 AS `tipo_informe`,
 1 AS `estado_informe`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping events for database 'invilara'
--

--
-- Dumping routines for database 'invilara'
--

--
-- Final view structure for view `vista_evidencia_informe`
--

/*!50001 DROP VIEW IF EXISTS `vista_evidencia_informe`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_evidencia_informe` AS select `e`.`id_evidencia` AS `id_evidencia`,`e`.`fotos` AS `fotos`,`e`.`url_archivos` AS `url_archivos`,`e`.`fecha_registro` AS `fecha_registro`,`e`.`etapa` AS `etapa`,`e`.`estado` AS `estado`,`i`.`id_informe` AS `id_informe`,`i`.`fecha` AS `fecha_informe`,`i`.`tipo_informe` AS `tipo_informe`,`i`.`estado` AS `estado_informe` from (`evidencia` `e` left join `informe_avance_obra` `i` on((((`e`.`etapa` = 'antes') and (`i`.`evidencia_antes` like concat('%',`e`.`id_evidencia`,'%'))) or ((`e`.`etapa` = 'durante') and (`i`.`evidencia_durante` like concat('%',`e`.`id_evidencia`,'%'))) or ((`e`.`etapa` = 'despues') and (`i`.`evidencia_despues` like concat('%',`e`.`id_evidencia`,'%')))))) where (`e`.`estado` = 1) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-07 21:20:04
