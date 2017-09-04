CREATE DATABASE  IF NOT EXISTS `mediconnect` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `mediconnect`;
-- MySQL dump 10.13  Distrib 5.7.17, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: mediconnect
-- ------------------------------------------------------
-- Server version	5.7.19-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `disease`
--

DROP TABLE IF EXISTS `disease`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `disease` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `keyword` varchar(150) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disease`
--

LOCK TABLES `disease` WRITE;
/*!40000 ALTER TABLE `disease` DISABLE KEYS */;
INSERT INTO `disease` VALUES (1,'妇产科疾病','子宫，卵巢，阴道，输卵管，附件，盆腔，妊娠，月经，白带'),(2,'糖尿病&内分泌疾病','甲状腺，下丘脑，垂体，肾上腺，血糖，肥胖'),(3,'神经系统疾病&神经外科疾病','脊髓，头痛，脑，癫痫，帕金森，肌肉，瘫痪，痴呆'),(4,'消化疾病&普外科疾病（胃肠外科疾病）','肝，胆，胰，脾，阑尾，胃，食管，肠，肛门，十二指肠，小肠，结肠，直肠'),(5,'泌尿疾病','肾，膀胱，肾盂，输尿管，结石，睾丸，精索，前列腺，尿道'),(6,'老年疾病','血压，血糖，血脂，骨质疏松，尿失禁'),(7,'循环疾病&心脏外科疾病','心，瓣膜，血管，血栓，搭桥，支架，冠脉，心梗，心肌缺血'),(8,'肾脏疾病','肾，尿道，尿路，输尿管，尿毒症，肾小球'),(9,'呼吸疾病','肺，支气管，胸腔，哮喘，呼吸，胸膜'),(10,'耳鼻咽喉疾病','耳，鼻，咽喉，声带，嗓子，扁桃体'),(11,'整形','骨，颈椎，关节，隆胸，整形，再造'),(12,'肿瘤','癌，瘤，肉瘤，增生，肿块'),(13,'风湿疾病','狼疮，风湿，尿酸，肌痛，结节'),(14,'疾病康复（康复医学？）','中风，卒中，复健，运动'),(15,'精神疾病','焦虑，抑郁，精神，心境，应激，躁狂'),(16,'眼科疾病','眼，视，白内障，晶状体，角膜，眼睑，结膜，虹膜');
/*!40000 ALTER TABLE `disease` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-08-30 21:53:06
